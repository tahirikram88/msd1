from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import boto3
from botocore.exceptions import ClientError

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

TZ_NAME = os.getenv("LOG_TIMEZONE", "America/New_York")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
SIZE_THRESHOLD_GB = float(os.getenv("SIZE_THRESHOLD_GB", "100"))
SIZE_THRESHOLD_BYTES = SIZE_THRESHOLD_GB * 1024 ** 3


@dataclass
class BucketDecision:
    bucket: str
    status: str
    reason: str


def tz_now() -> str:
    return datetime.now(ZoneInfo(TZ_NAME)).isoformat()


def build_lifecycle_policy() -> dict:
    return {
        "Rules": [
            {
                "ID": "standard-tiering-policy",
                "Status": "Enabled",
                "Filter": {"Prefix": ""},
                "Transitions": [
                    {"Days": 30, "StorageClass": "STANDARD_IA"},
                    {"Days": 180, "StorageClass": "GLACIER"},
                ],
            }
        ]
    }


def get_bucket_tags(s3_client, bucket_name: str) -> dict[str, str]:
    try:
        response = s3_client.get_bucket_tagging(Bucket=bucket_name)
        return {item["Key"]: item["Value"] for item in response.get("TagSet", [])}
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in {"NoSuchTagSet", "NoSuchBucket"}:
            return {}
        raise


def bucket_has_lifecycle(s3_client, bucket_name: str) -> bool:
    try:
        s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        return True
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code == "NoSuchLifecycleConfiguration":
            return False
        raise


def get_bucket_size_bytes(cloudwatch_client, bucket_name: str) -> int | None:
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=3)
    response = cloudwatch_client.get_metric_statistics(
        Namespace="AWS/S3",
        MetricName="BucketSizeBytes",
        Dimensions=[
            {"Name": "BucketName", "Value": bucket_name},
            {"Name": "StorageType", "Value": "StandardStorage"},
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,
        Statistics=["Average"],
    )
    datapoints = response.get("Datapoints", [])
    if not datapoints:
        return None
    latest = max(datapoints, key=lambda d: d["Timestamp"])
    return int(latest["Average"])


def apply_lifecycle_if_needed(s3_client, bucket_name: str) -> None:
    policy = build_lifecycle_policy()
    if DRY_RUN:
        LOGGER.info("%s DRY_RUN would apply lifecycle to bucket=%s policy=%s", tz_now(), bucket_name, json.dumps(policy))
        return
    s3_client.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration=policy,
    )
    LOGGER.info("%s Applied lifecycle policy to bucket=%s", tz_now(), bucket_name)


def inspect_bucket(s3_client, cloudwatch_client, bucket_name: str) -> BucketDecision:
    try:
        if bucket_has_lifecycle(s3_client, bucket_name):
            return BucketDecision(bucket_name, "SKIP", "Lifecycle policy already exists")

        tags = get_bucket_tags(s3_client, bucket_name)
        if tags.get("lifecycle-exempt", "").lower() == "true":
            return BucketDecision(bucket_name, "SKIP", "Exempt — No Action Taken")

        size_bytes = get_bucket_size_bytes(cloudwatch_client, bucket_name)
        if size_bytes is None:
            return BucketDecision(bucket_name, "WARN", "No CloudWatch BucketSizeBytes data returned")

        if size_bytes <= SIZE_THRESHOLD_BYTES:
            return BucketDecision(bucket_name, "SKIP", f"Bucket below threshold ({size_bytes} bytes)")

        apply_lifecycle_if_needed(s3_client, bucket_name)
        return BucketDecision(bucket_name, "REMEDIATE", f"Lifecycle applied or simulated for bucket > {SIZE_THRESHOLD_GB} GB")
    except ClientError as exc:
        LOGGER.exception("%s ClientError while processing bucket=%s", tz_now(), bucket_name)
        return BucketDecision(bucket_name, "ERROR", str(exc))
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("%s Unexpected error while processing bucket=%s", tz_now(), bucket_name)
        return BucketDecision(bucket_name, "ERROR", str(exc))


def list_all_buckets(s3_client) -> list[str]:
    response = s3_client.list_buckets()
    return [b["Name"] for b in response.get("Buckets", [])]


def lambda_handler(event, context):  # noqa: ANN001
    s3_client = boto3.client("s3")
    cloudwatch_client = boto3.client("cloudwatch")

    decisions = []
    for bucket_name in list_all_buckets(s3_client):
        decision = inspect_bucket(s3_client, cloudwatch_client, bucket_name)
        decisions.append(decision.__dict__)
        LOGGER.info("%s bucket=%s status=%s reason=%s", tz_now(), decision.bucket, decision.status, decision.reason)

    summary = {
        "timestamp": tz_now(),
        "dry_run": DRY_RUN,
        "inspected": len(decisions),
        "remediated": sum(1 for d in decisions if d["status"] == "REMEDIATE"),
        "skipped": sum(1 for d in decisions if d["status"] == "SKIP"),
        "warn": sum(1 for d in decisions if d["status"] == "WARN"),
        "errors": sum(1 for d in decisions if d["status"] == "ERROR"),
        "results": decisions,
    }
    LOGGER.info("%s run-summary=%s", tz_now(), json.dumps(summary))
    return summary
