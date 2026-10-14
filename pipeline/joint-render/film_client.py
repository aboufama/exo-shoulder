"""Render a film or stills on the RunPod Blender endpoint (exo-render): per-chunk motion files.

    film:   python film_client.py film  <film_render dir> <out.mp4>   [--spp 128] [--w 1920 --h 1080]
    stills: python film_client.py stills <scene.glb> <motion.json> <out dir> [--spp 256]
(run with the Flash tool python and RUNPOD_API_KEY set)
"""
import argparse, asyncio, base64, gzip, json, os, subprocess, sys, time
from runpod_flash import Endpoint
HERE = os.path.dirname(os.path.abspath(__file__)); EP_ID = "dj3qfmtwrwy2pr"
ap = argparse.ArgumentParser(); ap.add_argument("mode"); ap.add_argument("a1"); ap.add_argument("a2"); ap.add_argument("a3", nargs="?")
ap.add_argument("--spp", type=int, default=128); ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080); ap.add_argument("--only", type=int, default=0)
args = ap.parse_args()
b64z = lambda p: base64.b64encode(gzip.compress(open(p, "rb").read(), 9)).decode()
async def main():
    ep = Endpoint(id=EP_ID); gate = asyncio.Semaphore(10); t0 = time.time()
    if args.mode == "film":
        D = args.a1; out = args.a2; idx = json.load(open(os.path.join(D, "index.json"))); glb = b64z(os.path.join(D, "designs.glb"))
        script = open(os.path.join(HERE, "render_film.py")).read(); seg_dir = os.path.join(D, "segments"); os.makedirs(seg_dir, exist_ok=True)
        chunks = sorted(f for f in os.listdir(D) if f.startswith("motion_"))
        if args.only: chunks = chunks[:args.only]
        async def one(fn):
            m = json.load(open(os.path.join(D, fn))); a, b = m["a"], m["b"]; dst = os.path.join(seg_dir, f"seg_{a:04d}.mp4")
            if os.path.exists(dst): return True
            async with gate:
                for att in range(3):
                    try:
                        job = await ep.run({"job": dict(glb=glb, motion=b64z(os.path.join(D, fn)), script=script, a=a, b=b, w=args.w, h=args.h, spp=args.spp, fps=idx["fps"])})
                        await job.wait(); r = job.output or {}
                        if isinstance(r, dict) and "output" in r and "ok" not in r: r = r["output"]
                        if r.get("ok"): open(dst, "wb").write(base64.b64decode(r["mp4"])); print(f"  {a}-{b} ok {r['total_s']} s [{time.time() - t0:.0f} s]", flush=True); return True
                        print(f"  {a}-{b} failed: {str(r.get('log', ''))[-800:]}", flush=True)
                    except Exception as e: print(f"  {a}-{b} error {e!r}", flush=True)
            return False
        ok = await asyncio.gather(*[one(c) for c in chunks]); print(f"{sum(ok)}/{len(chunks)} chunks in {time.time() - t0:.0f} s")
        if all(ok) and not args.only:
            segs = sorted(os.listdir(seg_dir)); lst = os.path.join(seg_dir, "list.txt"); open(lst, "w").write("".join(f"file '{s}'\n" for s in segs if s.endswith(".mp4")))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], check=True)
            print("WROTE", out)
    else:
        glb, motion, out = args.a1, args.a2, args.a3; os.makedirs(out, exist_ok=True); n = len(json.load(open(motion))["frames"])
        job = await ep.run({"job": dict(glb=b64z(glb), motion=b64z(motion), script=open(os.path.join(HERE, "render_stills.py")).read(), a=0, b=n - 1, w=args.w, h=args.h, spp=args.spp, fps=1, png=True)})
        await job.wait(); r = job.output or {}
        if isinstance(r, dict) and "output" in r and "ok" not in r: r = r["output"]
        if not r.get("ok"): print("failed", str(r)[:2000]); return
        if "png" in r:
            for f, b in r["png"].items(): open(os.path.join(out, f), "wb").write(base64.b64decode(b))
        else:                                                                         # older worker: frames come back as a short MP4
            mp = os.path.join(out, "stills.mp4"); open(mp, "wb").write(base64.b64decode(r["mp4"]))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp, "-vsync", "0", os.path.join(out, "%04d.png")], check=True)
        print(f"stills in {r['total_s']} s (setup {r.get('setup_s')} s) -> {out}", r.get("dev", ""))
asyncio.run(main())
