"""Lenh `rewrite`: doi tieu de trong titles.txt bang model qua 9router, theo rewrite_prompt.txt cua folder chu de."""
import argparse
import json
import re
import sys
from pathlib import Path

from . import router
from .cli_titles import SEP

PROMPT_FILE = "rewrite_prompt.txt"
OLD = "# cu: "
CHUNK = 20

FORMAT = (
    "\n\nFORMATO DE RESPUESTA: recibirás una lista JSON de títulos. Responde SOLO con una lista JSON "
    "de strings, la misma cantidad y el mismo orden, sin explicaciones ni bloques de código."
)


def find_prompt(folder):
    """Tim rewrite_prompt.txt o folder hien tai, roi len cac folder cha."""
    for d in [folder, *folder.parents]:
        f = d / PROMPT_FILE
        if f.exists():
            return f
    return None


def ask(system, titles, model):
    out = router.chat(json.dumps(titles, ensure_ascii=False), system=system + FORMAT, model=model, timeout=300)
    out = re.sub(r"^```(?:json)?|```$", "", out.strip(), flags=re.M).strip()
    arr = json.loads(out)
    if not isinstance(arr, list) or len(arr) != len(titles) or not all(isinstance(x, str) and x.strip() for x in arr):
        raise ValueError(f"model tra ve {len(arr) if isinstance(arr, list) else '?'} muc, can {len(titles)}")
    return [x.strip() for x in arr]


def main():
    ap = argparse.ArgumentParser(description="Doi tieu de trong titles.txt bang 9router theo rewrite_prompt.txt")
    ap.add_argument("folder", help="Thu muc du an (co titles.txt)")
    ap.add_argument("--titles", help="File titles (mac dinh <folder>/titles.txt)")
    ap.add_argument("--prompt", help="File prompt (mac dinh tim rewrite_prompt.txt o folder va cac folder cha)")
    ap.add_argument("--model", help="Ghi de ROUTER_MODEL")
    ap.add_argument("--force", action="store_true", help="Lam lai ca dong da viet lai")
    ap.add_argument("--out", help="Ghi ra file moi nay (vd titles_new.txt), KHONG sua titles.txt")
    ap.add_argument("--number", action="store_true", help="Them so thu tu 001, 002... truoc moi tieu de moi")
    ap.add_argument("--dry-run", action="store_true", help="Chi in ket qua, khong ghi file")
    a = ap.parse_args()

    root = Path(a.folder).expanduser().resolve()
    tf = Path(a.titles).expanduser() if a.titles else root / "titles.txt"
    if not tf.exists():
        sys.exit(f"Khong thay {tf} (chay: python3 -m imgtool titles \"{root}\")")
    pf = Path(a.prompt).expanduser() if a.prompt else find_prompt(root)
    if not pf or not pf.exists():
        sys.exit(f"Khong thay {PROMPT_FILE} trong {root} hoac cac folder cha")
    system = pf.read_text(encoding="utf-8").strip()

    # Doc file, giu nguyen cac dong khac; dong "x | tieu de" ngay sau "# cu: ..." la da viet lai.
    lines = tf.read_text(encoding="utf-8").splitlines()
    todo = []  # (index dong, tieu de cu)
    for i, line in enumerate(lines):
        if not line.strip() or line.lstrip().startswith("#") or SEP not in line:
            continue
        rewritten = i > 0 and lines[i - 1].startswith(OLD)
        if rewritten and not a.force:
            continue
        old = lines[i - 1][len(OLD):] if rewritten else line.split(SEP, 1)[1].strip()
        todo.append((i, old))
    if not todo:
        sys.exit("Khong co dong nao can viet lai (them --force de lam lai)")

    print(f"Prompt: {pf}\nModel : {a.model or 'ROUTER_MODEL'}\nCan viet lai: {len(todo)} tieu de")
    new = {}
    try:
        for s in range(0, len(todo), CHUNK):
            part = todo[s:s + CHUNK]
            res = ask(system, [t for _, t in part], a.model)
            for (i, old), t in zip(part, res):
                new[i] = t
                print(f"  {old}\n  -> {t}")
    except (router.RouterError, ValueError) as e:
        print(f"LOI: {e}")
        if not new:
            sys.exit(1)
        print("Chi luu cac dong da xong.")

    if a.dry_run:
        return
    if a.out:
        of = Path(a.out).expanduser()
        if not of.is_absolute():
            of = root / of
        out, n = ["# Tieu de moi (tao boi rewrite). Dong '# cu' la ban goc."], 0
        for i, line in enumerate(lines):
            if i in new:
                n += 1
                t = f"{n:03d} {new[i]}" if a.number else new[i]
                out += [f"{OLD}{dict(todo)[i]}", f"{line.split(SEP, 1)[0]}{SEP}{t}"]
        of.write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"\nDa ghi {n} tieu de moi vao {of} (titles.txt giu nguyen)")
        return
    out, olds = [], dict(todo)
    for i, line in enumerate(lines):
        if i in new:
            rel = line.split(SEP, 1)[0]
            if not (i > 0 and lines[i - 1].startswith(OLD)):
                out.append(f"{OLD}{olds[i]}")
            out.append(f"{rel}{SEP}{new[i]}")
        elif i + 1 in new and line.startswith(OLD):
            continue  # --force: bo dong '# cu' cu, se ghi lai dong moi
        else:
            out.append(line)
    tf.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"\nDa ghi {len(new)} tieu de moi vao {tf} (ban cu giu o dong '# cu:')")
