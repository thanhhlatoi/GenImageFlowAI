"""Goi gflow-cli (khong chinh thuc) de tao anh tren Google Flow."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}


def find_gflow():
    """Tim lenh gflow: uu tien trong cung venv dang chay script."""
    local = Path(sys.executable).parent / "gflow"
    if local.exists():
        return str(local)
    found = shutil.which("gflow")
    if found:
        return found
    sys.exit("Khong tim thay lenh 'gflow'. Hay kich hoat venv: source .venv/bin/activate")


def list_images(root):
    images_dir = Path(root) / "images"
    if not images_dir.exists():
        return set()
    return {p for p in images_dir.rglob("*") if p.suffix.lower() in IMG_EXT}


def run_gflow(prompts, out_dir, count=1, aspect=None, model=None, jitter=None):
    """Goi `gflow image t2i` MOT LAN cho tat ca prompt (chi mo browser 1 lan).

    Tra ve (exit_code, danh sach file anh moi).
    """
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [find_gflow(), "image", "t2i", *prompts, "-n", str(count), "--continue-on-error"]
    # Chay Chrome tren man hinh ao (Xvfb) de khong hien len; dat IMGTOOL_SHOW=1 de xem cua so.
    # Khong dung headless that: reCAPTCHA tu choi (403), nen van la Chrome co giao dien.
    if shutil.which("xvfb-run") and not os.environ.get("IMGTOOL_SHOW"):
        cmd = ["xvfb-run", "-a", *cmd]
    if aspect:
        cmd += ["--aspect", aspect]
    if model:
        cmd += ["--model", model]
    if jitter:
        cmd += ["--jitter", jitter]

    env = {**os.environ, "GFLOW_CLI_OUTPUT_DIR": str(out_dir)}
    before = list_images(out_dir)
    # Khong capture de thay tien trinh/loi cua gflow truc tiep tren man hinh
    code = subprocess.run(cmd, env=env).returncode
    return code, sorted(list_images(out_dir) - before)
