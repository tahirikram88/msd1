# 4-Hour Cutover and Rollback Runbook

## Cutover goal
Switch clients from on-prem NetApp AFF volumes to AWS FSx for ONTAP with near-zero downtime and a controlled rollback path.

## Pre-cutover prerequisites
- All target SVMs, volumes, exports, shares, and security styles pre-created
- SnapMirror relationships healthy across all in-scope volumes
- Final baseline transfer completed
- Volume lag within approved threshold
- Client endpoint mapping sheet signed off
- DNS aliases / CNAMEs prepared with **low TTL** ahead of cutover
- NFS export policies and SMB ACL tests completed
- AD/DNS reachability validated for SMB
- Monitoring dashboard open for source, destination, network, and application checks

## Go / No-Go criteria
Proceed only if all are true:
1. All critical volumes report **healthy SnapMirror state**.
2. Last successful transfer for all critical volumes is within agreed lag threshold.
3. Sample read validation on destination passes.
4. No unresolved identity / ACL / export mismatches.
5. Network path to FSx endpoints is healthy from all major client segments.
6. Application owners confirm write freeze is in place.
7. Rollback contacts and bridge call are active.

## Cutover steps

### T-60 minutes
- confirm CAB approval / bridge line / on-call roster
- recheck replication lag and source health
- notify users of write freeze start time

### T-15 minutes
- stop application writes
- disable scheduled jobs and batch processes
- confirm no active write-heavy sessions remain

### T-10 minutes
- run final SnapMirror update for all in-scope volumes
- wait for success state
- record last transfer timestamps

### T-5 minutes
- break / resync state only as required by operating model
- make destination volumes writable
- present destination NFS/SMB endpoints

### Cutover minute
- update DNS aliases / DFS namespace / mount targets
- remount pilot client group first
- validate opens, reads, writes, and metadata ops

### T+15 minutes
- expand to general client population
- monitor errors, stale handles, access denials, and latency

### T+30 to T+120 minutes
- application smoke tests
- user signoff
- performance watch

## DNS / client handling

### NFS
- reduce TTL in advance
- where possible use **logical mount aliases** instead of hard-coded IPs
- pre-stage mount definitions
- remount on pilot systems first

### SMB
- prefer namespace abstraction such as DFS where available
- prevalidate AD integration and SPNs if relevant
- test permissions with representative users before the window

## Rollback triggers
Call No-Go or rollback if any of these occur:
- replication final update fails on critical volumes
- widespread auth / ACL mismatch blocks production access
- destination write validation fails
- client mount failure rate crosses threshold
- application owner rejects smoke test
- performance degradation exceeds agreed threshold

## Rollback procedure
1. Halt new client onboarding to AWS target.
2. Re-enable source exports / shares as primary write targets.
3. Repoint DNS alias / namespace back to on-prem endpoints.
4. Force remount / reconnect for affected clients.
5. Confirm application writes succeed on source.
6. Preserve destination state for forensic review; do not destroy it.
7. Document exact failed criterion and recovery timestamp.

## Why rollback is credible
Because the source remains authoritative until cutover commit, rollback is mainly an **endpoint reversal exercise**, not a bulk data recovery operation.
