# Automation Logic — Pre-Cutover Replication Health Orchestrator

## Chosen option
I selected **Option 2** because it directly supports the cutover Go/No-Go decision and is highly demonstrable in an interview.

## What it does
A Python orchestrator running from a Linux VM:
- reads a CSV inventory of 300 volumes
- queries replication status in parallel
- evaluates each volume against thresholds
- emits a **Red / Amber / Green** result per volume
- produces an overall **GO / NO-GO** output

## Checks performed per volume
- SnapMirror relationship exists
- relationship state is healthy
- mirror lag under threshold
- last transfer completed successfully
- last successful snapshot transfer within allowed age

## Example RAG logic
- **Green**: healthy, lag within SLA, recent successful transfer
- **Amber**: healthy but lag nearing threshold or partial warning
- **Red**: failed transfer, broken relationship, stale lag, or query error

## Why the panel will like this choice
- directly tied to the 4-hour cutover playbook
- easy to explain operationally
- production-minded because it uses bounded concurrency, CSV output, and deterministic decision rules
- shows that automation is supporting architecture, not replacing it
