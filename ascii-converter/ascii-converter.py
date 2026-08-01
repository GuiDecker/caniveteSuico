import argparse
import datetime
import html
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Glyphs ordered from darkest to lightest.
DENSITY = (r'$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|'
           '()1{}[]?-_+~<>i!lI;:,"^`\'.            ')

FONT_CANDIDATES = (
    '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf',
    '/usr/share/fonts/TTF/DejaVuSansMono.ttf',
)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'output')
GALLERY_DATA = os.path.join(PROJECT_DIR, 'gallery.json')
GALLERY_PAGE = os.path.join(PROJECT_DIR, 'gallery.html')


def to_ascii(img_name, width, contrast):
    """Convert an image file into a list of ASCII art rows."""
    density = DENSITY[:-11 + contrast]
    n = len(density)

    img = Image.open(img_name)
    img = img.convert('L')

    orig_width, orig_height = img.size
    r = orig_height / orig_width
    # Glyphs are taller than they are wide, so halve the height to keep the
    # original aspect ratio.
    height = int(width * r * 0.5)
    img = img.resize((width, height), Image.LANCZOS)

    arr = np.array(img)
    rows = []
    for i in range(height):
        row = []
        for j in range(width):
            p = arr[i, j]
            k = int(np.floor(p / 256 * n))
            row.append(density[n - 1 - k])
        rows.append(''.join(row))
    return rows


def load_font(size, font_path=None):
    """Load a monospace TrueType font at the given size."""
    candidates = [font_path] if font_path else list(FONT_CANDIDATES)
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    raise SystemExit(
        'No monospace font found. Pass one explicitly with --font '
        '(e.g. --font /usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf).')


def render(rows, out_name, font_size, font_path=None,
           fg='black', bg='white', padding=20):
    """Render ASCII art rows to an image file."""
    font = load_font(font_size, font_path)

    cell_width = int(round(font.getlength('M')))
    ascent, descent = font.getmetrics()
    cell_height = ascent + descent

    img_width = cell_width * max(len(row) for row in rows) + 2 * padding
    img_height = cell_height * len(rows) + 2 * padding

    img = Image.new('RGB', (img_width, img_height), bg)
    draw = ImageDraw.Draw(img)
    for i, row in enumerate(rows):
        # Drawn glyph by glyph to keep the grid aligned even if the font falls
        # back to a different width for some character.
        y = padding + i * cell_height
        for j, char in enumerate(row):
            if char == ' ':
                continue
            draw.text((padding + j * cell_width, y), char, font=font, fill=fg)

    save_kwargs = {}
    if out_name.lower().endswith(('.jpg', '.jpeg')):
        save_kwargs['quality'] = 95
        save_kwargs['subsampling'] = 0
    img.save(out_name, **save_kwargs)
    return img.size


def record_entry(entry):
    """Append an entry to the gallery index, newest first."""
    try:
        with open(GALLERY_DATA) as f:
            entries = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        entries = []

    # Re-running a conversion updates its card instead of duplicating it.
    entries = [e for e in entries if e.get('image') != entry['image']]
    entries.insert(0, entry)

    with open(GALLERY_DATA, 'w') as f:
        json.dump(entries, f, indent=2)
    return entries


def build_gallery(entries):
    """Write the gallery page from the recorded entries."""
    if entries:
        cards = '\n'.join(card_html(e) for e in entries)
    else:
        cards = '<p class="empty">No art yet. Run the converter with -o.</p>'

    with open(GALLERY_PAGE, 'w') as f:
        f.write(GALLERY_TEMPLATE.format(
            count=len(entries),
            generated=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            cards=cards))


def card_html(entry):
    """Render one gallery card."""
    e = {k: html.escape(str(v)) for k, v in entry.items()}
    text_link = ''
    if entry.get('text'):
        text_link = f' &middot; <a href="{e["text"]}" download>.txt</a>'
    return f'''    <figure class="card">
      <a href="{e['image']}" target="_blank">
        <img src="{e['image']}" alt="ASCII art from {e['source']}" loading="lazy">
      </a>
      <figcaption>
        <strong>{e['source']}</strong>
        <span class="meta">{e['width']} cols &middot; {e['size']} &middot; {e['created']}</span>
        <span class="meta"><a href="{e['image']}" download>image</a>{text_link}</span>
      </figcaption>
    </figure>'''


