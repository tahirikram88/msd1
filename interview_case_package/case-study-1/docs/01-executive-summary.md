# Case Study 1 — Executive Summary

## Problem statement
We have **400 TB of unstructured NAS data across 300+ NetApp AFF volumes** that must move to AWS while meeting two goals that naturally conflict:

1. **Near-zero downtime cutover** inside a 4-hour window.
2. **Avoid paying premium FSx SSD rates** for cold data that has not been touched for 3+ years.

## Recommended architecture
Use a **split-path migration strategy** instead of a single-tool strategy.

### Path A — Active NAS estate
- Migrate **hot + warm** NAS data to **Amazon FSx for NetApp ONTAP**.
- Use **NetApp SnapMirror** for baseline seeding and short final delta sync.
- Keep protocol fidelity for NFS/SMB workloads.
- Preserve storage semantics and reduce cutover risk.

### Path B — Archive estate
- Identify **cold data (>3 years untouched)** before final migration.
- Move it to **Amazon S3**, then transition to **S3 Glacier Flexible Retrieval**.
- Do **not** land archive data on FSx SSD first unless there is a temporary operational reason.

## Why not choose only one tool?

### Why not only DataSync?
DataSync is good for file-aware copy and filtering, but relying on it alone for the **final 4-hour cutover of 300 volumes** introduces too much uncertainty because it is still doing namespace scans, file comparisons, and task-level orchestration at file granularity.

### Why not only SnapMirror?
SnapMirror is the right answer for **predictable cutover**, but it mirrors the dataset as-is. If we mirror everything blindly, we violate the FinOps mandate by carrying years of cold data into expensive landing tiers.

## Final verdict
Use **DataSync selectively for archive diversion** and **SnapMirror for active volume replication and cutover**.

That gives the business:
- **FinOps control** for cold data
- **fast and predictable cutover** for active volumes
- **credible rollback** because the source remains authoritative until final commit

## Data classification model

| Tier | Definition | Destination | Why |
|---|---|---|---|
| Hot | Accessed within 12 months | FSx ONTAP SSD | Lowest latency, active engineering workloads |
| Warm | Accessed between 1 and 3 years | FSx ONTAP capacity pool tier | Lower cost, still file-system visible |
| Cold | Not accessed for >3 years | S3 + Glacier Flexible Retrieval lifecycle | Lowest-cost archive path |

## Scan strategy
Do **not** recursively walk 400 TB from production clients during peak hours.
Instead:
- use **snapshot-based metadata scans**
- run scanning from a **Linux jump host / scan VM**
- parallelize by volume with a bounded worker pool
- read **file metadata only**, not file content
- export a stakeholder CSV with cold %, warm %, hot %, recommendation, and migration path

## Cutover principle
The final change window is small, so the architecture is designed such that the cutover is only:
- stop writes
- trigger final SnapMirror update
- validate destination health
- switch client endpoints / DNS aliases / mount targets
- monitor application reopen success

That is much safer than trying to do last-minute data movement inside the maintenance window.
