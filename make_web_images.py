"""
Genera versioni web-ottimizzate di tutte le immagini del sito.
Output in img/:
  - *_web.jpg   max 1400px wide, quality 80  (full-width: hero, cover, sezione)
  - *_thumb.jpg max 600px  wide, quality 75  (card thumbnail)

Le immagini originali non vengono toccate (rimangono usabili da make_static.py).
"""
from pathlib import Path
from PIL import Image

BASE = Path(__file__).parent
OUT  = BASE / 'img'
OUT.mkdir(exist_ok=True)


def resize_save(src: Path, out: Path, max_w: int, quality: int):
    with Image.open(src) as img:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        if img.width > max_w:
            ratio = max_w / img.width
            img = img.resize((max_w, int(img.height * ratio)), Image.LANCZOS)
        img.save(out, 'JPEG', quality=quality, optimize=True)
    orig_kb = src.stat().st_size // 1024
    new_kb  = out.stat().st_size // 1024
    print(f'  {src.name:40s} {orig_kb:>5} KB  →  {out.name} ({new_kb} KB)')


# ── Full-width (hero, cover, sezioni) ─────────────────────────────
WEB = [
    'hero.jpg',
    'extracted_wed_p1_img0.jpeg',
    'extracted_wed_p3_img0.jpeg',
    'extracted_wed_p4_img0.jpeg',
    'extracted_live_p1_img0.jpeg',
    'extracted_live_p2_img0.jpeg',
    'extracted_live_p3_img0.jpeg',
    'extracted_live_p4_img0.jpeg',
    'extracted_live_p4_img1.jpeg',
    'extracted_live_p5_img1.jpeg',
]

# ── Card thumbnail (visibili a ~350px) ────────────────────────────
THUMB = [
    'extracted_wed_p1_img0.jpeg',
    'extracted_live_p1_img0.jpeg',
]

print('=== Web images (max 1400px, q80) ===')
for name in WEB:
    src = BASE / name
    resize_save(src, OUT / f'{Path(name).stem}_web.jpg', max_w=1400, quality=80)

print('\n=== Thumb images (max 600px, q75) ===')
for name in THUMB:
    src = BASE / name
    resize_save(src, OUT / f'{Path(name).stem}_thumb.jpg', max_w=600, quality=75)

print('\nDone.')
