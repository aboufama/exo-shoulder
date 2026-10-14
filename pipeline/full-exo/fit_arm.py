"""Map the user's arm (RIGHT ARM SUBASSY, CAD frame) onto the average body (rest pose, thorax frame, origin = GH):
exo elbow axis on the body's transepicondylar axis, 55.7 mm lateral of the elbow centre as in the CAD; upper-arm
parts (BOTTOM, TOP) with the bar along the humerus projected into the bar plane; forearm parts (MIDDLE, forearm cuff)
along the forearm at the body's rest flexion."""
import json, base64, numpy as np
from scipy.spatial import cKDTree
J = json.load(open("../avg/body_mesh.json")); L = J["landmarks"]
def dec(p): return np.frombuffer(base64.b64decode(p["pos"]), np.int16).reshape(-1, 3) / 10.0
SKIN = dec([p for p in J["parts"] if p["cls"] == "skin"][0]); KD = cKDTree(SKIN)
EL = np.array(L["elbow"]); EA = np.array(L["elbow_axis"]); EA /= np.linalg.norm(EA)
hup = -EL / np.linalg.norm(EL)                                          # up the humerus (elbow -> GH)
UH = np.array(L["ulnar_head"]); fdir = UH - EL; fdir /= np.linalg.norm(fdir)
E = json.load(open("../arm-rom/arm_rom.json"))["elbow"]; Fr = json.load(open("bottom_frame.json"))
C_cad, ax_cad, u_cad, fd_cad = (np.array(x) for x in (E["centre"], Fr["ax"], Fr["u"], E["forearm_dir"]))
OFF = 55.7                                                               # exo elbow pivot lateral of the elbow centre (CAD)
C_b = EL + OFF * EA
def frame(a, b):                                                         # orthonormal (a, b_perp, a x b)
    b = b - (b @ a) * a; b /= np.linalg.norm(b); return np.c_[a, b, np.cross(a, b)]
u_b = hup - (hup @ EA) * EA; u_b /= np.linalg.norm(u_b)
R_up = frame(EA, u_b) @ frame(ax_cad, u_cad).T                         # CAD -> body, upper-arm group
f_b = fdir - (fdir @ EA) * EA; f_b /= np.linalg.norm(f_b)
R_fo = frame(EA, f_b) @ frame(ax_cad, fd_cad - (fd_cad @ ax_cad) * ax_cad).T   # forearm group at the body's rest flexion
def to_body(P, grp): R = R_up if grp == "up" else R_fo; return (np.asarray(P) - C_cad) @ R.T + C_b
def skin_dist(P):
    d, i = KD.query(P); return d
if __name__ == "__main__":
    print("bar flare vs humerus", np.degrees(np.arcsin(abs(hup @ EA))).round(1), "deg")
    for s in (0, 50, 100, 124, 150, 200, 250, 300):
        p = C_b + s * u_b - 2.8 * EA                                     # bar skin-side face (channel opening)
        print(f"  bar s={s:3d}: {np.linalg.norm(p - (p @ hup) * hup):5.1f} mm off the arm axis, skin {skin_dist(p[None])[0]:5.1f} mm away")
    from load_arm import load
    parts = load(); CU = [p for p in parts if p[0] == "FOREARM CUFF"][0][2]
    vs, _ = CU.tessellate(0.3); P = to_body(np.array([[v.x, v.y, v.z] for v in vs]), "fore")
    o = to_body(np.array([-488.6, 123.1, 225.7]), "fore"); a = R_fo @ (fd_cad / np.linalg.norm(fd_cad))
    q = P - o; r = np.linalg.norm(q - np.outer(q @ a, a), axis=1); inner = np.abs(r - 49.0) < 0.3
    d = skin_dist(P[inner]); print(f"forearm cuff inner surface to skin: min {d.min():.1f} mean {d.mean():.1f} max {d.max():.1f} mm")
    # forearm skin radius around the cuff axis at its mid-length
    json.dump(dict(R_up=R_up.tolist(), R_fo=R_fo.tolist(), C_cad=C_cad.tolist(), C_b=C_b.tolist(), u_b=u_b.tolist(), EA=EA.tolist()), open("arm_fit.json", "w"))
