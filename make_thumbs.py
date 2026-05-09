"""
Download YouTube maxresdefault thumbnails and composite the official
YouTube play button (red rounded rect + white triangle) onto each one.
Saves results as JPEG in the repo root.
"""
import math
import requests
from io import BytesIO
from PIL import Image, ImageDraw

VIDEOS = {
    "thumb_live_main":             "7cPGLhehUpI",
    "thumb_live_dicitincello":     "Sdd9V_xn_rY",
    "thumb_live_indifferentemente": "hBHLMDIlMtY",
    "thumb_live_maruzzella":       "wZiZEGY-0bE",
    # Niuri Te Sule
    "thumb_nts_sternatia":         "VwqRA_xXvwA",
    "thumb_nts_novello1":          "n6PVBn8_4fM",
    "thumb_nts_novello2":          "dhrcsLyCbls",
}

def download_thumbnail(video_id: str) -> Image.Image:
    for quality in ("maxresdefault", "hqdefault"):
        url = f"https://i.ytimg.com/vi/{video_id}/{quality}.jpg"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            img = Image.open(BytesIO(r.content)).convert("RGB")
            # maxresdefault placeholder is 120x90 – skip it
            if img.width >= 480:
                print(f"  {video_id}: downloaded {quality} ({img.width}x{img.height})")
                return img
    raise RuntimeError(f"Could not download thumbnail for {video_id}")


def draw_play_button(thumb: Image.Image) -> Image.Image:
    """Composite a YouTube-style play button centred on the thumbnail."""
    w, h = thumb.size
    out = thumb.convert("RGBA")

    # Button size: ~15 % of width, 16:9 → 9:6.36 proportion matches YT (68x48)
    btn_w = max(68, int(w * 0.12))
    btn_h = int(btn_w * 48 / 68)
    radius = int(btn_w * 0.17)         # ~12 px at 68px width

    overlay = Image.new("RGBA", (btn_w, btn_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Red rounded rectangle (semi-transparent like YouTube does on hover)
    draw.rounded_rectangle(
        [0, 0, btn_w - 1, btn_h - 1],
        radius=radius,
        fill=(255, 0, 0, 230),
    )

    # White right-pointing triangle, centred
    cx, cy = btn_w // 2, btn_h // 2
    tri_h = int(btn_h * 0.45)
    tri_w = int(tri_h * 0.9)
    offset_x = int(btn_w * 0.05)   # slight right offset so it looks centred optically
    pts = [
        (cx - tri_w // 2 + offset_x, cy - tri_h // 2),
        (cx - tri_w // 2 + offset_x, cy + tri_h // 2),
        (cx + tri_w // 2 + offset_x + tri_w // 4, cy),
    ]
    draw.polygon(pts, fill=(255, 255, 255, 255))

    # Paste centred
    x = (w - btn_w) // 2
    y = (h - btn_h) // 2
    out.paste(overlay, (x, y), overlay)

    return out.convert("RGB")


import os
base = os.path.dirname(os.path.abspath(__file__))

for name, vid_id in VIDEOS.items():
    print(f"\nProcessing {name} ({vid_id}) …")
    try:
        thumb = download_thumbnail(vid_id)
        composited = draw_play_button(thumb)
        out_path = os.path.join(base, f"{name}.jpg")
        composited.save(out_path, "JPEG", quality=92)
        print(f"  saved → {out_path}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\nDone.")
