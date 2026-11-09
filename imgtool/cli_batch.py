"""Lenh `batch`: doc titles.txt cua du an, tao thumbnail moi vao thu muc new/ canh thumbnail cu."""
import argparse
import json
import re
import sys
from pathlib import Path

from .compose import render
from .paths import ROOT_TEMPLATES
from .template import ensure_asset
from .cli_titles import SEP


def parse(titles_file):
    items = []
    for n, line in enumerate(titles_file.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if SEP not in line:
            sys.exit(f"{titles_file}:{n}: thieu dau ' | ' -> {line!r}")
        rel, title = line.split(SEP, 1)
        items.append((rel.strip(), title.strip()))
    return items


NUM = re.compile(r"^(\d{1,4})\s+(.+)$")


def split_number(title):
    """'001 Soy la mala...' -> ('001', 'Soy la mala...'); khong co so -> (None, title)."""
    m = NUM.match(title)
    return (m.group(1), m.group(2)) if m else (None, title)


def safe_name(s):
    return re.sub(r'[\\/:*?"<>|]', "", s).strip()[:150]


def main():
    ap = argparse.ArgumentParser(description="Tao thumbnail moi cho ca du an vao thu muc new/")
    ap.add_argument("folder", help="Thu muc goc du an (co titles.txt)")
    ap.add_argument("--template", help="Ten template; mac dinh doc 'template' trong <folder>/project.json")
    ap.add_argument("--titles", help="File titles (mac dinh <folder>/titles.txt)")
    ap.add_argument("--force", action="store_true", help="Lam lai ca anh da co trong new/")
    a = ap.parse_args()

    root = Path(a.folder).expanduser().resolve()
    tname = a.template
    pj = root / "project.json"
    if not tname and pj.exists():
        tname = json.loads(pj.read_text(encoding="utf-8")).get("template")
    if not tname:
        sys.exit(f"Can --template hoac file {pj} dang {{\"template\": \"ten_template\"}}")
    tpl = ROOT_TEMPLATES / tname
    if not (tpl / "template.json").exists():
        sys.exit(f"Khong co template '{tname}' trong {ROOT_TEMPLATES}")
    tf = Path(a.titles).expanduser() if a.titles else root / "titles.txt"
    if not tf.exists():
        sys.exit(f"Khong thay {tf} (chay: python3 -m imgtool titles \"{root}\")")
    items = parse(tf)
    if not items:
        sys.exit("titles.txt khong co dong nao")

    ensure_asset(tpl, "avatar.jpg", "avatar_prompt", "1:1", False)
    ensure_asset(tpl, "bg.jpg", "bg_prompt", "16:9", False)

    done = skipped = failed = 0
    for rel, title in items:
        old = root / rel
        num, title = split_number(title)  # so thu tu chi dung dat ten file, khong ve len anh
        name = safe_name(f"{num} {title}") if num else old.stem
        out = old.parent / "new" / f"{name}.png"
        if out.exists() and not a.force:
            skipped += 1
            continue
        out.parent.mkdir(exist_ok=True)
        try:
            render(tpl, title, out)
            print("->", out)
            done += 1
        except (Exception, SystemExit) as e:
            failed += 1
            print(f"LOI [{title}]: {e}")
    print(f"\nXong: {done} moi, {skipped} bo qua (da co), {failed} loi.")
    if failed:
        sys.exit(1)
