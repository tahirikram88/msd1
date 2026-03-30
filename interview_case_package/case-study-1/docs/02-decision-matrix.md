# SnapMirror vs DataSync — Decision Matrix

## Summary decision
**Primary migration engine for active NAS data:** SnapMirror  
**Selective archive/offload tool:** AWS DataSync

## Tool comparison

| Decision area | SnapMirror | AWS DataSync | Verdict |
|---|---|---|---|
| Final cutover predictability | Excellent | Medium | SnapMirror wins |
| File-level include/exclude filters | Poor | Excellent | DataSync wins |
| NetApp-to-NetApp replication semantics | Excellent | N/A | SnapMirror wins |
| Preservation of ONTAP efficiencies and replication model | Excellent | Limited | SnapMirror wins |
| Namespace-aware archival diversion | Limited | Excellent | DataSync wins |
| Risk during 4-hour maintenance window | Low if pre-seeded | Medium to high at scale | SnapMirror wins |
| Ease of proving low-RPO final delta | High | Medium | SnapMirror wins |
| FinOps control over cold-only routing | Poor alone | High | DataSync wins |

## Architecture decision

### Use SnapMirror when
- target is **FSx for ONTAP**
- cutover must be **predictable and short**
- application owners want familiar NAS semantics
- rollback must be easy and fast

### Use DataSync when
- moving **cold archive data** out of primary NAS path
- filtering by age / path / share / business unit
- sending data to **S3** instead of ONTAP volumes
- producing auditable task reports for archive moves

## Network / bandwidth analysis

For rough planning, assuming decimal units:
- 400 TB = **3,200,000 Gb**
- 5 days = **432,000 seconds**

### Theoretical minimum line-rate transfer time
| Effective throughput | Approx. time for 400 TB |
|---|---:|
| 1 Gbps | ~37.0 days |
| 5 Gbps | ~7.4 days |
| 10 Gbps | ~3.7 days |
| 20 Gbps | ~1.85 days |
|

## Interpretation
- At **1 Gbps**, the baseline cannot finish in the prep window.
- At **5 Gbps**, you are too close to the limit once protocol overhead, retransmits, throttling, and business-hour contention are considered.
- At **10 Gbps+**, the baseline is feasible if seeding starts early and cold data is diverted.

## Practical recommendation
- Prefer **AWS Direct Connect** over VPN for throughput consistency and lower operational risk.
- Seed replication **before** the change window.
- Reduce the active mirrored estate by excluding archive data from the primary migration stream.
- Do not promise the panel that 400 TB can be cleanly moved in 5 days without stating the dependency on **available bandwidth**.

## Interview soundbite
> DataSync solves filtering. SnapMirror solves cutover. The design uses each where it is strongest instead of forcing one tool to solve both business mandates.
