#!/usr/bin/env python3
"""The exo-gpu-bench RunPod POD (outside the serverless worker quota) - stdlib only, the API key is never printed.

    python3 tools/gpu_pod.py create [--gpu "NVIDIA RTX 2000 Ada Generation"]   start the pod (secure EU-RO-1 + the farm volume)
    python3 tools/gpu_pod.py status                                           its state, $/h, uptime
    python3 tools/gpu_pod.py stop | terminate                                 stop (keeps the container disk) / terminate
    python3 tools/gpu_pod.py submit <script.sh> <job name> [--include PATH]... drop a job (+ files under exo-farm/gpu/code/)
    python3 tools/gpu_pod.py fetch <job name> [--outdir DIR]                  print its log (+ bring out/<job name>/ back)

How work reaches it: no public port. The pod mounts the farm's private network volume exo-farm-cas at /workspace and runs,
one at a time, the job scripts that farm jobs (tools/cloud_run.py, authenticated by our RunPod key) drop in
exo-farm/gpu/queue/*.sh (alphabetical order); each job's log goes to exo-farm/gpu/out/<job>.log; a file
exo-farm/gpu/cancel kills the running job (`python3 tools/gpu_pod.py cancel`). A fresh pod needs the boot job first
(pipeline/gpu_pod/boot.sh: torch with Blackwell kernels, the repo tree, the bench grids). After 30 min with no job it stops itself
(runpodctl, the pod-scoped key RunPod injects) as a safety net; the search driver stops it when the search ends.
Never touches pods whose name does not start with exo-gpu (crl-* are the user's).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runpod_guard as G                                     # noqa: E402

NAME = "exo-gpu-bench"
VOLUME = "u9gf22x1a2"                                        # exo-farm-cas, EU-RO-1
IMAGE = "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"
SPOOL = ("G=/workspace/exo-farm/gpu; mkdir -p $G/queue $G/done $G/out; "
         "echo \"$(date -u +%FT%TZ) up $RUNPOD_POD_ID\" >> $G/pod.log; nvidia-smi -L >> $G/pod.log 2>&1; idle=0; "
         "while true; do j=$(ls $G/queue/*.sh 2>/dev/null | head -1); "
         "if [ -n \"$j\" ]; then b=$(basename $j .sh); mv $j $G/done/$b.sh; rm -f $G/cancel; "
         "cd $G; setsid timeout 4h bash $G/done/$b.sh > $G/out/$b.log 2>&1 & p=$!; echo $p > $G/running.pid; "
         "while kill -0 $p 2>/dev/null; do if [ -f $G/cancel ]; then kill -- -$p; echo cancelled >> $G/out/$b.log; rm -f $G/cancel; fi; sleep 3; done; "
         "echo \"end $(date -u +%FT%TZ)\" >> $G/out/$b.log; touch $G/out/$b.done; idle=0; "
         "else sleep 5; idle=$((idle+5)); fi; "
         "if [ $idle -ge 1800 ]; then echo \"$(date -u +%FT%TZ) idle-stop\" >> $G/pod.log; runpodctl stop pod $RUNPOD_POD_ID; sleep 600; fi; done")


def pods():
    return [p for p in G.gql("query { myself { pods { id name desiredStatus costPerHr uptimeSeconds: lastStatusChange "
                             "machine { gpuDisplayName } } } }")["myself"]["pods"] if p["name"].startswith("exo-gpu")]


def create(gpu, name=NAME, spool="gpu"):
    """spool = the pod's queue / out folder under exo-farm/ (a 2nd pod gets its own: gpu2, ...; code/ stays in exo-farm/gpu)"""
    if any(p["name"] == name and p["desiredStatus"] == "RUNNING" for p in pods()): print("already running"); return
    q = ('mutation { podFindAndDeployOnDemand(input: { cloudType: SECURE, gpuCount: 1, gpuTypeId: %s, name: "%s", '
         'imageName: "%s", containerDiskInGb: 30, volumeInGb: 0, networkVolumeId: "%s", dataCenterId: "EU-RO-1", '
         'volumeMountPath: "/workspace", startSsh: false, dockerArgs: %s }) { id desiredStatus costPerHr machine { gpuDisplayName } } }'
         % (json.dumps(gpu), name, IMAGE, VOLUME, json.dumps("bash -c " + json.dumps(SPOOL.replace("exo-farm/gpu;", f"exo-farm/{spool};")))))
    print(json.dumps(G.gql(q)["podFindAndDeployOnDemand"]))


