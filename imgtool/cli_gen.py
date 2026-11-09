"""Lenh `genImage.py`: tao anh thuan tu prompt, khong qua template."""
import argparse
import sys
from pathlib import Path

from .gflow import run_gflow
from .lines import read_lines
from .paths import OUTPUT_ROOT


def main():
    ap = argparse.ArgumentParser(description="Tao anh Google Flow qua gflow-cli")
    ap.add_argument("prompt", nargs="?", help="Prompt mo ta anh")
    ap.add_argument("--file", help="File txt, moi dong 1 prompt (dong bat dau bang # bi bo qua)")
    ap.add_argument("-n", "--count", type=int, default=1, help="So anh moi prompt")
    ap.add_argument("--aspect", help="Ti le, vd 16:9, 9:16, 1:1")
    ap.add_argument("--model", help="Ten model (xem: gflow image t2i --help)")
    ap.add_argument("--out", default=str(OUTPUT_ROOT / "genImage"), help="Thu muc luu ket qua")
    ap.add_argument("--jitter", help="Nghi giua cac prompt, vd 3-8 (giay); mac dinh cua gflow")
    a = ap.parse_args()

    if a.file:
        prompts = read_lines(a.file)
    elif a.prompt:
        prompts = [a.prompt]
    else:
        ap.error("Can truyen prompt hoac --file")

    code, files = run_gflow(prompts, a.out, a.count, a.aspect, a.model, a.jitter)
    for f in files:
        print("  ->", f)
    print(f"\nXong: {len(files)} anh moi cho {len(prompts)} prompt. Anh o: {Path(a.out).resolve()}/images")
    if code != 0:
        sys.exit(f"gflow tra ve ma loi {code}: co the mot so prompt that bai (xem log o tren)")
