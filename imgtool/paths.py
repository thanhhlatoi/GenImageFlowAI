"""Thu muc luu anh: mac dinh ~/Documents/NasSynology/GenImageFlowAI (doi bang IMGTOOL_OUT)."""
import os
from pathlib import Path

OUTPUT_ROOT = Path(os.environ.get("IMGTOOL_OUT") or Path.home() / "Documents" / "NasSynology" / "GenImageFlowAI")

ROOT_TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
