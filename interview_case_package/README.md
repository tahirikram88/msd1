# Cloud & Storage Engineering Interview Package

This repository is a complete, README-driven interview package for the two case studies in the supplied prompt:

- **Case Study 1:** 400TB Hybrid Data Dilemma & FinOps Optimization
- **Case Study 2:** Automated S3 Lifecycle Enforcement

It is designed for a **screen-share walkthrough**, not just static reading.

## Repository layout

```text
.
├── README.md
├── assets/
├── case-study-1/
│   ├── diagrams/
│   ├── docs/
│   ├── automation/
│   └── scripts/
├── case-study-2/
│   ├── src/
│   ├── terraform/
│   └── tests/
└── lab/
    ├── sample-data/
    └── scripts/
```

## What to present

### Part 1 — Architecture & Migration Strategy (30 minutes)
Walk in this order:
1. `case-study-1/docs/01-executive-summary.md`
2. `case-study-1/diagrams/hybrid-migration-architecture.png`
3. `case-study-1/docs/02-decision-matrix.md`
4. `case-study-1/docs/03-finops-cost-model.md`
5. `case-study-1/docs/04-cutover-and-rollback-runbook.md`
6. `case-study-1/docs/05-data-integrity-strategy.md`
7. `case-study-1/automation/precutover_replication_healthcheck.py`
8. `case-study-1/docs/06-automation-logic.md`

### Part 2 — AWS Automation & IaC (15 minutes)
Walk in this order:
1. `case-study-2/src/main.py`
2. `case-study-2/terraform/main.tf`
3. `case-study-2/terraform/iam.tf`
4. `case-study-2/terraform/variables.tf`
5. `case-study-2/tests/test_policy_builder.py`
6. `case-study-2/README.md`

### Demo / Lab section
1. `lab/README.md`
2. `lab/scripts/bootstrap_demo.sh`
3. `case-study-1/scripts/demo_walkthrough.md`
4. `case-study-2/scripts/live_demo_script.md`

## Recommended interview narrative

### Your headline answer
> I am using a **hybrid migration pattern**: first classify data into hot, warm, and cold; **archive cold data directly to S3 Glacier Flexible Retrieval**, migrate hot and warm NAS workloads to **Amazon FSx for NetApp ONTAP**, and use **SnapMirror** for low-risk, near-zero-downtime cutover of the remaining active NAS volumes.

### Why this wins
- **FinOps mandate satisfied** because dead data avoids expensive primary SSD landing.
- **4-hour cutover mandate satisfied** because final delta replication uses SnapMirror, not a large file-walk copy tool.
- **Operational risk reduced** because cutover/rollback are volume-centric, scripted, and reversible.
- **Architecture is explainable** to both storage engineers and non-storage leaders.

## Key design choices

### Case Study 1
- **Warm data definition:** last access between 1 and 3 years.
- **Cold data definition:** no access for more than 3 years.
- **Hot/active data definition:** access within 1 year.
- **Cold data treatment:** archive outside FSx primary namespace where possible.
- **Migration engine:** **SnapMirror for active NAS datasets**, **DataSync for archive/offload workflows**.
- **Client cutover:** DNS aliasing + low TTL + mount validation + scripted rollback.

### Case Study 2
- **Runtime:** Python Lambda using boto3
- **Trigger:** EventBridge Scheduler / rule at **2:00 AM America/New_York**
- **Safety:** `DRY_RUN=true` supported
- **Scale:** pagination, retry-safe code paths, per-bucket exception handling
- **Least privilege:** narrow IAM policy for S3, CloudWatch, and Logs

## Assumptions used in cost illustrations
The numbers in the FinOps section are illustrative and intended for an interview decision model, not a production quote:
- 400 TB total source estate
- 60% cold, 20% warm, 20% hot
- Region-specific pricing will vary
- Retrieval, request, transfer, backup, and throughput costs are discussed separately from storage-only comparisons

## How to publish this as GitHub

```bash
cd interview_case_package
git init
git add .
git commit -m "Add complete interview package"
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```

## AI assistance note
This package was prepared with AI assistance for drafting and structure, but the architecture, reasoning, code organization, and walkthrough narrative are designed to be explained directly by the presenter.
