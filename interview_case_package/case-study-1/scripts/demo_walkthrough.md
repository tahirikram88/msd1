# Case Study 1 — Live Demo Script

## Opening
"I will show you the business problem first, then the architecture, then the tool decision, then the cutover playbook, and finally the automation that supports the Go/No-Go decision."

## Architecture section
"The key mistake would be to treat all 400 TB as equally valuable. My design classifies data into hot, warm, and cold. Hot data stays on FSx SSD, warm data is tiered to the FSx capacity pool, and cold data is archived to S3 Glacier Flexible Retrieval. That satisfies the FinOps mandate without putting the 4-hour cutover at risk."

## Migration engine section
"I am not choosing between SnapMirror and DataSync as if one must win completely. I use SnapMirror where predictability matters most: the final active volume cutover. I use DataSync where filtering matters most: cold-data diversion to S3."

## Bandwidth section
"At 1 Gbps the baseline is impossible in five days. At 10 Gbps it becomes feasible. So I would call out Direct Connect and pre-seeding as dependencies, not hide them."

## Cutover section
"During the maintenance window, I am not trying to move bulk data. I am only stopping writes, performing final delta sync, switching endpoints, validating, and keeping a clean rollback path."

## Automation section
"This script gives the bridge team a deterministic answer. Instead of reading 300 relationships manually, it produces a Green, Amber, Red view and an overall GO or NO-GO decision."

## Close
"So the design is technically credible, FinOps-aligned, and operationally safe."
