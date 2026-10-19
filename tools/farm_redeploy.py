#!/usr/bin/env python3
"""Redeploy the CPU farm's code (pipeline/cloud, Flash app "cloud", env "production") IN PLACE on the existing endpoint
exo-cpu1 - same endpoint id, same queue, no new endpoint (a plain `flash deploy` without the old .flash state provisions
a NEW endpoint, which the account worker quota of 10 refuses). docs/CLOUD_RUN.md "Redeploy".

    cd pipeline/cloud && RUNPOD_API_KEY="$(cat ~/.runpod_key)" flash build --python-version 3.12
    RUNPOD_API_KEY="$(cat ~/.runpod_key)" ~/.local/share/uv/tools/runpod-flash/bin/python tools/farm_redeploy.py deploy
    ... status                          active build, endpoint template fingerprint, executionTimeoutMs
    ... rollback <build id>             make an older build active again (+ rolling release)

What `deploy` does (the steps of `flash deploy` minus its endpoint reconcile):
  1. upload .flash/artifact.tar.gz as a new build of app "cloud"
  2. make it the active build of env "production" (workers unpack the env's active build when they boot)
  3. store the manifest on the build, with the existing endpoint id
  4. rolling release: write the new source fingerprint into the endpoint template's env (the same env var flash itself
     uses), so RunPod replaces the workers as they finish their jobs; queued jobs stay in the endpoint's queue
  5. executionTimeoutMs -> 3600000 (1 h server-side runaway limit)
Runs with the runpod-flash tool's python (it imports runpod_flash). The API key is read from the environment and never
printed; the template's own env (it holds a key) is sent back unchanged except the fingerprint.
"""
import asyncio, json, os, sys, urllib.request
from pathlib import Path

from runpod_flash.core.api.runpod import RunpodGraphQLClient
from runpod_flash.core.resources.app import FlashApp

APP, ENV, EP = "cloud", "production", "exo-cpu1"
HERE = Path(__file__).resolve().parent.parent / "pipeline" / "cloud"
EXEC_MS = 3600000


def _rest_patch(eid, body):
    req = urllib.request.Request(f"https://rest.runpod.io/v1/endpoints/{eid}", data=json.dumps(body).encode(), method="PATCH",
                                 headers={"Authorization": "Bearer " + os.environ["RUNPOD_API_KEY"].strip(),
                                          "Content-Type": "application/json", "User-Agent": "exo-farm-redeploy/1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or b"null")


async def _endpoint(c):
    d = await c._execute_graphql("query { myself { endpoints { id name templateId executionTimeoutMs workersMax } } }", {})
    eps = [e for e in d["myself"]["endpoints"] if e["name"] == EP]
    if len(eps) != 1:
        sys.exit(f"expected exactly one endpoint named {EP}, found {len(eps)}")
    return eps[0]


async def _roll(c, ep, fingerprint):
    """write the fingerprint into the endpoint template env -> RunPod rolling release onto the env's active build"""
    t = await c.get_template(ep["templateId"])
    env = [dict(key=kv["key"], value=kv["value"]) for kv in t.get("env") or []]
    old = next((kv["value"] for kv in env if kv["key"] == "_FLASH_SOURCE_FINGERPRINT"), None)
    env = [kv for kv in env if kv["key"] != "_FLASH_SOURCE_FINGERPRINT"] + [dict(key="_FLASH_SOURCE_FINGERPRINT", value=fingerprint)]
    payload = dict(id=t["id"], name=t["name"], imageName=t["imageName"], containerDiskInGb=t["containerDiskInGb"],
                   dockerArgs=t.get("dockerArgs") or "", env=env, readme=t.get("readme") or "", volumeInGb=0)
    await c.update_template(payload)
    print(f"template {t['id']}: fingerprint {str(old)[:12]} -> {fingerprint[:12]} (rolling release)")


async def status():
    app = await FlashApp.from_name(APP); env = await app.get_environment_by_name(ENV)
    async with RunpodGraphQLClient() as c:
        ep = await _endpoint(c); t = await c.get_template(ep["templateId"])
    fp = next((kv["value"] for kv in t.get("env") or [] if kv["key"] == "_FLASH_SOURCE_FINGERPRINT"), None)
    builds = await app.list_builds()
    print(f"app {APP} env {ENV}: active build {env.get('activeBuildId')}; builds: "
          + ", ".join(f"{b['id']} ({b['createdAt'][11:16]})" for b in builds))
    print(f"endpoint {EP} {ep['id']}: workersMax {ep['workersMax']}, executionTimeoutMs {ep['executionTimeoutMs']}, "
          f"template fingerprint {str(fp)[:12]}")


async def deploy():
    art = HERE / ".flash" / "artifact.tar.gz"; man = json.loads((HERE / ".flash" / "flash_manifest.json").read_text())
    if man.get("python_version") != "3.12":
        sys.exit("the build must target python 3.12 (the image's CPython): flash build --python-version 3.12")
    app = await FlashApp.from_name(APP); env = await app.get_environment_by_name(ENV); old = env.get("activeBuildId")
    async with RunpodGraphQLClient() as c:
        ep = await _endpoint(c)
    build = await app.upload_build(art); bid = build["id"]
    print(f"uploaded {art.stat().st_size / 1e6:.0f} MB as build {bid} (previous active build {old})")
    fp = man.get("source_fingerprint") or bid
    for r in man.get("resources", {}).values():
        r.setdefault("env", {})["_FLASH_SOURCE_FINGERPRINT"] = fp
    man["resources"][EP]["endpoint_id"] = ep["id"]
    man.setdefault("resources_endpoints", {})[EP] = f"https://api.runpod.ai/v2/{ep['id']}"
    await app.deploy_build_to_environment(bid, environment_name=ENV)
    await app.update_build_manifest(bid, man)
    print(f"env {ENV}: active build -> {bid}")
    async with RunpodGraphQLClient() as c:
        await _roll(c, ep, fp)
    if ep.get("executionTimeoutMs") != EXEC_MS:
        _rest_patch(ep["id"], {"executionTimeoutMs": EXEC_MS}); print(f"executionTimeoutMs {ep.get('executionTimeoutMs')} -> {EXEC_MS}")
    print(f"rollback: tools/farm_redeploy.py rollback {old}")


async def rollback(bid):
    app = await FlashApp.from_name(APP)
    await app.deploy_build_to_environment(bid, environment_name=ENV)
    async with RunpodGraphQLClient() as c:
        ep = await _endpoint(c); await _roll(c, ep, "rollback-" + bid)
    print(f"env {ENV}: active build -> {bid}")


if __name__ == "__main__":
    if not os.environ.get("RUNPOD_API_KEY"):
        sys.exit('set RUNPOD_API_KEY="$(cat ~/.runpod_key)"')
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    asyncio.run(dict(status=status, deploy=deploy)[cmd]() if cmd != "rollback" else rollback(sys.argv[2]))
