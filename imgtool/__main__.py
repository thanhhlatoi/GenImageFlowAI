"""Diem vao duy nhat (chay tu thu muc goc du an):

    python -m imgtool make reddit_post --title "I Kicked My Sister Out..."
    python -m imgtool make reddit_post --file titles.txt     # moi dong 1 tieu de
    python -m imgtool make reddit_post --title "..." --new-bg    # hoac --new-avatar
    python -m imgtool make reddit_post --title "..." --debug     # luu tung lop de soi loi
    python -m imgtool titles "<thu muc du an>"   # tach ten thumbnail cu -> titles.txt de sua
    python -m imgtool batch "<thu muc du an>" --template reddit_post   # tao thumbnail moi vao new/
    python -m imgtool restyle "<thu muc>" --template letras_reddit   # giu thumbnail cu, chi doi nen + avatar
    python -m imgtool rewrite "<thu muc du an>" [--dry-run]   # doi tieu de bang 9router
    python -m imgtool router [--ask "xin chao"]   # kiem tra 9router (can ROUTER_KEY)
    python -m imgtool gen "a hot air balloon over Tokyo" -n 2 --aspect 16:9
    python -m imgtool gen --file prompts.txt --out ./out

Chuan bi (1 lan): gflow auth login --browser chrome
"""
import sys

from .cli_gen import main as gen
from .cli_make import main as make
from .cli_titles import main as titles
from .cli_batch import main as batch
from .cli_restyle import main as restyle
from .cli_router import main as router
from .cli_rewrite import main as rewrite

COMMANDS = {"make": make, "gen": gen, "titles": titles, "batch": batch, "restyle": restyle, "router": router, "rewrite": rewrite}

if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
    sys.exit(__doc__)

cmd = sys.argv[1]
sys.argv = [f"imgtool {cmd}", *sys.argv[2:]]  # de --help hien dung ten lenh
COMMANDS[cmd]()
