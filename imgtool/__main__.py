"""Diem vao duy nhat (chay tu thu muc goc du an):

    python -m imgtool make reddit_post --title "I Kicked My Sister Out..."
    python -m imgtool make reddit_post --file titles.txt     # moi dong 1 tieu de
    python -m imgtool make reddit_post --title "..." --new-bg    # hoac --new-avatar
    python -m imgtool make reddit_post --title "..." --debug     # luu tung lop de soi loi
    python -m imgtool gen "a hot air balloon over Tokyo" -n 2 --aspect 16:9
    python -m imgtool gen --file prompts.txt --out ./out

Chuan bi (1 lan): gflow auth login --browser chrome
"""
import sys

from .cli_gen import main as gen
from .cli_make import main as make

COMMANDS = {"make": make, "gen": gen}

if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
    sys.exit(__doc__)

cmd = sys.argv[1]
sys.argv = [f"imgtool {cmd}", *sys.argv[2:]]  # de --help hien dung ten lenh
COMMANDS[cmd]()
