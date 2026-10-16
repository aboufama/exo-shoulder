# Golden push: shared frontier and compute notes

Target (CLAUDE.md "The golden solution", user 2026-10-16 ~05:50 UTC): verified score >= 95 (gap <= 13.75 on
Bench(110,360) exact, frozen shape) at complexity ~0; fold margin 5 deg; O20 hubs only; J1 on the back of the shoulder +
acromion top only.

## GPU bench (tools/gpu_bench.py) - pod exo-gpu-bench

- Why: the CPU farm is capped at ~5 serverless workers by the account quota and the 4-core box sits at load ~33, so the
  search is compute-bound. A RunPod POD is outside the serverless worker quota.
- Pod: **exo-gpu-bench (id 9qh3ze1zhuu235), 1x NVIDIA RTX PRO 4000 Blackwell (24 GB), secure cloud EU-RO-1, $0.57/h** (started 06:12 UTC; the RTX 2000 Ada at $0.24/h had no instance with the volume, so the next cheapest that can mount
  the farm's network volume exo-farm-cas, where the Bench(110,360) signed-distance grid already lives; community pods
  are cheaper per hour only for the 4080 SUPER class and cannot see the volume). No public port: the pod runs job
  scripts that farm jobs drop on the private network volume and writes results back there. Stopped / terminated the
  moment the search ends (idle self-stop after 30 min as a safety net).
