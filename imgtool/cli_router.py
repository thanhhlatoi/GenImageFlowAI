"""Lenh `router`: kiem tra ket noi 9router, liet ke model, hoac gui thu 1 cau."""
import argparse
import sys

from . import router


def main():
    ap = argparse.ArgumentParser(description="Kiem tra ket noi 9router")
    ap.add_argument("--ask", help="Gui thu 1 cau hoi den ROUTER_MODEL (hoac --model)")
    ap.add_argument("--model", help="Ghi de ROUTER_MODEL")
    a = ap.parse_args()
    try:
        print(f"9router: {router.URL}")
        ms = router.models()
        print(f"Ket noi OK, {len(ms)} model:")
        for m in ms:
            print("  ", m)
        if a.ask:
            print("\n" + router.chat(a.ask, model=a.model))
    except router.RouterError as e:
        sys.exit(f"LOI: {e}")
