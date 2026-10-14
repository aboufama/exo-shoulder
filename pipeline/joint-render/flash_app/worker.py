"""RunPod Flash worker: Blender 4.2 LTS Cycles chunk renderer for the EXO joint animation (deployed with flash deploy)."""
from runpod_flash import Endpoint, GpuGroup


@Endpoint(name="exo-blender-cycles", gpu=[GpuGroup.ADA_24], workers=(0, 4),
          idle_timeout=30, execution_timeout_ms=900000,
          system_dependencies=["libxrender1", "libxi6", "libxkbcommon0", "libsm6", "libgl1", "libxxf86vm1",
                               "libxfixes3", "libegl1", "xz-utils", "ffmpeg", "wget"])
async def render_chunk(job: dict):
    import base64, gzip, json, os, subprocess, time
    t0 = time.time()
    root = "/tmp/blender-4.2.3-linux-x64"
    if not os.path.exists(root + "/blender"):                                   # once per warm worker
        subprocess.run("cd /tmp && wget -q https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz"
                       " && tar xf blender-4.2.3-linux-x64.tar.xz && rm blender-4.2.3-linux-x64.tar.xz", shell=True, check=True)
    t_setup = time.time() - t0
    work = f"/tmp/job_{job['a']}"
    os.makedirs(work + "/frames", exist_ok=True)
    open(work + "/joint.glb", "wb").write(gzip.decompress(base64.b64decode(job["glb"])))
    open(work + "/motion.json", "wb").write(gzip.decompress(base64.b64decode(job["motion"])))
    open(work + "/render_blender.py", "w").write(job["script"])
    cmd = [root + "/blender", "-b", "--factory-startup", "-P", work + "/render_blender.py", "--",
           "--glb", work + "/joint.glb", "--out", work + "/frames", "--w", str(job["w"]), "--h", str(job["h"]),
           "--spp", str(job["spp"]), "--frames", f"{job['a']}-{job['b']}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    log = (r.stdout + r.stderr)[-3000:]
    frames = sorted(f for f in os.listdir(work + "/frames") if f.endswith(".png"))
    if len(frames) != job["b"] - job["a"] + 1:
        return {"ok": False, "a": job["a"], "log": log, "frames": len(frames)}
    if job.get("png"):                                                           # stills: return the frames themselves
        return {"ok": True, "a": job["a"], "png": {f: base64.b64encode(open(work + "/frames/" + f, "rb").read()).decode() for f in frames},
                "setup_s": round(t_setup, 1), "total_s": round(time.time() - t0, 1)}
    seg = work + "/seg.mp4"
    fps = str(job.get("fps", 30))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", fps, "-start_number", str(job["a"]),
                    "-i", work + "/frames/%04d.png", "-c:v", "libx264", "-preset", "slow", "-crf", "12",
                    "-pix_fmt", "yuv420p", "-r", fps, seg], check=True)
    full = r.stdout + r.stderr
    dev = [l for l in full.splitlines() if l.startswith(("devices:", "compute:")) ][:3] + [l for l in full.splitlines() if l.startswith("Time:")]
    import os as _os; dev.append(f"cpus={_os.cpu_count()} t_blender={time.time() - t0 - t_setup:.1f}s")
    try:
        dev.append(subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"], capture_output=True, text=True).stdout.strip())
    except Exception as e:  # noqa: BLE001
        dev.append(f"nvidia-smi: {e}")
    return {"ok": True, "a": job["a"], "mp4": base64.b64encode(open(seg, "rb").read()).decode(),
            "setup_s": round(t_setup, 1), "total_s": round(time.time() - t0, 1), "dev": dev}
