"""Lenh `restyle`: GIU NGUYEN thumbnail cu (chu, khung), chi doi nen va avatar.

Nen = phan ngoai khung bo goc; avatar = hinh tron trong khung. Anh ra: <thu muc anh cu>/new/<ten cu>.jpg
"""
import argparse
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from .gflow import IMG_EXT, run_gflow
from .paths import ROOT_TEMPLATES
from .template import load_cfg

SS = 4  # ve mask to gap 4 lan roi thu nho cho mep muot


def card_mask(size, box, radius):
    w, h = size
    m = Image.new("L", (w * SS, h * SS), 0)
    x0, y0, x1, y1 = (v * SS for v in box)
    ImageDraw.Draw(m).rounded_rectangle((x0, y0, x1, y1), radius=radius * SS, fill=255)
    return m.resize(size, Image.LANCZOS)


def cover(img, size):
    """Phong to anh cho kin khung roi cat giua."""
    s = max(size[0] / img.width, size[1] / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    l, t = (img.width - size[0]) // 2, (img.height - size[1]) // 2
    return img.crop((l, t, l + size[0], t + size[1]))


def circle(path, r, zoom=1.0):
    av = Image.open(path).convert("RGB")
    s = round(min(av.size) * zoom)  # zoom < 1: cat sat vao giua de hinh to hon trong vong tron
    av = av.crop(((av.width - s) // 2, (av.height - s) // 2, (av.width + s) // 2, (av.height + s) // 2)).resize((2 * r, 2 * r), Image.LANCZOS)
    m = Image.new("L", (8 * r, 8 * r), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 8 * r - 1, 8 * r - 1), fill=255)
    return av, m.resize((2 * r, 2 * r), Image.LANCZOS)


def restyle_one(old_path, out_path, bg, av, av_mask, cfg, mask):
    old = Image.open(old_path).convert("RGB")
    if old.size != tuple(cfg["size"]):
        old = old.resize(tuple(cfg["size"]), Image.LANCZOS)
    res = Image.composite(old, bg, mask)  # trong khung giu anh cu, ngoai khung la nen moi
    cx, cy = cfg["avatar_center"]
    r = cfg["avatar_radius"]
    res.paste(Image.new("RGB", (2 * r, 2 * r), "white"), (cx - r, cy - r), av_mask)  # xoa avatar cu
    res.paste(av, (cx - r, cy - r), av_mask)
    res.save(out_path, quality=95)


def ensure_avatar(tpl, cfg, force):
    path = tpl / "avatar.jpg"
    if path.exists() and not force:
        return
    # i2i (tao tu anh mau) chua dung duoc voi tai khoan Flow nay (gflow #799) -> tao tu prompt mo ta avatar cu
    code, files = run_gflow([cfg["avatar_prompt"]], tpl / "_gen", aspect="1:1")
    if not files:
        sys.exit(f"Khong tao duoc avatar (gflow ma loi {code})")
    path.write_bytes(files[-1].read_bytes())


def ensure_bg(tpl, cfg, force):
    path = tpl / "bg.jpg"
    if path.exists() and not force:
        return
    code, files = run_gflow([cfg["bg_prompt"]], tpl / "_gen", aspect="16:9")
    if not files:
        sys.exit(f"Khong tao duoc nen (gflow ma loi {code})")
    path.write_bytes(files[-1].read_bytes())


def bg_for(tpl, cfg, stem, idx, force):
    """Nen rieng cho 1 thumbnail: luu templates/<ten>/bgs/<ten anh>.jpg, chua co thi tao (1 lan goi gflow/anh)."""
    path = tpl / "bgs" / f"{stem}.jpg"
    if path.exists() and not force:
        return path
    themes = cfg["bg_themes"]
    prompt = f"{cfg['bg_prompt']}, {themes[idx % len(themes)]}"
    code, files = run_gflow([prompt], tpl / "_gen", aspect="16:9")
    if not files:
        sys.exit(f"Khong tao duoc nen cho '{stem}' (gflow ma loi {code})")
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(files[-1].read_bytes())
    return path


def main():
    ap = argparse.ArgumentParser(description="Giu thumbnail cu, chi doi nen + avatar, luu vao new/")
    ap.add_argument("folder", help="Thu muc chua thumbnail cu (tim ca thu muc con)")
    ap.add_argument("--template", required=True, help="Ten template (co card_box, avatar_prompt, bg_prompt)")
    ap.add_argument("-n", "--limit", type=int, help="Chi lam n anh dau tien")
    ap.add_argument("--new-avatar", action="store_true", help="Tao lai avatar")
    ap.add_argument("--new-bg", action="store_true", help="Tao lai nen")
    ap.add_argument("--bg-each", action="store_true", help="Moi thumbnail 1 nen rieng (theo bg_themes trong template.json)")
    ap.add_argument("--new-bg-each", action="store_true", help="Voi --bg-each: tao lai nen rieng da co")
    ap.add_argument("--force", action="store_true", help="Bo qua danh dau .restyle_done, lam lai tat ca")
    a = ap.parse_args()

    root = Path(a.folder).expanduser().resolve()
    tpl = ROOT_TEMPLATES / a.template
    cfg = load_cfg(tpl)
    imgs = sorted(p for p in root.rglob("*") if p.suffix.lower() in IMG_EXT and p.is_file()
                  and "new" not in p.relative_to(root).parts[:-1] and not p.name.startswith("000"))
    if a.limit:
        imgs = imgs[:a.limit]
    if not imgs:
        sys.exit(f"Khong thay thumbnail nao trong {root}")

    ensure_avatar(tpl, cfg, a.new_avatar)
    if not a.bg_each:
        ensure_bg(tpl, cfg, a.new_bg)

    size = tuple(cfg["size"])
    bg = None if a.bg_each else cover(Image.open(tpl / "bg.jpg").convert("RGB"), size)
    mask = card_mask(size, cfg["card_box"], cfg["card_radius"])
    r = cfg["avatar_radius"]
    av, av_mask = circle(tpl / "avatar.jpg", r, cfg.get("avatar_zoom", 1.0))

    # Danh dau anh da lam: <thu muc>/.restyle_done (moi dong 1 duong dan thumbnail cu). Co trong do hoac da co file ra thi bo qua.
    mark = root / ".restyle_done"
    marked = set(mark.read_text(encoding="utf-8").splitlines()) if mark.exists() else set()
    done = skipped = 0
    for i, p in enumerate(imgs):
        out = p.parent / "new" / f"{p.stem}.jpg"
        rel = p.relative_to(root).as_posix()
        if (rel in marked or out.exists()) and not a.force:
            skipped += 1
            continue
        out.parent.mkdir(exist_ok=True)
        pbg = cover(Image.open(bg_for(tpl, cfg, p.stem, i, a.new_bg_each)).convert("RGB"), size) if a.bg_each else bg
        restyle_one(p, out, pbg, av, av_mask, cfg, mask)
        print("->", out)
        with mark.open("a", encoding="utf-8") as f:  # ghi ngay sau moi anh, dung giua chung van nho
            f.write(rel + "\n")
        marked.add(rel)
        done += 1
    print(f"\nXong: {done} moi, {skipped} bo qua (da co).")
