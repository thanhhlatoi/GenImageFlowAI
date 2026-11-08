"""Lenh `make.py`: tao anh theo template (xem make.py)."""
import argparse
import re
import sys
from pathlib import Path

from .compose import render
from .lines import read_lines
from .template import ensure_asset

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser(description="Tao anh bai dang theo template")
    ap.add_argument("template", help="Ten folder trong templates/")
    ap.add_argument("--title")
    ap.add_argument("--file", help="File txt, moi dong 1 tieu de (mac dinh: templates/<ten>/titles.txt)")
    ap.add_argument("--new-avatar", action="store_true", help="Tao lai avatar bang gflow")
    ap.add_argument("--new-bg", action="store_true", help="Tao lai nen bang gflow")
    ap.add_argument("--debug", action="store_true", help="Luu tung lop vao out/_debug")
    a = ap.parse_args()

    tpl = ROOT / "templates" / a.template
    if not (tpl / "template.json").exists():
        sys.exit(f"Khong co template '{a.template}' trong {ROOT / 'templates'}")
    if a.file:
        titles = read_lines(a.file)
    elif a.title:
        titles = [a.title]
    else:
        default = tpl / "titles.txt"
        if not default.exists():
            ap.error(f"Can --title hoac --file, hoac tao {default}")
        print(f"Doc tieu de tu {default}")
        titles = read_lines(default)
    if not titles:
        sys.exit("Khong co tieu de nao de chay")

    ensure_asset(tpl, "avatar.jpg", "avatar_prompt", "1:1", a.new_avatar)
    ensure_asset(tpl, "bg.jpg", "bg_prompt", "16:9", a.new_bg)

    out = tpl / "out"
    out.mkdir(exist_ok=True)
    for i, t in enumerate(titles, 1):
        slug = re.sub(r"[^a-z0-9]+", "-", t.lower())[:40].strip("-")
        path = out / f"{i:02d}_{slug}.png"
        render(tpl, t, path, debug=a.debug)
        print("->", path)