GALLERY_TEMPLATE = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ASCII Art Gallery</title>
<style>
  :root {{
    --bg: #ffffff; --fg: #1a1a1a; --muted: #6b6b6b;
    --card: #fafafa; --border: #e3e3e3;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #16161a; --fg: #ececec; --muted: #9a9a9a;
      --card: #1e1e24; --border: #2e2e36;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 2.5rem 1.5rem; background: var(--bg); color: var(--fg);
    font: 15px/1.5 ui-sans-serif, system-ui, -apple-system, sans-serif;
  }}
  header {{ max-width: 1200px; margin: 0 auto 2rem; }}
  h1 {{ margin: 0 0 .25rem; font-size: 1.6rem; letter-spacing: -.02em; }}
  .sub {{ color: var(--muted); font-size: .875rem; }}
  .grid {{
    max-width: 1200px; margin: 0 auto; display: grid; gap: 1.5rem;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  }}
  .card {{
    margin: 0; background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; overflow: hidden;
  }}
  .card img {{
    display: block; width: 100%; height: 260px; object-fit: contain;
    background: #fff; padding: .5rem;
  }}
  figcaption {{
    padding: .75rem .9rem; display: flex; flex-direction: column; gap: .2rem;
    border-top: 1px solid var(--border);
  }}
  figcaption strong {{ font-size: .9rem; word-break: break-all; }}
  .meta {{ color: var(--muted); font-size: .78rem; }}
  a {{ color: inherit; }}
  .meta a {{ text-decoration: underline; }}
  .empty {{ color: var(--muted); max-width: 1200px; margin: 0 auto; }}
</style>
</head>
<body>
<header>
  <h1>ASCII Art Gallery</h1>
  <p class="sub">{count} piece(s) &middot; updated {generated}</p>
</header>
<div class="grid">
{cards}
</div>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(
        description='Convert an image into ASCII art.')
    parser.add_argument('image', help='path to the source image')
    parser.add_argument('width', nargs='?', type=int, default=100,
                        help='width of the ASCII art in characters '
                             '(default: 100)')
    parser.add_argument('-o', '--output', nargs='?', const='',
                        help='save the ASCII art as an image instead of '
                             'printing it, and add it to the gallery. Give a '
                             'path, or pass the flag bare to save into '
                             'output/ (.png recommended)')
    parser.add_argument('-t', '--text', action='store_true',
                        help='also save the raw .txt alongside the image, so '
                             'the characters stay copy-pasteable')
    parser.add_argument('--no-gallery', action='store_true',
                        help='skip updating gallery.html for this run')
    parser.add_argument('--font-size', type=int, default=16,
                        help='font size in pixels when saving an image; '
                             'higher means a larger, sharper result '
                             '(default: 16)')
    parser.add_argument('--font',
                        help='path to a monospace .ttf to use when saving')
    parser.add_argument('--contrast', type=int, default=10,
                        choices=range(-10, 11), metavar='[-10-10]',
                        help='contrast of the glyph ramp (default: 10)')
    parser.add_argument('--fg', default='black',
                        help='text colour when saving (default: black)')
    parser.add_argument('--bg', default='white',
                        help='background colour when saving (default: white)')
    args = parser.parse_args()

    if args.width < 1:
        parser.error('width must be at least 1')

    try:
        rows = to_ascii(args.image, args.width, args.contrast)
    except FileNotFoundError:
        raise SystemExit(f'No such image: {args.image}')
    except OSError as exc:
        raise SystemExit(f'Could not read {args.image}: {exc}')

    if args.output is None:
        for row in rows:
            print(row)
        return

    source = os.path.basename(args.image)
    stem = os.path.splitext(source)[0]

    out_name = args.output
    if not out_name:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_name = os.path.join(OUTPUT_DIR, f'{stem}-ascii.png')
    else:
        parent = os.path.dirname(os.path.abspath(out_name))
        os.makedirs(parent, exist_ok=True)

    size = render(rows, out_name, args.font_size, args.font, args.fg, args.bg)
    print(f'Saved {out_name} ({size[0]}x{size[1]})', file=sys.stderr)

    text_name = None
    if args.text:
        text_name = os.path.splitext(out_name)[0] + '.txt'
        with open(text_name, 'w') as f:
            f.write('\n'.join(rows) + '\n')
        print(f'Saved {text_name}', file=sys.stderr)

    if args.no_gallery:
        return

    def relative(path):
        return os.path.relpath(os.path.abspath(path), PROJECT_DIR)

    entries = record_entry({
        'source': source,
        'image': relative(out_name),
        'text': relative(text_name) if text_name else None,
        'width': args.width,
        'size': f'{size[0]}x{size[1]}',
        'created': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
    })
    build_gallery(entries)
    print(f'Gallery updated: {GALLERY_PAGE} ({len(entries)} piece(s))',
          file=sys.stderr)


if __name__ == '__main__':
    main()
