"""Doc file txt: moi dong 1 muc, bo dong trong va dong bat dau bang #."""
import sys
from pathlib import Path


def read_lines(path):
    p = Path(path)
    if not p.exists():
        sys.exit(f"Khong thay file: {p.resolve()}")
    return [l.strip() for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.lstrip().startswith("#")]
