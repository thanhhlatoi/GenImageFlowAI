"""Lenh `titles`: quet thumbnail cu, lay ten file lam tieu de, ghi ra 1 file de sua."""
import argparse
import sys
from pathlib import Path

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}
SEP = " | "


def main():
    ap = argparse.ArgumentParser(description="Tach tieu de tu ten thumbnail ra file titles.txt")
    ap.add_argument("folder", help="Thu muc goc can quet (vd ES1 404 Cronicas Redditeras)")
    ap.add_argument("--out", help="File ket qua (mac dinh: <folder>/titles.txt)")
    ap.add_argument("--force", action="store_true", help="Ghi de file da co")
    a = ap.parse_args()

    root = Path(a.folder).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"Khong thay thu muc: {root}")
    out = Path(a.out).expanduser() if a.out else root / "titles.txt"
    if out.exists() and not a.force:
        sys.exit(f"{out} da ton tai (them --force de ghi de, se mat noi dung ban da sua)")

    imgs = sorted(p for p in root.rglob("*") if p.suffix.lower() in IMG_EXT and p.is_file() and "new" not in p.relative_to(root).parts[:-1])
    lines = [
        "# Moi dong: duong dan thumbnail cu | tieu de. Sua phan SAU dau | , dung dong vao phan truoc.",
        "# Dong bat dau bang # bi bo qua. Xoa dong neu khong muon lam anh do.",
    ]
    lines += [f"{p.relative_to(root).as_posix()}{SEP}{p.stem}" for p in imgs]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Tim thay {len(imgs)} thumbnail -> {out}")
