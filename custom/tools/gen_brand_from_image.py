#!/usr/bin/env python3
"""Build every 12 Armoured logo/icon asset from one badge photo.

Usage: gen_brand_from_image.py <logo_image> <custom_dir> <scratch_dir> [--white-bg]

1. Cuts the logo out of the image. Default: GrabCut + convex hull, for a convex badge photographed
   on a background. --white-bg: flood-fills the white background from the border (white inside the
   logo is kept) and un-blends the anti-aliased rim from white, for artwork on a plain white page.
2. Writes in-app SVG logos (PNG embedded; Qt's VectorImage and QtSvg both render
   embedded raster images), Android launcher/adaptive icons, Windows .ico + installer
   header, macOS .icns, Linux PNG/SVG and a Play Store icon, at the same paths, sizes
   and formats as upstream QGroundControl expects.
Needs: opencv-python, numpy, Pillow, fontTools, rsvg-convert.
"""
import base64
import io
import os
import shutil
import subprocess
import sys

import cv2
import numpy as np
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageFilter

PHOTO, CUSTOM, SCRATCH = sys.argv[1:4]
WHITE_BG = "--white-bg" in sys.argv[4:]
os.makedirs(SCRATCH, exist_ok=True)

ICON_BG = "#1C1C1C"   # adaptive icon / store icon background (charcoal)
RED = "#D82926"       # red from the 12 Armoured crest (pennants, motto scroll)
GOLD = "#E7B321"      # gold from the 12 Armoured crest (lances)
# Adaptive-icon foreground height (of 108dp): small enough that the crest's lance tips, which
# reach its corners, stay inside the 66dp safe circle on round-icon launchers.
ADAPTIVE_FILL = 0.48 if WHITE_BG else 0.60
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def out(path):
    p = os.path.join(CUSTOM, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


# ---------------------------------------------------------------- 1. cut out the logo
img = cv2.imread(PHOTO)
h, w = img.shape[:2]


def cut_white_background():
    """Logo on plain white: (cutout RGBA, single-color silhouette RGBA)."""
    f = img.astype(np.float32)
    whiteish = f.min(axis=2) >= 232
    n, lab = cv2.connectedComponents(whiteish.astype(np.uint8), connectivity=4)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fg = ~np.isin(lab, list(border))
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg.astype(np.uint8), connectivity=8)
    keep = np.zeros(n, bool)
    keep[1:] = st[1:, 4] > 2000                  # drops page specks such as edge lines
    fg = keep[lab]
    # Rim pixels (within 3 px of the background) are blended with white: un-blend them.
    dist = cv2.distanceTransform(fg.astype(np.uint8), cv2.DIST_L2, 3)
    band = fg & (dist <= 3)
    alpha = fg.astype(np.float32)
    alpha[band] = np.clip((255 - f.min(axis=2)[band]) / 255.0 * 1.6, 0, 1)
    a3 = np.maximum(alpha, 1e-3)[..., None]
    color = np.where(band[..., None], np.clip((f - (1 - a3) * 255) / a3, 0, 255), f)
    rgba = np.dstack([cv2.cvtColor(color.astype(np.uint8), cv2.COLOR_BGR2RGB), (alpha * 255).astype(np.uint8)])
    ys, xs = np.where(alpha > 0.02)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    # Silhouette: the logo shape with its interior white (numerals, lettering, pennant halves) as holes.
    holes = whiteish & fg & (dist > 3)
    holes = cv2.morphologyEx(holes.astype(np.uint8) * 255, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(holes)
    big = np.zeros(n, bool)
    big[1:] = st[1:, 4] >= 150
    sil_a = (alpha * 255).astype(np.uint8)
    sil_a[big[lab]] = 0
    sil = np.zeros((h, w, 4), np.uint8)
    sil[:, :, :3] = 255
    sil[:, :, 3] = sil_a
    return Image.fromarray(rgba).crop(box), Image.fromarray(sil).crop(box)


def cut_badge_photo():
    """Convex badge photographed on a background: (cutout RGBA, single-color silhouette RGBA)."""
    h, w = img.shape[:2]
    gc = np.zeros((h, w), np.uint8)
    cv2.grabCut(img, gc, (8, 4, w - 16, h - 12), np.zeros((1, 65)), np.zeros((1, 65)), 6, cv2.GC_INIT_WITH_RECT)
    fg = np.where((gc == 1) | (gc == 3), 255, 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg)
    fg = ((lab == 1 + np.argmax(st[1:, 4])) * 255).astype(np.uint8)
    cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    hull = cv2.convexHull(max(cnts, key=cv2.contourArea))
    mask = np.zeros((h, w), np.uint8)
    cv2.fillPoly(mask, [hull], 255)
    mask = cv2.erode(mask, np.ones((5, 5), np.uint8))          # trim the photo's edge shadow
    mask = cv2.GaussianBlur(mask, (5, 5), 0)                    # soft anti-aliased edge
    x, y, bw, bh = cv2.boundingRect(hull)


    rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    rgba[:, :, 3] = mask
    badge = Image.fromarray(rgba).crop((x, y, x + bw, y + bh))  # full-res cutout
    badge.save(f"{SCRATCH}/badge_cutout.png")

    # Single-color silhouette for QGCLogoWhite (tinted by QGCColoredImage): keep the
    # bronze metal (frame, banner, stag head), drop the red/white field.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    H, S, V = hsv[:, :, 0].astype(int), hsv[:, :, 1].astype(int), hsv[:, :, 2].astype(int)
    metal = ((H >= 8) & (H <= 32) & (S >= 45) & (V >= 45)).astype(np.uint8) * 255
    metal = cv2.morphologyEx(metal, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    metal = cv2.morphologyEx(metal, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    inner = cv2.erode(mask, np.ones((3, 3), np.uint8))
    # The name banner (bronze text on bronze) segments noisily: make it a solid band down to
    # the first row where the red field takes over.
    red = ((H <= 6) | (H >= 170)) & (S >= 120)
    red_rows = np.where(red.sum(axis=1) > 0.25 * w)[0]
    if len(red_rows):
        metal[: red_rows[0] - 4, :] = 255
    # Solid outer frame (its engraved pattern also segments noisily).
    frame = cv2.subtract(inner, cv2.erode(inner, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(0.085 * bw) * 2 + 1,) * 2)))
    metal = cv2.bitwise_or(metal, frame)
    metal = cv2.bitwise_and(metal, inner)
    # Drop specks and fill pinholes.
    n, lab, st, _ = cv2.connectedComponentsWithStats(metal)
    keep = np.zeros(n, bool)
    keep[1:] = st[1:, 4] >= 400
    metal = (keep[lab] * 255).astype(np.uint8)
    holes = cv2.bitwise_and(cv2.bitwise_not(metal), inner)
    n, lab, st, _ = cv2.connectedComponentsWithStats(holes)
    small = np.zeros(n, bool)
    small[1:] = st[1:, 4] < 250
    metal[small[lab]] = 255
    sil = np.zeros((h, w, 4), np.uint8)
    sil[:, :, :3] = 255
    sil[:, :, 3] = cv2.GaussianBlur(metal, (3, 3), 0)
    silhouette = Image.fromarray(sil).crop((x, y, x + bw, y + bh))
    silhouette.save(f"{SCRATCH}/badge_silhouette.png")
    return badge, silhouette


badge, silhouette = cut_white_background() if WHITE_BG else cut_badge_photo()
badge.save(f"{SCRATCH}/logo_cutout.png")
silhouette.save(f"{SCRATCH}/logo_silhouette.png")


def fit(im, box_w, box_h):
    """Badge scaled to fit box_w x box_h, aspect kept."""
    s = min(box_w / im.width, box_h / im.height)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


def square(size, fill=0.94, bg=None, src=badge):
    """Badge centered on a size x size canvas, its height `fill` of the canvas."""
    canvas = Image.new("RGBA", (size, size), bg or (0, 0, 0, 0))
    b = fit(src, size * fill, size * fill)
    canvas.alpha_composite(b, ((size - b.width) // 2, (size - b.height) // 2))
    return canvas


def b64png(im):
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def svg_with_image(im, size, view=None, extra_before="", place=None):
    """SVG wrapping an embedded PNG. `place` = (x, y, w, h) in viewBox units."""
    view = view or f"0 0 {size} {size}"
    px, py, pw, ph = place or (0, 0, size, size)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{size}" height="{size}" viewBox="{view}">\n{extra_before}'
            f'<image x="{px}" y="{py}" width="{pw}" height="{ph}" preserveAspectRatio="xMidYMid meet" '
            f'xlink:href="data:image/png;base64,{b64png(im)}"/>\n</svg>\n')


def write(path, text):
    with open(out(path), "w") as f:
        f.write(text)


# ---------------------------------------------------------------- 2. in-app logos
# Embedded at 384 px tall: sharp on the toolbar (~2 text lines) at 3x DPI, small file.
write("res/Images/QGCLogoFull.svg", svg_with_image(square(384, 1.0), 384))
write("res/Images/QGCLogoWhite.svg", svg_with_image(square(384, 1.0, src=silhouette), 384))

# GCS heading marker: upstream arrow geometry (72x72, points up), charcoal with a gold rim (a red
# fill would swallow the crest's red), logo inside.
arrow_badge = fit(badge, 96, 96)
bx_h = 26.0
bx_w = bx_h * badge.width / badge.height
write("res/Images/QGCLogoArrow.svg", (
    '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
    'width="72" height="72" viewBox="0 0 72 72">\n'
    f'<path fill="{ICON_BG}" d="M36 0 0 72l36-18 36 18z"/>\n'
    f'<path fill="{GOLD}" fill-rule="evenodd" d="M36 0 0 72l36-18 36 18zM36 4.47 3.3 69.9 36 53.55 68.7 69.9z"/>\n'
    f'<image x="{36 - bx_w / 2:.2f}" y="25" width="{bx_w:.2f}" height="{bx_h}" preserveAspectRatio="xMidYMid meet" '
    f'xlink:href="data:image/png;base64,{b64png(arrow_badge)}"/>\n</svg>\n'))

# Startup zoom animation (qml/TwelveASplash.qml) scales the badge to ~half the screen height,
# so it gets its own high-resolution copy.
fit(badge, 1000, 768).save(out("res/Images/SplashBadge.png"), optimize=True)

# ---------------------------------------------------------------- 3. Android
for dens, px in {"ldpi": 48, "mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 144}.items():
    square(px, 0.96).save(out(f"android/res/mipmap-{dens}/ic_launcher.png"))
    square(px, 0.96).save(out(f"android/res/drawable-{dens}/icon.png"))   # also the splash icon

# Adaptive icon (Android 8+): 108dp canvas, art inside the central 66dp circle.
for dens, scale in {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}.items():
    square(round(108 * scale), ADAPTIVE_FILL).save(out(f"android/res/drawable-{dens}/ic_launcher_foreground_img.png"))
# Upstream's adaptive icon points at @drawable/ic_launcher_foreground (a vector there);
# here it becomes a bitmap wrapper around the PNGs above, so upstream XML stays untouched.
write("android/res/drawable/ic_launcher_foreground.xml",
      '<?xml version="1.0" encoding="utf-8"?>\n'
      '<!-- 12 Armoured adaptive icon foreground: the badge PNG (drawable-*dpi/ic_launcher_foreground_img.png),\n'
      '     generated by tools/gen_brand_from_image.py. -->\n'
      '<bitmap xmlns:android="http://schemas.android.com/apk/res/android"\n'
      '    android:src="@drawable/ic_launcher_foreground_img"\n'
      '    android:gravity="fill"\n'
      '    android:filter="true" />\n')
write("android/res/values/ic_launcher_colors.xml",
      '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
      f'    <color name="ic_launcher_background">{ICON_BG}</color>\n</resources>\n')

# ---------------------------------------------------------------- 4. desktop / store
square(512, 0.90, bg=ICON_BG).convert("RGB").save(out("res/icons/store_512x512.png"))
square(256, 0.96).save(out("deploy/linux/TwelveArmoured_256.png"))
write("deploy/linux/TwelveArmoured.svg", svg_with_image(square(512, 0.96), 512))

ico_app = [square(s, 0.96) for s in (16, 32, 48, 64, 128, 256)]
ico_app[-1].save(out("res/icons/qgroundcontrol.ico"), sizes=[i.size for i in ico_app], append_images=ico_app[:-1])
ico_win = [square(s, 0.96) for s in (16, 20, 24, 32, 40, 48, 64)]
ico_win[-1].save(out("deploy/windows/WindowsQGC.ico"), sizes=[i.size for i in ico_win], append_images=ico_win[:-1])
icns = [square(s, 0.92) for s in (16, 32, 64, 128, 256, 512, 1024)]
icns[-1].save(out("deploy/macos/TwelveArmoured.icns"), append_images=icns[:-1])


# Windows installer header 150x57: badge + "12 ARMOURED".
def text_path(text, cx, cy, height, max_width, font=TTFont(FONT)):
    gs, cmap = font.getGlyphSet(), font.getBestCmap()
    cap = getattr(font["OS/2"], "sCapHeight", 0) or 1493
    names = [cmap[ord(c)] for c in text]
    s = height / cap
    width = sum(gs[n].width for n in names) * s
    if width > max_width:
        s *= max_width / width
        height *= max_width / width
        width = max_width
    xx, pen = cx - width / 2, SVGPathPen(gs)
    for n in names:
        gs[n].draw(TransformPen(pen, (s, 0, 0, -s, xx, cy + height / 2)))
        xx += gs[n].width * s
    return pen.getCommands()


hdr_badge = fit(badge, 60, 49)
hdr_svg = f"{SCRATCH}/installheader.svg"
with open(hdr_svg, "w") as f:
    f.write('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            'width="150" height="57" viewBox="0 0 150 57">\n<rect width="150" height="57" fill="#FFFFFF"/>\n'
            f'<image x="6" y="4" width="{hdr_badge.width}" height="{hdr_badge.height}" '
            f'xlink:href="data:image/png;base64,{b64png(hdr_badge)}"/>\n'
            f'<path fill="{RED}" d="{text_path("12 ARMOURED", 97, 28.5, 9, 90)}"/>\n</svg>\n')
subprocess.run(["rsvg-convert", "-w", "150", "-h", "57", hdr_svg, "-o", f"{SCRATCH}/installheader.png"], check=True)
Image.open(f"{SCRATCH}/installheader.png").convert("RGB").save(out("deploy/windows/installheader.bmp"))

# Keep an unmodified copy of the source image with the overlay so the set can be regenerated.
shutil.copyfile(PHOTO, out("tools/logo_source" + os.path.splitext(PHOTO)[1].lower()))
print("ok", badge.size)
