# FinOps Summary — Storage Cost Model

## Objective
Compare a naive full lift-and-shift against a tiered destination strategy.

## Working assumptions
- Total source data: **400 TB**
- Hot: **20% = 80 TB**
- Warm: **20% = 80 TB**
- Cold: **60% = 240 TB**
- Illustrative comparison focuses on **storage** first, then notes other cost dimensions.

## Scenario A — Bad design: everything lands on FSx SSD

| Tier | Capacity | Unit price assumption | Monthly cost |
|---|---:|---:|---:|
| FSx ONTAP SSD | 400 TB | $0.04375/GB-month | ~$17,920 |

## Scenario B — Recommended tiered design

| Tier | Capacity | Destination | Unit price assumption | Monthly cost |
|---|---:|---|---:|---:|
| Hot | 80 TB | FSx ONTAP SSD | $0.04375/GB-month | ~$3,584 |
| Warm | 80 TB | FSx ONTAP capacity pool | $0.007665/GB-month | ~$628 |
| Cold | 240 TB | S3 Glacier Flexible Retrieval | $0.0036/GB-month | ~$885 |
| **Total** | **400 TB** |  |  | **~$5,097 / month** |

## Storage-only savings
- Full SSD landing: **~$17,920/month**
- Tiered target state: **~$5,097/month**
- **Estimated monthly reduction:** **~$12,823/month**
- **Estimated annual reduction:** **~$153,876/year**

## Important caveats to say out loud
This is not the whole bill. You should explicitly mention:
- FSx throughput capacity charges
- backup charges
- DataSync transfer charges where applicable
- S3 request / retrieval costs
- Direct Connect port / data transfer costs
- archive metadata overhead and retention minimums

## Why the panel should still like this model
Even with those extra charges, the **directional savings** are large enough that the architecture decision is still valid. The purpose of this section is to prove the design does not merely work technically — it also aligns to the FinOps veto against lifting dead data onto premium tiers.

## Interview soundbite
> I am not claiming penny-perfect pricing. I am showing that the architecture removes the biggest cost mistake: storing archive data on premium primary storage.
