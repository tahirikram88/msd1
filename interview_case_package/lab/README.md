# Demo Lab Guide

This lab is a lightweight demo environment you can explain in an interview. It is not intended to reproduce a full 400 TB migration.

## Goal
Demonstrate:
- repository structure
- replication health precheck logic
- S3 lifecycle enforcement Lambda flow
- Terraform layout
- end-to-end walkthrough without needing a production NetApp estate

## Lab topology
- 1 Linux laptop or VM
- Python 3.11+
- AWS CLI configured to a sandbox account
- Optional mock ONTAP API using sample JSON

## Demo plan
1. Show the architecture PNG.
2. Open the decision matrix.
3. Run the replication health script against sample CSV inventory.
4. Open the S3 Lambda code.
5. Open Terraform.
6. Explain DRY_RUN and IAM least privilege.

## Suggested local setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r ../case-study-2/src/requirements.txt
```

## Mock precheck run
```bash
cd ../case-study-1/automation
python3 precutover_replication_healthcheck.py ../../lab/sample-data/replication_inventory.csv output.csv
```

## Mock Lambda unit test run
```bash
cd ../case-study-2
python3 -m pytest -q
```