def act(what, name=NAME):
    for p in pods():
        if p["name"] != name: continue
        m = "podStop" if what == "stop" else "podTerminate"
        G.gql('mutation { %s(input: {podId: "%s"}) %s }' % (m, p["id"], "{ id desiredStatus }" if m == "podStop" else ""))
        print(what, p["id"])


def submit(script, name, include=(), spool="gpu"):
    """drop a job script (and files it needs, under exo-farm/gpu/code/) on the volume through one farm job"""
    import subprocess
    inc = sum((["--include", x] for x in [script, *include]), [])
    cmd = ("set -e; V=/runpod-volume/exo-farm/gpu; mkdir -p $V/code $V/queue; "
           + "".join(f"mkdir -p $V/code/$(dirname {x}); cp -r {x} $V/code/{x}; " for x in include)
           + f"Q=/runpod-volume/exo-farm/{spool}; mkdir -p $Q/queue; cp {script} $Q/queue/{name}.sh.tmp; mv $Q/queue/{name}.sh.tmp $Q/queue/{name}.sh; ls -la $Q/queue $Q/out | tail -8; tail -3 $Q/pod.log")
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "cloud_run.py"), "run", "--no-base", "--no-bench-cache",
                    "--timeout", "600", *inc, "--", cmd], check=False)


def cancel():
    """kill the job the pod is running (through one farm job)"""
    import subprocess
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "cloud_run.py"), "run", "--no-base", "--no-bench-cache",
                    "--timeout", "300", "--", "touch /runpod-volume/exo-farm/gpu/cancel; ls /runpod-volume/exo-farm/gpu/"], check=False)


def fetch(name, outdir=None, spool="gpu"):
    """print a job's log (and bring exo-farm/<spool>/out/<name>/ back under outdir) through one farm job"""
    import subprocess
    cmd = (f"V=/runpod-volume/exo-farm/{spool}; tail -3 $V/pod.log; ls $V/out | tail -5; echo ---; tail -c 20000 $V/out/{name}.log; "
           f"mkdir -p gpu_out; [ -d $V/out/{name} ] && cp -r $V/out/{name} gpu_out/ || true")
    extra = ["--out", f"gpu_out/{name}/*", "--outdir", outdir] if outdir else []
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "cloud_run.py"), "run", "--no-base", "--no-bench-cache",
                    "--timeout", "600", *extra, "--", cmd], check=False)


if __name__ == "__main__":
    a = sys.argv[1:] or ["status"]
    nm = a[a.index("--name") + 1] if "--name" in a else NAME          # a 2nd pod: --name exo-gpu-bench2 --spool gpu2
    sp = a[a.index("--spool") + 1] if "--spool" in a else "gpu"
    if a[0] == "create": create(a[a.index("--gpu") + 1] if "--gpu" in a else "NVIDIA RTX 2000 Ada Generation", nm, sp)
    elif a[0] in ("stop", "terminate"): act(a[0], nm)
    elif a[0] == "submit": submit(a[1], a[2], [x for i, x in enumerate(a) if i > 0 and a[i - 1] == "--include"], sp)
    elif a[0] == "cancel": cancel()
    elif a[0] == "fetch": fetch(a[1], a[a.index("--outdir") + 1] if "--outdir" in a else None, sp)
    else: print(json.dumps(pods(), indent=1))
