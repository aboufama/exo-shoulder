"""Render the EXO joint animation on RunPod Serverless (Flash): a queue-based Blender Cycles worker that scales to
zero. Each job renders a chunk of frames headless with the official Blender 4.2 LTS build (cached per warm worker)
and returns that chunk as a short lossless-quality H.264 segment; the segments are concatenated locally.

    RUNPOD_API_KEY=$(cat ~/.runpod_key) ~/.local/share/uv/tools/runpod-flash/bin/python serverless_render.py [--chunk 24]

Inputs read from this folder: joint.glb (scene), motion.json (choreography from motion.py), render_blender.py.
Output: EXO_joint_exploded_rt.mp4.
"""
import argparse
import asyncio
import base64
import gzip
import json
import os
import subprocess
import time

from runpod_flash import Endpoint

HERE = os.path.dirname(os.path.abspath(__file__))


EP_ID = "dj3qfmtwrwy2pr"                     # deployed from flash_app/worker.py (flash deploy --app exo-render)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunk", type=int, default=24); ap.add_argument("--w", type=int, default=1920)
    ap.add_argument("--h", type=int, default=1080); ap.add_argument("--spp", type=int, default=160)
    ap.add_argument("--only", type=int, default=0, help="render just the first N chunks (test)")
    ap.add_argument("--glb", default="joint.glb"); ap.add_argument("--motion", default="motion.json")
    ap.add_argument("--script", default="render_blender.py"); ap.add_argument("--out", default="EXO_joint_exploded_rt.mp4")
    ap.add_argument("--fps", type=int, default=30)
    args = ap.parse_args()
    glb = base64.b64encode(gzip.compress(open(os.path.join(HERE, args.glb), "rb").read(), 9)).decode()
    motion = base64.b64encode(gzip.compress(open(os.path.join(HERE, args.motion), "rb").read(), 9)).decode()
    script = open(os.path.join(HERE, args.script)).read()
    N = len(json.load(open(os.path.join(HERE, args.motion)))["frames"])
    print(f"payload {(len(glb) + len(motion) + len(script)) / 1e6:.1f} MB per job", flush=True)
    chunks = [(a, min(a + args.chunk, N) - 1) for a in range(0, N, args.chunk)]
    if args.only:
        chunks = chunks[:args.only]
    print(f"{N} frames -> {len(chunks)} jobs of {args.chunk}", flush=True)
    os.makedirs(os.path.join(HERE, "segments"), exist_ok=True)
    t0 = time.time()
    ep = Endpoint(id=EP_ID)

    gate = asyncio.Semaphore(10)                                   # one job in flight per worker: no upload pile-up

    async def one(a, b):
        if os.path.exists(os.path.join(HERE, "segments", f"seg_{a:04d}.mp4")):
            return True
        async with gate:
            return await _one(a, b)

    async def _one(a, b):
        for attempt in range(3):
            try:
                job = await ep.run({"job": dict(glb=glb, motion=motion, script=script, a=a, b=b, w=args.w, h=args.h, spp=args.spp, fps=args.fps)})
                await job.wait()
                res = job.output or {}
                if isinstance(res, dict) and "output" in res and "ok" not in res:
                    res = res["output"]
                if res.get("ok"):
                    open(os.path.join(HERE, "segments", f"seg_{a:04d}.mp4"), "wb").write(base64.b64decode(res["mp4"]))
                    print(f"  frames {a}-{b} done in {res['total_s']} s (setup {res['setup_s']} s) {res['dev']}  [{time.time() - t0:.0f} s]", flush=True)
                    return True
                print(f"  frames {a}-{b} FAILED (attempt {attempt + 1}): {res.get('frames')} frames\n{res.get('log', '')[-1500:]}", flush=True)
            except Exception as e:                                               # noqa: BLE001
                print(f"  frames {a}-{b} error (attempt {attempt + 1}): {e!r}", flush=True)
        return False

    ok = await asyncio.gather(*[one(a, b) for a, b in chunks])
    print(f"{sum(ok)}/{len(chunks)} chunks in {time.time() - t0:.0f} s", flush=True)
    if all(ok) and not args.only:
        lst = os.path.join(HERE, "segments", "list.txt")
        open(lst, "w").write("".join(f"file 'seg_{a:04d}.mp4'\n" for a, _ in chunks))
        out = os.path.join(HERE, args.out)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], check=True)
        print("WROTE", out, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
