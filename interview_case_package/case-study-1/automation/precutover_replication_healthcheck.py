#!/usr/bin/env python3
"""Pre-cutover replication health check for NetApp-to-FSx SnapMirror relationships.

This is interview-grade reference code. It is intentionally vendor-neutral in the API layer,
so you can adapt it to ONTAP REST endpoints or a NetApp SDK in the lab.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional

import requests

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "20"))
LAG_THRESHOLD_SECONDS = int(os.getenv("LAG_THRESHOLD_SECONDS", str(4 * 3600)))
WARNING_LAG_SECONDS = int(os.getenv("WARNING_LAG_SECONDS", str(2 * 3600)))
VERIFY_TLS = os.getenv("VERIFY_TLS", "true").lower() == "true"


@dataclass
class VolumeRecord:
    source_svm: str
    source_volume: str
    dest_svm: str
    dest_volume: str
    relationship_id: str


@dataclass
class HealthResult:
    source_svm: str
    source_volume: str
    dest_svm: str
    dest_volume: str
    relationship_id: str
    state: str
    healthy: bool
    lag_seconds: Optional[int]
    last_transfer_status: str
    last_transfer_time: Optional[str]
    rag_status: str
    reason: str


class OntapClient:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = VERIFY_TLS
        self.session.headers.update({"accept": "application/json"})

    def get_snapmirror(self, relationship_id: str) -> Dict:
        url = f"{self.base_url}/api/snapmirror/relationships/{relationship_id}"
        response = self.session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()


def parse_lag_seconds(raw: Optional[str]) -> Optional[int]:
    if not raw:
        return None
    try:
        days = hours = minutes = seconds = 0
        if "d" in raw:
            d, raw = raw.split("d", 1)
            days = int(d.strip())
        parts = [int(p) for p in raw.strip().split(":")]
        if len(parts) == 3:
            hours, minutes, seconds = parts
        elif len(parts) == 2:
            minutes, seconds = parts
        else:
            return None
        return days * 86400 + hours * 3600 + minutes * 60 + seconds
    except Exception:
        return None


def evaluate_rag(state: str, healthy: bool, lag_seconds: Optional[int], last_transfer_status: str) -> tuple[str, str]:
    if not healthy:
        return "RED", "Relationship is not healthy"
    if state.lower() not in {"snapmirrored", "in_sync", "sync", "mirrored"}:
        return "RED", f"Unexpected state: {state}"
    if last_transfer_status.lower() not in {"success", "ok", "completed"}:
        return "RED", f"Last transfer status is {last_transfer_status}"
    if lag_seconds is None:
        return "AMBER", "Lag could not be parsed"
    if lag_seconds > LAG_THRESHOLD_SECONDS:
        return "RED", f"Lag {lag_seconds}s exceeds threshold"
    if lag_seconds > WARNING_LAG_SECONDS:
        return "AMBER", f"Lag {lag_seconds}s nearing threshold"
    return "GREEN", "Healthy and within threshold"


def fetch_volume_health(client: OntapClient, record: VolumeRecord) -> HealthResult:
    try:
        payload = client.get_snapmirror(record.relationship_id)
        state = str(payload.get("state", "unknown"))
        healthy = bool(payload.get("healthy", False))
        lag_seconds = parse_lag_seconds(payload.get("lag_time")) if isinstance(payload.get("lag_time"), str) else payload.get("lag_time")
        last_transfer = payload.get("last_transfer", {}) or {}
        last_transfer_status = str(last_transfer.get("status", "unknown"))
        last_transfer_time = last_transfer.get("end_time")
        rag_status, reason = evaluate_rag(state, healthy, lag_seconds, last_transfer_status)
        return HealthResult(
            source_svm=record.source_svm,
            source_volume=record.source_volume,
            dest_svm=record.dest_svm,
            dest_volume=record.dest_volume,
            relationship_id=record.relationship_id,
            state=state,
            healthy=healthy,
            lag_seconds=lag_seconds,
            last_transfer_status=last_transfer_status,
            last_transfer_time=last_transfer_time,
            rag_status=rag_status,
            reason=reason,
        )
    except requests.RequestException as exc:
        return HealthResult(
            source_svm=record.source_svm,
            source_volume=record.source_volume,
            dest_svm=record.dest_svm,
            dest_volume=record.dest_volume,
            relationship_id=record.relationship_id,
            state="query_failed",
            healthy=False,
            lag_seconds=None,
            last_transfer_status="unknown",
            last_transfer_time=None,
            rag_status="RED",
            reason=f"API query failed: {exc}",
        )


def load_inventory(path: str) -> List[VolumeRecord]:
    records: List[VolumeRecord] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                VolumeRecord(
                    source_svm=row["source_svm"],
                    source_volume=row["source_volume"],
                    dest_svm=row["dest_svm"],
                    dest_volume=row["dest_volume"],
                    relationship_id=row["relationship_id"],
                )
            )
    return records


def write_results_csv(path: str, results: Iterable[HealthResult]) -> None:
    rows = [asdict(r) for r in results]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)


def compute_overall_decision(results: List[HealthResult]) -> str:
    return "NO-GO" if any(r.rag_status == "RED" for r in results) else "GO"


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: precutover_replication_healthcheck.py <inventory.csv> <output.csv>")
        return 2

    inventory_path = sys.argv[1]
    output_path = sys.argv[2]
    base_url = os.environ.get("ONTAP_BASE_URL", "https://ontap-mgmt.example.com")
    username = os.environ.get("ONTAP_USERNAME", "admin")
    password = os.environ.get("ONTAP_PASSWORD", "changeme")

    inventory = load_inventory(inventory_path)
    client = OntapClient(base_url, username, password)

    started = time.time()
    results: List[HealthResult] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(fetch_volume_health, client, record) for record in inventory]
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda x: (x.rag_status, x.source_svm, x.source_volume))
    write_results_csv(output_path, results)

    summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "checked": len(results),
        "green": sum(1 for r in results if r.rag_status == "GREEN"),
        "amber": sum(1 for r in results if r.rag_status == "AMBER"),
        "red": sum(1 for r in results if r.rag_status == "RED"),
        "overall_decision": compute_overall_decision(results),
        "elapsed_seconds": round(time.time() - started, 2),
    }
    print(json.dumps(summary, indent=2))
    return 0 if summary["overall_decision"] == "GO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
