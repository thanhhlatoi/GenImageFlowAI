"""Chay: .venv/bin/python tests/test_compose.py  (khong can gflow/mang)."""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PIL import Image

from imgtool.compose import render

TPL = ROOT / "templates" / "reddit_post"

with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / "a.png"
    render(TPL, "A short title", out, debug=True)
    assert Image.open(out).size == (1280, 720)
    assert (Path(tmp) / "_debug" / "1_text_layer.png").exists()

    try:
        render(TPL, "word " * 300, out)
        raise SystemExit("FAIL: tieu de qua dai phai bao loi")
    except ValueError:
        pass
print("OK")
