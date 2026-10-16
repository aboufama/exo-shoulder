# Golden push: shared frontier and compute notes

Target (CLAUDE.md "The golden solution", user 2026-10-16 ~05:50 UTC): verified score >= 95 (gap <= 13.75 on
Bench(110,360) exact, frozen shape) at complexity ~0; fold margin 5 deg; O20 hubs only; J1 on the back of the shoulder +
acromion top only.

## GPU bench (tools/gpu_bench.py) - pod exo-gpu-bench

- Why: the CPU farm is capped at ~5 serverless workers by the account quota and the 4-core box sits at load ~33, so the
  search is compute-bound. A RunPod POD is outside the serverless worker quota.
- Pod: **exo-gpu-bench (id 2odeqs93uh5ua5; the first one, 9qh3ze1zhuu235, was terminated at 06:47 UTC when its parity job hung on a fork after CUDA init - the CPU reference pool now spawns), 1x NVIDIA RTX PRO 4000 Blackwell (24 GB), secure cloud EU-RO-1, $0.57/h** (started 06:12 UTC; the RTX 2000 Ada at $0.24/h had no instance with the volume, so the next cheapest that can mount
  the farm's network volume exo-farm-cas, where the Bench(110,360) signed-distance grid already lives; community pods
  are cheaper per hour only for the 4080 SUPER class and cannot see the volume). No public port: the pod runs job
  scripts that farm jobs drop on the private network volume and writes results back there. Stopped / terminated the
  moment the search ends (idle self-stop after 30 min as a safety net).
- How work reaches the pod: `python3 tools/gpu_pod.py submit <job.sh> <name> --include tools/gpu_bench.py` (one farm
  job drops the script + files on the volume; the pod's spool runs it), `python3 tools/gpu_pod.py fetch <name>
  --outdir DIR` (one farm job brings exo-farm/gpu/out/<name>/ back). Jobs: pipeline/gpu_pod/*.sh.

### The port (tools/gpu_bench.py)

Family = docs/concepts/models/zc-frontier-3r.py exactly (three active pins through GH, O20 hubs, 12 x 3 straps with the
kit's skin-fitted K3 undersides + ramps + `over` + 60 deg climb, the K7 14 x 6 neck, stack orders inv2 / inv3, fold
margin 5, 1 mm radial K6, hub crowns / walls, every member's top face, the audit's sampling and pose-locality rules,
hub_F <= 140, the J1 seat region). Every step is the kit's own arithmetic in float64 on the device (the K6 dot
products in float32, as the kit); continuity slerps come from scipy tables (the kit's Slerp). Configs are batched
(48-72 per call, grouped by stack order); strap sample counts vary per config and are padded with duplicates of the
last sample (zero weight in the in-band share). Protocols: same-bench (the golden search: fit = wear = Bench(110,360))
and frozen (fit Bench(60,160) -> wear Bench(110,360), the verifier's protocol).
