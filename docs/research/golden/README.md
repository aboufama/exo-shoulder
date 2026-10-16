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

### Parity (the gate): GPU port vs the CPU kit model (zc-frontier-3r evaluate, tools/concept_bench.py fast path)

Same configs, same bench, CPU reference = the kit model itself run on the pod's CPUs (`python3 tools/gpu_bench.py parity
--n 50 --sane --leaders ...`). Configs: 50 random configs inside the rulings (J1 seat region, the zc-frontier BOUNDS, both
branches, all four stack orders, q 0.85-1, end_extra 0-6) whose metal stays inside the +-260 mm grid box (a GPU
pre-pass picks them from 500 draws: the rest have a member at the 400 mm "no clearance" sentinel, are dishonest
(+100) and cost the CPU minutes on libigl's exact path) + the 4 verified / screened leaders' configs (spine-parked
k7008 axes at O20 / margin 5, the spine-parked polish, fold-sph3r and raglan-routed bests - one of them does put
1.57 M points outside the box: the port hands those to the kit's own exact function, `GB_EXACT_OUTSIDE=1`, and matches).

| protocol | configs | max abs diff: gap | reach | follow | in-band 14 | in-band 10 | contact | configs > 1 gap point | GPU s | CPU s (procs) |
|---|---|---|---|---|---|---|---|---|---|---|
| same-bench Bench(110,360) (the golden search objective) | 54 | **0.0** | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | **0** | 251.9 (one leader's 1.57 M outside-box points on libigl) | 249.4 (15) |
| frozen: fit Bench(60,160) -> wear Bench(110,360) (the verifier's protocol) | 54 | **0.0** | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | **0** | 5.7 | 14.8 (15) |

Files: docs/research/golden/gpu_parity_same110.json, gpu_parity_frozen.json (per config: params, GPU and CPU metrics,
honest, hub_F, CPU seconds).

Also measured: Bench(60,160) component parity on the CPU torch path (closure masks, dense K2 masks and every member's
fitted underside identical to the kit, 3 configs incl. inv2 = inv3 = 1) and end-to-end on 2 configs with ~0.5 M
outside-box points each (every metric identical). Parity is exact, not approximate: the port replays the kit's
arithmetic step for step (float64, the kit's integer march, numpy's quantile rule, float32 K6 dots), so the gap of
every config on the list is the same number to the last digit. Gap values of the 54: 46.8 ... 250.3 (median 171).

The first frozen-protocol run (20 configs) disagreed on 6: a bug in the parity script's CPU side (it re-fitted on the
wear bench whenever the FIT-bench gap was >= 200); fixed (= tools/zc_frontier.py cmd_frozen) and re-run: identical.

### Speed (Bench(110,360) same-bench, RTX PRO 4000 Blackwell, `speed --n 576`, metal outside the box on the grid only)

| | evals/s | s per config | notes |
|---|---|---|---|
| GPU pod, chunk 96 | **8.46** | 0.118 | per 96 configs: K2 0.39 s, K3 march + profiles 7.1 s, K6 + skin / crown / top distances 3.6 s - the GPU is saturated (chunk 192 scales linearly) |
| CPU kit, one process (pod EPYC core) | 0.27 | 3.75 median, 6.8 p90 | the parity set (sane configs); the 400 mm-sentinel configs take 1-4 min each on libigl |
| CPU farm worker (8 vCPU, 4 jobs) | ~1.1 | | 4 processes |
| GPU pod, frozen protocol (fit 60/160, wear 110/360), chunk 96 | 12.1 | 0.083 | the fit runs on the smaller bench |

Per dollar: the pod ($0.57/h) gives ~53 k evals/$; a farm worker ($0.288/h) ~13 k evals/$ -> ~4x per dollar, ~8x per
worker slot, and outside the serverless worker quota (the farm's 9 workers would give ~10 evals/s in total).

### First GPU hill-climb (pipeline/gpu_pod/gpu6.sh, same-bench Bench(110,360) = the golden search objective)

`search`: a uniform map of 6144 configs over the whole zero-complexity box (zc-frontier BOUNDS, J1 seat region only,
both branches, all four stack orders) + the 4 leaders as seeds, then (1 + 16) evolution around the 24 best distinct
configs (Gaussian steps on the zc SCALE, x1.25 / x0.85 step control, 5 % sigma / inv flips) until the 30 min budget.
Metal outside the grid box is read on the grid there (`GB_EXACT_OUTSIDE=0`, the configs that have any are counted per
row in `outside` and are dishonest, +100, anyway). Frontier: docs/research/golden/gpu_frontier.json (best 64 + history).

What it measured (new knowledge): the uniform map of 6144 configs found nothing better than the leaders' basin (best
45.2 after the map, the spine-parked polish seed scores 46.8 on this objective); the climb then moved the basin to
**36.66 at 20 min** (honest, hub F 53 / 62 / 70 mm, reach 0.625, follow 0.936, in-band 14 0.874, contact 0.052) - every
top config is the spine-parked family (J1 az ~90, el ~62, a1 ~39, a2 ~66, J3 wdir ~(88, -22), sigma -1) with **inv3 = 1**
(link 2 on hub 3's lower plate, member 3 + neck bridging over it). The gap is still reach (27.5 of 36.7 points), as
docs/research/reach_attribution.md says: every top-64 config sits at reach 0.58-0.64; a 95+ (gap <= 13.75) needs reach
~0.80+ with contact ~0, which the climb has not approached in this family on this bench.
