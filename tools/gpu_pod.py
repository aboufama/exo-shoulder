#!/usr/bin/env python3
"""The exo-gpu-bench RunPod POD (outside the serverless worker quota) - stdlib only, the API key is never printed.

    python3 tools/gpu_pod.py create [--gpu "NVIDIA RTX 2000 Ada Generation"]   start the pod (secure EU-RO-1 + the farm volume)
    python3 tools/gpu_pod.py status                                           its state, $/h, uptime
    python3 tools/gpu_pod.py stop | terminate                                 stop (keeps the container disk) / terminate
    python3 tools/gpu_pod.py submit <script.sh> <job name> [--include PATH]... drop a job (+ files under exo-farm/gpu/code/)
    python3 tools/gpu_pod.py fetch <job name> [--outdir DIR]                  print its log (+ bring out/<job name>/ back)

How work reaches it: no public port. The pod mounts the farm's private network volume exo-farm-cas at /workspace and runs,
one at a time, the job scripts that farm jobs (tools/cloud_run.py, authenticated by our RunPod key) drop in
exo-farm/gpu/queue/*.sh; each job's log goes to exo-farm/gpu/out/<job>.log. After 30 min with no job it stops itself
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
         "if [ -n \"$j\" ]; then b=$(basename $j .sh); mv $j $G/done/$b.sh; "
         "(cd $G && timeout 4h bash $G/done/$b.sh > $G/out/$b.log 2>&1; echo \"rc=$?\" >> $G/out/$b.log; touch $G/out/$b.done); idle=0; "
         "else sleep 5; idle=$((idle+5)); fi; "
         "if [ $idle -ge 1800 ]; then echo \"$(date -u +%FT%TZ) idle-stop\" >> $G/pod.log; runpodctl stop pod $RUNPOD_POD_ID; sleep 600; fi; done")


def pods():
    return [p for p in G.gql("query { myself { pods { id name desiredStatus costPerHr uptimeSeconds: lastStatusChange "
                             "machine { gpuDisplayName } } } }")["myself"]["pods"] if p["name"].startswith("exo-gpu")]


def create(gpu):
    if any(p["name"] == NAME and p["desiredStatus"] == "RUNNING" for p in pods()): print("already running"); return
    q = ('mutation { podFindAndDeployOnDemand(input: { cloudType: SECURE, gpuCount: 1, gpuTypeId: %s, name: "%s", '
         'imageName: "%s", containerDiskInGb: 30, volumeInGb: 0, networkVolumeId: "%s", dataCenterId: "EU-RO-1", '
         'volumeMountPath: "/workspace", startSsh: false, dockerArgs: %s }) { id desiredStatus costPerHr machine { gpuDisplayName } } }'
         % (json.dumps(gpu), NAME, IMAGE, VOLUME, json.dumps("bash -c " + json.dumps(SPOOL))))
    print(json.dumps(G.gql(q)["podFindAndDeployOnDemand"]))


def act(what):
    for p in pods():
        if p["name"] != NAME: continue
        m = "podStop" if what == "stop" else "podTerminate"
        G.gql('mutation { %s(input: {podId: "%s"}) %s }' % (m, p["id"], "{ id desiredStatus }" if m == "podStop" else ""))
        print(what, p["id"])


def submit(script, name, include=()):
    """drop a job script (and files it needs, under exo-farm/gpu/code/) on the volume through one farm job"""
    import subprocess
    inc = sum((["--include", x] for x in [script, *include]), [])
    cmd = ("set -e; V=/runpod-volume/exo-farm/gpu; mkdir -p $V/code $V/queue; "
           + "".join(f"mkdir -p $V/code/$(dirname {x}); cp -r {x} $V/code/{x}; " for x in include)
           + f"cp {script} $V/queue/{name}.sh.tmp; mv $V/queue/{name}.sh.tmp $V/queue/{name}.sh; ls -la $V/queue $V/out | tail -8; tail -3 $V/pod.log")
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "cloud_run.py"), "run", "--no-base", "--no-bench-cache",
                    "--timeout", "600", *inc, "--", cmd], check=False)


def fetch(name, outdir=None):
    """print a job's log (and bring exo-farm/gpu/out/<name>/ back under outdir) through one farm job"""
    import subprocess
    cmd = (f"V=/runpod-volume/exo-farm/gpu; tail -3 $V/pod.log; ls $V/out | tail -5; echo ---; tail -c 20000 $V/out/{name}.log; "
           f"mkdir -p gpu_out; [ -d $V/out/{name} ] && cp -r $V/out/{name} gpu_out/ || true")
    extra = ["--out", f"gpu_out/{name}/*", "--outdir", outdir] if outdir else []
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "cloud_run.py"), "run", "--no-base", "--no-bench-cache",
                    "--timeout", "600", *extra, "--", cmd], check=False)


if __name__ == "__main__":
    a = sys.argv[1:] or ["status"]
    if a[0] == "create": create(a[a.index("--gpu") + 1] if "--gpu" in a else "NVIDIA RTX 2000 Ada Generation")
    elif a[0] in ("stop", "terminate"): act(a[0])
    elif a[0] == "submit": submit(a[1], a[2], [x for i, x in enumerate(a) if i > 0 and a[i - 1] == "--include"])
    elif a[0] == "fetch": fetch(a[1], a[a.index("--outdir") + 1] if "--outdir" in a else None)
    else: print(json.dumps(pods(), indent=1))
