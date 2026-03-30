# Data Integrity Strategy

## Problem
You cannot afford a full 400 TB reread just to prove integrity after migration.

## Strategy
Use a **layered validation approach** instead of a brute-force full scan.

## Layer 1 — Replication evidence
For SnapMirror volumes, capture:
- relationship health
- last transfer success
- lag time
- snapshot transfer status
- bytes transferred / common snapshot lineage where available

This provides a storage-native proof of replication health.

## Layer 2 — Metadata parity checks
For each migrated volume / share, compare:
- file count
- directory count
- total bytes
- sampled recent-write paths
- sampled large-file paths

## Layer 3 — Statistical sampling
Sample files by:
- size buckets
- path depth
- recent activity
- legacy cold corners
- file extension mix

Compute and compare hashes on a representative subset instead of the full dataset.

## Layer 4 — Business validation
Run application-level smoke tests with real users:
- open project directories
- compile from source tree
- read large model / media assets
- create, rename, and delete test files where allowed

## Layer 5 — Exception ledger
Every mismatch goes into a ledger with:
- source path
- destination path
- mismatch type
- severity
- owner
- disposition

## Why this is credible
The interview prompt asks how to validate without rereading 400 TB. This model answers that by combining:
- storage-native evidence
- metadata reconciliation
- targeted hash validation
- business-use confirmation

## Interview soundbite
> I validate in layers: replication health, metadata parity, statistical sampling, and business smoke tests. That gives high confidence without a full reread penalty.
