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
row in `outside` and are dishonest, +100, anyway). Frontier: docs/research/golden/gpu_climb_gpu6.json (best 64 + history; was gpu_frontier.json).

What it measured (new knowledge): the uniform map of 6144 configs found nothing better than the leaders' basin (best
45.2 after the map, the spine-parked polish seed scores 46.8 on this objective); the climb then moved the basin to
**36.66 at 20 min** (honest, hub F 53 / 62 / 70 mm, reach 0.625, follow 0.936, in-band 14 0.874, contact 0.052) - every
top config is the spine-parked family (J1 az ~90, el ~62, a1 ~39, a2 ~66, J3 wdir ~(88, -22), sigma -1) with **inv3 = 1**
(link 2 on hub 3's lower plate, member 3 + neck bridging over it). The gap is still reach (27.5 of 36.7 points), as
docs/research/reach_attribution.md says: every top-64 config sits at reach 0.58-0.64; a 95+ (gap <= 13.75) needs reach
~0.80+ with contact ~0, which the climb has not approached in this family on this bench.

Pod log: exo-gpu-bench #1 (9qh3ze1zhuu235) 06:11-06:47 UTC, #2 (2odeqs93uh5ua5) 06:47-08:01 UTC, both terminated;
~1.7 h x $0.57 = ~$1.0. Lesson: the pod's cgroup holds 31 GB, so a 40-process CPU reference pool got OOM-killed workers
and hung (multiprocessing waits forever) - keep the CPU pool at <= 15 processes on this pod type.

Next (the loop): (1) verify the frontier's top configs on the exact path (`python3 tools/zc_frontier.py frozen
'<params>' OUT.json` on the farm: fit 110/360 fast -> wear exact, and the verifier protocol 60/160 -> 110/360 exact);
(2) restart the pod (`tools/gpu_pod.py create`, queue pipeline/gpu_pod/boot.sh then a search job) for longer climbs
from the inv3 = 1 basin and a 4-DOF / fold-lever family port - reach, not proximity, is what is left to win.

## Exhaustive GPU search of the zero-complexity class (2026-10-16, from 08:10 UTC)

Pods (outside the serverless worker quota, both mounting the farm volume exo-farm-cas, secure cloud EU-RO-1; work
reaches them through the volume spool as before): **exo-gpu-bench = 1x NVIDIA RTX PRO 4000 Blackwell (24 GB), $0.57/h**
(spool exo-farm/gpux0) and **exo-gpu-bench2 = 1x NVIDIA RTX 5090 (32 GB), $1.19/h** (spool exo-farm/gpux1; wall clock
is the constraint). Time box ~2.3 h, ~$4 at most; both are terminated the moment the search ends. The farm queue was
31 jobs deep (golden-push), so the first pods (08:09, spool only) were terminated after 9 min unused and re-created at
08:18 carrying their code and jobs in the pod definition (`tools/gpu_pod.py create --payload ... --jobs ...`: an env
var with the tar.gz of the code, unpacked at start, jobs queued in the pod's own spool) - no farm round trip to start.

Third pod: **exo-gpu-bench3 = 1x NVIDIA RTX 5090 (32 GB), $1.19/h** from 08:30 UTC (spool exo-farm/gpux3; a first one on an
RTX PRO 4500 Blackwell at $0.72/h ran 08:28-08:30 and was terminated to fix its sweep budget), for an independent ~10^6-config Sobol sweep (pipeline/gpu_pod/xs2.sh, scramble seed 12): the
first halves (57,652 configs each) took ~1 min for the bounds and ~1 min for the full bench of what passed them.

Method (pipeline/gpu_pod/xs.sh, `tools/gpu_bench.py screen` / `cma`, both pods = 2 halves of one Sobol sequence):
1. **Sobol map of the whole class** (scrambled Sobol, seed 11, 11 dims = tools/zc_frontier.py cmd_sobol's map: J1 seat
   az / el area-uniform over the allowed back + acromion-top region only, J3 direction area-uniform over the arm-frame
   sphere wd 20-175 (both ends of the J3 line), arcs a1 / a2 12-168 (both ends of the J2 line), branch, q 0.8-1, end
   hold 0-8), on **Bench(110,360)** (the verification pose set).
2. **Exact lower bounds, no strap needed**: stage A = K1 closure + K2 dense continuity (the full bench's own mask) ->
   reach / follow upper bounds; stage B = the three O20 hub discs alone: their K3 levels (= the full bench's hub F,
   which no strap changes; > 140 mm = +100) and the poses where a hub underside / crown / wall / top face is inside the
   skin at that level (never `good` in the full bench). Bound = 100 (max(0, .90 - reach_ub) + max(0, .95 - follow_ub))
   (+100 if a hub F > 140): reach / follow can only drop further, in-band and contact only add, so the plain AND the
   near-touch gap of every config are >= its bound.
3. **Full bench in bound order** for every config with bound < 45, at both J3 stack orders (inv2 = 0, inv3 = 0 / 1),
   until the budget: the certificate is the bound of the first config left out (nothing below it was skipped).
4. **Batched multi-start CMA-ES** (one CMA per basin, lambda 12, all populations in one GPU call, near-touch objective
   by the CLAUDE.md rule) from the 50 best distinct basins of both screens (+ the CPU optimum 28.85 and the 20-min climb's
   36.66 as seeds), a converged start (sigma or 15 generations without a 0.05 gain) hands its slot to the next basin.
5. **Outside judge**: the 10 best distinct configs by GPU plain gap -> `tools/zc_frontier.py frozen` (the zc model's
   checks + docs/concepts/verify/spine-parked-j2-3r.py top_check, O20, margin 5) on the pods' CPUs: fit Bench(110,360)
   fast -> wear Bench(110,360) EXACT, and the verifier protocol fit Bench(60,160) fast -> wear Bench(110,360) EXACT.

## Pin-knee port (tools/gpu_bench_knee.py) - pod exo-gpu-pinknee

Why: the leader family (skin-normal-3r-pin-knee, H1; raglan-knee-3r routes) is searched by tools/knee_polish.py on
the CPU farm, which is capped at 5 serverless workers and had a 37-job queue; the zero-complexity port showed a pod runs
outside that quota. Pod: **exo-gpu-pinknee = 1x NVIDIA RTX PRO 4500 Blackwell (32 GB), 10 vCPU, secure EU-RO-1, $0.72/h**
(the RTX PRO 4000 at $0.57/h, A4000, 4000 Ada, 2000 Ada, A5000, L4 and A4500 had no instance with the volume at 08:31 UTC;
this was the cheapest in stock), spool exo-farm/gpuk (`tools/gpu_pod.py create --name exo-gpu-pinknee --spool gpuk`),
code through the volume (pipeline/gpu_pod/knee0.sh boots and waits for the code tarball; knee1.sh / knee2.sh run
knee_run.sh / knee_run2.sh). The pod terminates itself when its search ends (idle self-stop 30 min as the safety net).

### What the port is: the kit, accelerated - not a re-model

Every configuration is built by the CPU kit's own code, unchanged: knee_polish.evaluate (same bench) or
knee_polish.frozen_on + score_model (frozen) -> the pin-knee model (seats on the rest skin along GH rays for J1 / J2,
the tilted J3 line b3, the spherical IK and fold margin, the closed-form planar knee, its window [ang_min, 180 - ang_min]
and fixed branch, 10 fps continuity incl. the knee, the part geometry: O20 hubs with the 12.25 stack, 8 x 3 straps with
skin-fitted undersides and 60 deg ramps, E strap + E boss (O12) on hub 3's member, knee link, arm pad, pin stack, the
greedy pose drop, finalize, contact-only walls / crowns / tops / edges) -> the verifier's checks -> the near-touch
audit. tools/gpu_bench_knee.py replaces only the per-pose loops, with batched torch code on the device:

| replaced | by | arithmetic |
|---|---|---|
| S.Model.needed (sphere-traced skin requirement, 16 steps, per-pose break, inside-at-start -> BIG, slab test vs the knee / pad boxes for link 2) | `needed`: every pose at once, a per-pose `done` mask = the CPU break | the model's transforms (numpy, all poses at once), float64 |
| the run loop (`_run_batched`: every non-adjacent pair >= 1 mm - hubs, straps, E strap, knee link, pad; adjacent E-L2 / knee-hub 3 / knee-E >= 0.15 mm; jam rule; metal + contact-only distances; B.res, cmin, why) | `run` + `collide_all`: all valid poses at once, nearest-neighbour minima by brute force (exact distances, as cKDTree) | same sd_cyl / sd_box formulas |
| the verifier's extra_checks (independent 3D closure of hub 3 / pin a / pin b / both knee axes, knee vs hub 3's upper half 1 mm, E boss vs hubs 1-2, link 1 (1 mm) and link 2 (0.15 mm)) | `extra_checks`, all taken poses at once | same |
| Bench.dist (trilinear on the int8 grid) | `GridDev.dist` on the device | concept_bench's corner order, float32 corners x float64 weights; points outside the +-260 mm box -> the kit's exact libigl path |
| v2 only: the seats' exact distance on the rest skin; S.Design.ik | `ExactCached` (the same libigl AABB + fast-winding-number BVH, built once instead of per call: max diff 0.0 on 6.5k points); `ik_vec` (rotm batched instead of per frame: bitwise equal on 6000 frames x 7 configs) | identical |

Margin is a parameter (`--margin`, CB_FOLD_MARGIN set before the kit loads; 5 = the user's ruling); hubs O20 only;
raglan-knee-3r's routed links (r1t / r1d / r2t / r2d / rc) are installed on the verifier's pin-knee model by the
raglan model's own `routed_add_links` (great circle bit for bit when |r1d|, |r2d| < 0.25) in BOTH the port and the CPU
reference.

### Parity (the gate): port on the pod's GPU vs the CPU kit itself on the pod's CPUs, same configs, same bench

Configs (`--mix --leaders`, seed 0): H1, k4598, P5 (+ raglan-knee-3r's best in v2) + 50 inside the rulings: 40 near the
three leaders at 0.5 / 1 / 2 / 3 x knee_polish's CMA scale, 10 uniform in the polish bounds (FREE), O20, J1 seat on the
back / acromion top (anterior component <= 0.20). Metrics compared: the knee_polish objective set - gap (verifier-
corrected), near-touch gap (metal < 1 mm = contact) and < 2 mm, the model's own gap, reach, follow, in-band 2-14 /
2-10, contact.

| protocol (margin 5, O20) | configs compared | max abs diff: gap | near-touch gap (< 1 mm) | < 2 mm | model gap | reach | follow | in-band 14 | in-band 10 | contact | configs > 0.5 (gap / near-touch) | GPU s | CPU s (procs) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| same-bench Bench(110,360) (the polish objective) | 53 / 53 | **0.0** | **0.0** | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | **0** / 0 | 363.9 (6 workers) | 411.4 (3) |
| frozen: fit Bench(60,160) -> wear Bench(110,360) (the round-3 verifier's protocol) | 53 / 53 | **0.0** | **0.0** | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | **0** / 0 | 278.4 (6 workers) | 334.3 (3) |

Port v1 (no CPU-side changes), RTX PRO 4500 pod, 2026-10-16 08:36-08:48 UTC. Every one of the 53 configs agrees to the
last printed digit on every metric in both protocols (parity is exact, not approximate: the kit's arithmetic is replayed
step for step; the device's float64 matmuls differ from BLAS by ulps at most, and no threshold sat that close). The set
spans gap 21.5 ... 375 (29 configs < 100; 13 all-contact at 375 same-bench). Leaders, same-bench (plain / near-touch):
H1 24.57 / 25.68 (= the rebase track's H1 objective at margin 5, 25.68), k4598 29.97 / 34.23, P5 21.54 / 22.08;
frozen: H1 27.28 / 30.62, k4598 29.63 / 34.48, P5 24.94 / 31.46 (fast grid on the wear bench; the exact-path claims stay
with the verifier). Also measured on this box before the pod (CPU torch, Bench(60,160) same-bench): 10 configs incl. the
three leaders and raglan-knee-3r's routed best (22.69 / 29.82 on both sides) - identical.

Files: docs/research/golden/knee_parity_same110.json, knee_parity_frozen.json (per config: params, GPU and CPU metrics).


Port v2 (+ the bit-identical CPU-side speed-ups and raglan routes; 08:48-08:58 UTC, 8 GPU workers; the CPU rows of v1
reused for the same 53 configs - the CPU side does not depend on the port - and raglan-knee-3r's best run fresh on
the CPU):

| protocol (margin 5, O20) | configs compared | max abs diff: gap | near-touch | < 2 mm | model gap | reach | follow | in-band 14 | in-band 10 | contact | configs > 0.5 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| same-bench Bench(110,360) | 54 / 54 | **0.0** | **0.0** | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | **0** / 0 |
| fit Bench(60,160) -> wear Bench(110,360) | 54 / 54 | **0.0** | **0.0** | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | **0** / 0 |

raglan-knee-3r's best (routed link 1: r1t 0.80, r1d -30.6): same-bench 32.31 / near-touch 36.82, frozen 27.88 / 32.97
(its verified 27.82 at margin 5 is the exact wear path) - identical on both sides.
Files: knee_parity2_same110.json, knee_parity2_frozen.json.

### Speed

| | s per config, configs with gap < 100 (median / mean) | notes |
|---|---|---|
| CPU kit (knee_polish.evaluate / frozen_on), one process on the pod | same-bench 8.18 / 8.69, frozen 10.94 / 12.07 | the parity reference, 2-3 processes beside the GPU workers |
| port v1 (6 workers, 3 CPU processes beside them) | 4.32 / 5.46, frozen 11.42 / 11.43 | v1 still ran the seats' libigl trees per call (1.7 s / config) and the per-frame IK |
| **port v2** (8 workers) | **0.86 / 1.99, frozen 0.72 / 0.76** | **9.5x (same-bench) - 15x (frozen) per process**; the rest is the kit's CPU-side Python (greedy drop, finalize, report, audit) |
| port v2, 9 workers, `speed --n 72` (the parity mix incl. 14 uniform-random configs) | 0.91 median, 0.29 evals/s overall | the wall clock is set by 3 junk configs (uniform draws, gap 375) whose traced samples leave the +-260 mm grid box: the kit's exact libigl path per pose, 1-4 min each on the CPU in BOTH implementations (r42: 263 s port, 257 s kit) |

Where the time goes (cProfile, v2 on CPU torch, Bench(60,160)): the batched distance / pair work is the only large
item and it moves to the GPU; the seats' rest-skin distances fell from 1.72 s to 0.009 s per config (ExactCached). Per
dollar: in the polish region a v2 worker does ~1.1 configs/s; the pod's 10 vCPU carry ~8 workers -> ~8 evals/s for
$0.72/h (~40 k evals/$), against ~0.4 evals/s for a farm worker at $0.288/h (4 kit processes at ~10 s; ~5 k evals/$):
~8x per dollar and outside the serverless worker quota. Next lever: batch configurations inside one process (the
zero-complexity port's design) and port the greedy drop - the CPU-side Python is now the limit, not the GPU.

### Search

(pending)
