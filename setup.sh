#!/usr/bin/env bash
# Cai dat 1 lan: xvfb (he thong) + venv + thu vien Python. Chay: bash setup.sh
set -e
cd "$(dirname "$0")"

command -v xvfb-run >/dev/null || sudo apt install -y xvfb
[ -d .venv ] || python3 -m venv .venv
.venv/bin/python -m pip --version >/dev/null 2>&1 || .venv/bin/python -m ensurepip -q
.venv/bin/python -m pip install -q -r requirements.txt

echo "Cai xong. Buoc tiep theo (chi lan dau): .venv/bin/gflow auth login --browser chrome"
