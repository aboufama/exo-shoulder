"""the model's own frozen protocol (fit Bench(60,160) fast, freeze, wear Bench(110,360) exact), box end_extra opened to the rule bound 8"""
import os, sys, json, importlib.util
os.environ["CB_FOLD_MARGIN"] = "5.0"
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
spec = importlib.util.spec_from_file_location("dcm", os.path.join(REPO, "docs/concepts/models/deltoid-crest-j3-3r.py"))
DC = importlib.util.module_from_spec(spec); sys.modules["dcm"] = DC; spec.loader.exec_module(DC)
DC.BOX["end_extra"] = (0.0, 8.0)
DC.frozen(dict(DC.PARAMS, **json.loads(sys.argv[1])), sys.argv[2])
