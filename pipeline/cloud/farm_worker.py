"""RunPod Flash CPU farm endpoint (exo-cpu1): runs named commands of this repo on serverless CPU workers.
Logic in farm_impl.py; client tools/cloud_run.py; how-to docs/CLOUD_RUN.md; costs docs/RUNPOD_COSTS.md.
Deploy (from this directory): RUNPOD_API_KEY="$(cat ~/.runpod_key)" flash deploy --python-version 3.12   (the Flash CPU image is CPython 3.12;
packages are pinned to the local versions, so the judges give the same numbers as on CPython 3.11 locally - validated)

Instance: cpu3c-8-16 (3rd-gen compute-optimised, 8 vCPU, 16 GB) = the lowest serverless $/vCPU-h RunPod lists
($0.288/h = $0.036 per vCPU-h, GraphQL cpuFlavors.specifics slsPrice, EU-RO-1, 2026-10-15; cpu3c is the same per vCPU at
every size, and 8 vCPU is the largest size Flash 1.20 accepts); cpu5c-8-16 ($0.336/h) only as the fallback when cpu3c has
no stock. 4 jobs per worker (max_concurrency 4) because the account's worker quota is 10 across ALL endpoints (GPU search +
the user's render endpoint held 6 + 4 of it on 2026-10-15): 4 workers give 16 job slots (a job alone gets all 8 vCPU).
CPU serverless exists only in EU-RO-1, so the CAS network volume lives there too.
Scale to zero (workersMin 0), idle 10 s, workersMax 4, 1 h server-side runaway limit.
Redeploy without a new endpoint (the account worker quota refuses one): tools/farm_redeploy.py.
"""
import os

from runpod_flash import CpuInstanceType, DataCenter, Endpoint, NetworkVolume

JOBS_PER_WORKER = 4                                            # keep equal to max_concurrency below (a literal: flash reads it statically)
# The Flash CPU image boots /app/handler.py, which imports the generated handler_exo-cpu1.py as a module and then calls
# runpod.serverless.start({"handler": handler}) WITHOUT the generated concurrency_modifier: max_concurrency=4 was never
# applied and every worker took ONE job at a time (measured 2026-10-15 21:45 UTC on the farm-2 build: 12 sleep-20 jobs,
# max 1 concurrent per worker; runpod 1.10.1 has no env var for it). This module is imported while that handler loads,
# before start() runs, so wrap start() to add the modifier. Worker only (RUNPOD_ENDPOINT_ID), never at build time; any
# failure leaves the stock 1-job behaviour.
if os.environ.get("RUNPOD_ENDPOINT_ID"):
    try:
        import runpod.serverless as _rs

        if not getattr(_rs.start, "_farm_concurrency", False):
            _start0 = _rs.start

            def _start(config, *a, **k):
                if isinstance(config, dict):
                    config.setdefault("concurrency_modifier", lambda current: JOBS_PER_WORKER)
                return _start0(config, *a, **k)

            _start._farm_concurrency = True
            _rs.start = _start
    except Exception:                                           # noqa: BLE001
        pass

VOL = NetworkVolume(name="exo-farm-cas", size=20, datacenter=DataCenter.EU_RO_1)        # 20 GB = $1.40/month


@Endpoint(name="exo-cpu1", cpu=[CpuInstanceType.CPU3C_8_16, CpuInstanceType.CPU5C_8_16], workers=(0, 4), idle_timeout=10,
          execution_timeout_ms=3600000, volume=VOL, datacenter=DataCenter.EU_RO_1, max_concurrency=4,
          dependencies=["numpy==2.0.2", "scipy==1.13.1", "trimesh==4.12.2", "libigl==2.6.3", "networkx==3.6.1", "rtree==1.4.1",
                        "mujoco==3.16.0", "pillow"])
async def farm_job(job: dict):
    import asyncio, os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import farm_impl
    return await asyncio.to_thread(farm_impl.handle, job)          # blocking work off the event loop: 4 jobs share a worker
