"""Doc template.json va tao avatar/nen (1 lan) cho 1 folder template."""
import json
import sys
from pathlib import Path

from .gflow import run_gflow


def load_cfg(tpl_dir):
    return json.loads((Path(tpl_dir) / "template.json").read_text(encoding="utf-8"))


def ensure_asset(tpl_dir, name, prompt_key, aspect, force=False):
    """Neu chua co file `name` trong template (hoac force) thi tao bang gflow."""
    tpl = Path(tpl_dir)
    path = tpl / name
    if path.exists() and not force:
        return
    code, files = run_gflow([load_cfg(tpl)[prompt_key]], tpl / "_gen", aspect=aspect)
    if not files:
        sys.exit(f"Khong tao duoc {name} (gflow ma loi {code}). Thu doi '{prompt_key}' trong template.json")
    path.write_bytes(files[-1].read_bytes())
