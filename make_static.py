"""
Genera 4 file HTML statici (email-ready) dai 2 presskit:
  presskit_wedding_it.html  presskit_wedding_en.html
  presskit_live_it.html     presskit_live_en.html

Trasformazioni applicate:
  - Rimozione Google Fonts CDN
  - Rimozione lang-bar e JavaScript
  - Estrazione lingua singola (ITA o ENG)
  - Risoluzione CSS variables -> valori letterali
  - Sostituzione Google Fonts -> Georgia / Arial (web-safe)
  - Embedding immagini come base64 (resize max 800px)
  - CSS inlining via premailer
"""
import base64, re, warnings
from pathlib import Path
from io import BytesIO

warnings.filterwarnings('ignore')

from PIL import Image
from bs4 import BeautifulSoup
import premailer

FOLDER = Path(r'C:\Users\Tommaso\Desktop\Nuova cartella')

WEDDING_VARS = {
    '--cream':    '#faf7f2',
    '--light':    '#f2ede4',
    '--ink':      '#1c1a17',
    '--muted':    '#5a5248',
    '--gold':     '#9b7b2f',
    '--gold-lt':  '#c9a84c',
    '--border':   '#e4ddd0',
    '--text-max': '820px',
}

LIVE_VARS = {
    '--cream':    '#f5f1ea',
    '--light':    '#ede8de',
    '--ink':      '#1c1a17',
    '--muted':    '#5a5248',
    '--acc':      '#6b2737',
    '--acc-lt':   '#9c3d52',
    '--border':   '#e0d9cf',
    '--text-max': '820px',
}


def resolve_css_vars(css_text, vars_map):
    def replace_var(m):
        name = m.group(1).strip()
        fallback = (m.group(2) or '').strip() or None
        return vars_map.get(name, fallback or m.group(0))
    for _ in range(5):
        css_text = re.sub(
            r'var\(\s*(--[\w-]+)\s*(?:,\s*([^)]+?))?\s*\)',
            replace_var, css_text
        )
    css_text = re.sub(r':root\s*\{[^}]+\}', '', css_text)
    return css_text


def img_to_b64(img_path, max_width=800):
    try:
        with Image.open(img_path) as img:
            if img.mode == 'RGBA':
                bg = Image.new('RGB', img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img = bg
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            if img.width > max_width:
                ratio = max_width / img.width
                img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
            buf = BytesIO()
            is_png = img_path.suffix.lower() == '.png'
            if is_png:
                img.save(buf, 'PNG', optimize=True)
                mime = 'image/png'
            else:
                img.save(buf, 'JPEG', quality=82, optimize=True)
                mime = 'image/jpeg'
            b64 = base64.b64encode(buf.getvalue()).decode('ascii')
            return f'data:{mime};base64,{b64}'
    except Exception as e:
        print(f'    WARN: cannot encode {img_path.name}: {e}')
        return None


def make_static(html_path, lang, vars_map, out_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # 1. Remove Google Fonts
    for tag in soup.find_all('link'):
        href = tag.get('href', '')
        if 'fonts.google' in href or 'fonts.gstatic' in href:
            tag.decompose()

    # 2. Remove lang-bar
    el = soup.find(class_='lang-bar')
    if el:
        el.decompose()

    # 3. Remove all script tags
    for s in soup.find_all('script'):
        s.decompose()

    # 4. Keep only target language, remove the other
    other = 'en' if lang == 'it' else 'it'
    for el in soup.find_all(attrs={'data-lang': other}):
        el.decompose()
    for el in soup.find_all(attrs={'data-lang': lang}):
        del el['data-lang']

    # 5. Set html lang attribute
    html_tag = soup.find('html')
    if html_tag:
        html_tag['lang'] = lang

    # 6. Resolve CSS vars + replace Google Fonts in <style>
    for style in soup.find_all('style'):
        css = style.string or ''
        css = resolve_css_vars(css, vars_map)
        css = css.replace("'Cormorant Garamond', Georgia, serif", "Georgia, 'Times New Roman', serif")
        css = css.replace("'Lato', Arial, sans-serif", "Arial, Helvetica, sans-serif")
        style.string = css

    # 7. Embed images as base64
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src.startswith('data:') or src.startswith('http'):
            continue
        img_path = FOLDER / src
        if img_path.exists():
            print(f'    encoding {src} ...')
            data_uri = img_to_b64(img_path)
            if data_uri:
                img['src'] = data_uri
        else:
            print(f'    WARN: {src} not found')

    html_str = str(soup)

    # 8. Inline CSS with premailer
    try:
        html_str = premailer.transform(html_str, remove_classes=False, strip_important=False)
        print('    CSS inlined')
    except Exception as e:
        print(f'    WARN: CSS inlining skipped ({e})')

    # 9. Fix image attributes post-premailer:
    #    - remove invalid height="auto" HTML attribute
    #    - add width="100%" for full-width images (cover-photo, sec-img-full)
    #    - add max-width:100% to inline style to prevent overflow
    soup2 = BeautifulSoup(html_str, 'html.parser')
    for img in soup2.find_all('img'):
        # Remove invalid height="auto" attribute
        if img.get('height', '') == 'auto':
            del img['height']
        # Full-width images: enforce width="100%" attribute + safe inline style
        classes = img.get('class', [])
        if isinstance(classes, str):
            classes = classes.split()
        if any(c in classes for c in ('cover-photo', 'sec-img-full')):
            img['width'] = '100%'
            existing_style = img.get('style', '')
            if 'max-width' not in existing_style:
                img['style'] = existing_style.rstrip(';') + '; max-width:100%;'
        # Logo and small images: remove width="100%" if accidentally set
        if any(c in classes for c in ('cover-logo', 'specs-logo')):
            if img.get('width') == '100%':
                del img['width']
    html_str = str(soup2)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_str)

    kb = out_path.stat().st_size / 1024
    print(f'    -> {out_path.name}  ({kb:.0f} KB)')


tasks = [
    ('presskit_wedding.html', 'wedding', WEDDING_VARS),
    ('presskit_live.html',    'live',    LIVE_VARS),
]

OUT_FOLDER = FOLDER / 'presskit_static'
OUT_FOLDER.mkdir(exist_ok=True)

for filename, name, vars_map in tasks:
    for lang in ['it', 'en']:
        print(f'\n[{name.upper()} / {lang.upper()}]')
        make_static(
            FOLDER / filename,
            lang,
            vars_map,
            OUT_FOLDER / f'presskit_{name}_{lang}.html',
        )

print('\nDone.')
