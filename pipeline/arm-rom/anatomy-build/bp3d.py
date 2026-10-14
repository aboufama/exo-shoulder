"""BodyParts3D (CC BY-SA 2.1 JP, DBCLS) loader: curated bones / muscles / skin for the exo body model."""
import os, re
import numpy as np

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "anatomy-src")
OBJ = os.path.join(SRC, "obj", "BodyParts3D_3.0_obj_99")

EXCLUDE = re.compile(r"hairs|eyebrow|lobule|precuneus|septum pellucidum|midbrain|tuber cinereum|stria terminalis|fossa|gyrus|nucleus|ventricle|colliculus|arter|vein|aorta|vena|sinus|thalam|hippocamp|amygdala|capsule|corpus|commissure|fornix|cerebel|cerebr|pons|medulla|spinal cord|canal|foramen|gland|kidney|lung|heart|atri|liver|stomach|duoden|jejun|ileum|colon|rect|appendix|bladder|esophag|trache|bronch|thymus|spleen|pancrea|gallbladder|penis|testis|epididym|deferent|prostat|tooth|gingiva|pharyn|papillary|valve|coronary|cardiac|habenula|hypothal|pineal|mammillary|geniculate|chiasm|optic|nerve|plexus|taenia|lamina|aqueduct|peduncle|insula|claustr|putamen|globus|caudate|choroid|brachium of|seminal|ureter|urethra|ovary|uter|vagin|tongue|lens|cornea|eyeball|intervertebral disk|diaphragm|gyri|lobe|sulcus|cortex|white matter|tract of|ventral|dorsal|fissure|ganglion|cord|limb of|retinaculum|interosseous membrane|ligament|sphincter|duct|hymen|labial part", re.I)
BONE = re.compile(r"\b(bone|vertebra|rib|sternum|manubrium of sternum|xiphoid process|clavicle|scapula|humerus|radius|ulna|femur|tibia|fibula|patella|calcaneus|talus|phalanx|scaphoid|lunate|triquetrum|pisiform|trapezium|trapezoid|capitate|hamate|sacrum|coccyx|atlas|axis|ethmoid|maxilla|mandible|vomer|inferior nasal concha)\b|metacarpal bone|metatarsal bone|cuneiform bone|cuboid bone|navicular bone|body of sternum|vertebra$", re.I)
CARTILAGE = re.compile(r"cartilage|meniscus|tendon|aponeurosis|iliotibial", re.I)


def names():
    out = {}
    for line in open(os.path.join(SRC, "parts_list_e.txt"), encoding="utf-8", errors="replace"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2: out[p[0].strip('"')] = p[1].strip('"')
    return out


def classify(name):
    if name == "skin": return "skin"
    if EXCLUDE.search(name) and not BONE.search(name): return None
    if BONE.search(name) and not re.search(r"muscle|levator|depressor", name, re.I): return "bone"
    if CARTILAGE.search(name): return "cartilage"
    if EXCLUDE.search(name): return None
    if name in ("ear",): return None
    return "muscle"


def load_obj(fid):
    V, F = [], []
    with open(os.path.join(OBJ, fid + ".obj"), errors="replace") as f:
        for line in f:
            if line.startswith("v "): V.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("f "):
                idx = [int(t.split("/")[0]) for t in line.split()[1:]]
                for k in range(1, len(idx) - 1): F.append([idx[0], idx[k], idx[k + 1]])
    return np.array(V, float), np.array(F, int) - 1


def catalogue():
    nm = names(); out = []
    for f in sorted(os.listdir(OBJ)):
        if not f.endswith(".obj"): continue
        fid = f[:-4]; n = nm.get(fid, fid); c = classify(n)
        if c: out.append((fid, n, c))
    return out
