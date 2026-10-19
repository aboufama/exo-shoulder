"""Build the dense per-frame skin maps (.cache/maps_s1.pt) in independent frame chunks, so the build can run in parallel
(the CPU farm: tools/cloud_run.py batch) and be merged. Same function and inputs as tools/build_maps.py (band_impl
build_frame_maps on every pose of pipeline/conformal/band_poses.b64, spacing 0.8, CPU float32 -> float16 maps).

    python3 tools/build_maps_chunk.py chunk <a> <b> <out.pt>          frames a..b-1 -> out.pt (dict r1, r1c, r2c, cs; float16)
    python3 tools/build_maps_chunk.py merge <out maps_s1.pt> <chunk.pt>...   concatenate in frame order (checks coverage)
    python3 tools/build_maps_chunk.py compare <a.pt> <b.pt>             max abs difference per map on the common frames
"""
import os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); GPU = os.path.join(ROOT, "pipeline", "conformal", "gpu")
sys.path.insert(0, GPU); sys.path.insert(0, os.path.join(ROOT, "pipeline", "avg"))


def chunk(a, b, out):
    import torch
    out = os.path.abspath(out); os.makedirs(os.path.dirname(out), exist_ok=True)   # before the chdir below
    torch.set_num_threads(int(os.environ.get("THREADS", 2)))
    os.chdir(GPU); import band_impl as BI
    P = BI.load_poses(open(os.path.join(ROOT, "pipeline", "conformal", "band_poses.b64")).read(), "cpu")
    POSE = P["POSE"]; b = min(b, len(POSE)); t0 = time.time()
    M = BI.build_frame_maps(POSE[a:b], "cpu", spacing=0.8)
    torch.save({"a": a, "b": b, "n": len(POSE), **{k: v.cpu() for k, v in M.items()}}, out)
    print(f"frames {a}..{b - 1} of {len(POSE)} in {time.time() - t0:.0f}s -> {out}", flush=True)


def merge(out, parts):
    import torch
    C = sorted((torch.load(p) for p in parts), key=lambda z: z["a"])
    n = C[0]["n"]; edges = [(z["a"], z["b"]) for z in C]
    assert edges[0][0] == 0 and edges[-1][1] == n and all(e1[1] == e2[0] for e1, e2 in zip(edges, edges[1:])), f"gaps/overlaps: {edges}"
    M = {k: torch.cat([z[k] for z in C], 0) for k in ("r1", "r1c", "r2c", "cs")}
    torch.save(M, out); print(f"merged {len(C)} chunks, {n} frames -> {out} ({os.path.getsize(out) / 1e6:.0f} MB)")


def compare(pa, pb):
    import torch
    A, B = torch.load(pa), torch.load(pb); lo = max(A.get("a", 0), B.get("a", 0)); hi = min(A.get("b", 10 ** 9), B.get("b", 10 ** 9))
    for k in ("r1", "r1c", "r2c", "cs"):
        x = A[k][lo - A.get("a", 0):hi - A.get("a", 0)].float(); y = B[k][lo - B.get("a", 0):hi - B.get("a", 0)].float()
        fin = torch.isfinite(x) & torch.isfinite(y); d = (x - y).abs()[fin]
        print(f"{k}: frames {lo}..{hi - 1}, max |diff| {float(d.max()) if d.numel() else 0:.4f}, finite mismatch {int((torch.isfinite(x) != torch.isfinite(y)).sum())}")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "chunk": chunk(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif c == "merge": merge(sys.argv[2], sys.argv[3:])
    elif c == "compare": compare(sys.argv[2], sys.argv[3])
