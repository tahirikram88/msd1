# Case Study 2 — Automated S3 Lifecycle Enforcement

## Objective
Run every night, inspect all S3 buckets, and apply a standard lifecycle policy to large buckets that do not already have one unless they are explicitly exempt.

## Business rule
Apply remediation only when all are true:
- bucket has **no active lifecycle policy**
- `BucketSizeBytes` indicates size **> 100 GB**
- bucket tag `lifecycle-exempt=true` is **not** present
- `DRY_RUN` is **false**

## Lifecycle policy applied
- Transition to **STANDARD_IA** after 30 days
- Transition to **GLACIER** (Glacier Flexible Retrieval) after 180 days

## Safety controls
- `DRY_RUN=true` logs intent without mutating buckets
- missing CloudWatch metric data is a warning and skip
- per-bucket exception handling prevents one bad bucket from failing the whole run
- pagination is supported

## Deploy
```bash
cd terraform
terraform init
terraform plan -var="lambda_zip_path=../build/lifecycle_enforcer.zip"
terraform apply -var="lambda_zip_path=../build/lifecycle_enforcer.zip"
```

## Test locally
```bash
cd ..
python3 -m pytest -q
```
