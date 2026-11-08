"""Dung anh bai dang: nen AI * (khung trang + chu den), avatar tron dan de len.

Cac buoc (moi buoc 1 ham, de debug rieng):
    text_layer   -> khung trang + dau trang + tieu de (chu den)
    background   -> anh nen da lam sang
    circle_crop  -> avatar cat tron
    render       -> ghep 3 lop tren, luu file
"""
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

from .template import load_cfg

FONTS = Path(__file__).parent / "fonts"


def wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and draw.textlength(trial, font=font) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def fit_title(draw, title, cfg):
    """Chon co chu lon nhat ma tieu de van vua khung. Tra ve (font, cac dong, co chu)."""
    x0, y0, x1, y1 = cfg["title_box"]
    for size in range(cfg["font_max"], cfg["font_min"] - 1, -2):
        font = ImageFont.truetype(str(FONTS / cfg["font"]), size)
        lines = wrap(draw, title, font, x1 - x0)
        if len(lines) * size * cfg["line_height"] <= y1 - y0:
            return font, lines, size
    raise ValueError(f"Tieu de qua dai, khong vua khung ngay ca o co chu {cfg['font_min']}px")


def text_layer(tpl, cfg, title):
    """Khung trang: dau trang cat tu anh mau + tieu de chu den."""
    canvas = Image.new("RGB", tuple(cfg["size"]), "white")
    d = ImageDraw.Draw(canvas)

    box = tuple(cfg["header_patch"])
    canvas.paste(Image.open(tpl / "original.jpg").convert("RGB").crop(box), box[:2])

    font, lines, size = fit_title(d, title, cfg)
    x0, y0, x1, y1 = cfg["title_box"]
    pitch = size * cfg["line_height"]
    top = (y0 + y1 - pitch * len(lines)) / 2  # can giua theo chieu doc
    for i, line in enumerate(lines):
        d.text(((x0 + x1) / 2, top + pitch * (i + 0.5)), line, font=font, fill="black", anchor="mm")
    return canvas


def background(path, size):
    """Nen: lam sang them 35% de chu den van doc duoc."""
    bg = Image.open(path).convert("RGB").resize(size)
    return Image.blend(bg, Image.new("RGB", size, "white"), 0.35)


def circle_crop(path, radius):
    """Cat vuong o giua roi cat tron. Tra ve (anh, mask)."""
    av = Image.open(path).convert("RGB")
    s = min(av.size)
    av = av.crop(((av.width - s) // 2, (av.height - s) // 2, (av.width + s) // 2, (av.height + s) // 2))
    av = av.resize((2 * radius, 2 * radius))
    mask = Image.new("L", (8 * radius, 8 * radius), 0)  # ve to roi thu nho cho mep muot
    ImageDraw.Draw(mask).ellipse((0, 0, 8 * radius - 1, 8 * radius - 1), fill=255)
    return av, mask.resize((2 * radius, 2 * radius), Image.LANCZOS)


def render(tpl_dir, title, out_path, avatar="avatar.jpg", bg="bg.jpg", debug=False):
    tpl = Path(tpl_dir)
    cfg = load_cfg(tpl)
    text = text_layer(tpl, cfg, title)
    back = background(tpl / bg, tuple(cfg["size"]))
    res = ImageChops.multiply(text, back)

    cx, cy = cfg["avatar_center"]
    r = cfg["avatar_radius"]
    av, mask = circle_crop(tpl / avatar, r)
    res.paste(av, (cx - r, cy - r), mask)

    out_path = Path(out_path)
    if debug:  # luu tung lop de xem lop nao sai
        dbg = out_path.parent / "_debug"
        dbg.mkdir(exist_ok=True)
        text.save(dbg / "1_text_layer.png")
        back.save(dbg / "2_background.png")
    res.save(out_path)
