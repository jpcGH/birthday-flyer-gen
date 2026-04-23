import textwrap
import uuid
from datetime import datetime
from pathlib import Path

from django.conf import settings
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .forms import DEFAULT_BIRTHDAY_WISH

THEME_COLORS = {
    'royal_grace': {
        'bg_top': '#0A1B4D',
        'bg_bottom': '#4E2A6B',
        'accent': '#E0C27A',
        'accent_soft': '#F5E7C5',
        'text': '#FFFFFF',
    },
    'refuge_light': {
        'bg_top': '#F6F1E6',
        'bg_bottom': '#DECDAF',
        'accent': '#2D4E7A',
        'accent_soft': '#7C5A24',
        'text': '#1D2533',
    },
    'covenant_bloom': {
        'bg_top': '#2B0E2A',
        'bg_bottom': '#7B2D58',
        'accent': '#F1C98B',
        'accent_soft': '#FDE8C5',
        'text': '#FFF8F1',
    },
}


def _get_font(size, bold=False):
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/Library/Fonts/Arial Bold.ttf' if bold else '/Library/Fonts/Arial.ttf',
        'arialbd.ttf' if bold else 'arial.ttf',
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_vertical_gradient(size, top_hex, bottom_hex):
    w, h = size
    top = tuple(int(top_hex[i:i + 2], 16) for i in (1, 3, 5))
    bottom = tuple(int(bottom_hex[i:i + 2], 16) for i in (1, 3, 5))
    canvas = Image.new('RGB', size, top)
    draw = ImageDraw.Draw(canvas)

    for y in range(h):
        ratio = y / max(h - 1, 1)
        color = tuple(int(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        draw.line([(0, y), (w, y)], fill=color)
    return canvas


def _fit_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], []
    for word in words:
        trial = ' '.join(current + [word])
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return lines


def _format_date(date_obj):
    return datetime.strftime(date_obj, '%d %B %Y')


def generate_birthday_flyer(record, church_logo_path=None):
    theme = THEME_COLORS.get(record.theme, THEME_COLORS['royal_grace'])
    width, height = 1080, 1350

    base = _draw_vertical_gradient((width, height), theme['bg_top'], theme['bg_bottom'])
    overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    o_draw = ImageDraw.Draw(overlay)

    o_draw.ellipse((70, 90, 410, 430), fill=(255, 255, 255, 30))
    o_draw.ellipse((720, 120, 1040, 440), fill=(255, 255, 255, 22))
    o_draw.rounded_rectangle((38, 32, width - 38, height - 32), radius=36, outline=theme['accent'], width=4)
    o_draw.line((80, 245, width - 80, 245), fill=theme['accent'], width=2)
    o_draw.line((80, height - 126, width - 80, height - 126), fill=theme['accent'], width=2)

    base = Image.alpha_composite(base.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(base)

    heading_font = _get_font(76, bold=True)
    title_font = _get_font(31, bold=True)
    name_font = _get_font(60, bold=True)
    meta_font = _get_font(34)
    wish_font = _get_font(31)
    small_font = _get_font(22)

    draw.text((540, 98), 'Happy Birthday', font=heading_font, fill=theme['accent'], anchor='mm')
    draw.text((540, 156), 'Redeemed Christian Church of God', font=title_font, fill=theme['accent_soft'], anchor='mm')
    draw.text((540, 196), 'City of Refuge Parish', font=title_font, fill=theme['accent_soft'], anchor='mm')

    photo = Image.open(record.uploaded_photo.path).convert('RGB')
    photo_size = 410
    photo = photo.resize((photo_size, photo_size), Image.Resampling.LANCZOS)

    mask = Image.new('L', (photo_size, photo_size), 0)
    m_draw = ImageDraw.Draw(mask)
    m_draw.ellipse((0, 0, photo_size, photo_size), fill=255)

    ring_size = photo_size + 28
    framed = Image.new('RGBA', (ring_size, ring_size), (0, 0, 0, 0))
    f_draw = ImageDraw.Draw(framed)
    f_draw.ellipse((0, 0, ring_size, ring_size), fill=theme['accent'])
    f_draw.ellipse((10, 10, ring_size - 10, ring_size - 10), fill=theme['bg_top'])
    framed.paste(photo, (14, 14), mask)

    shadow = Image.new('RGBA', framed.size, (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.ellipse((14, 18, ring_size - 8, ring_size - 2), fill=(0, 0, 0, 130))
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))

    px = (width - ring_size) // 2
    py = 275
    base.alpha_composite(shadow, (px, py + 10))
    base.alpha_composite(framed, (px, py))

    name = record.celebrant_name.strip().upper()
    name_lines = textwrap.wrap(name, width=20)[:2]
    y_pos = 748
    for line in name_lines:
        draw.text((540, y_pos), line, font=name_font, fill=theme['text'], anchor='mm')
        y_pos += 66

    draw.text((540, y_pos + 10), _format_date(record.birthday_date), font=meta_font, fill=theme['accent'], anchor='mm')

    wish_text = (record.wish or '').strip() or DEFAULT_BIRTHDAY_WISH
    wish_lines = _fit_text(draw, wish_text, wish_font, max_width=860)[:5]

    wish_box_top = y_pos + 78
    box = Image.new('RGBA', (900, 258), (255, 255, 255, 34 if record.theme != 'refuge_light' else 70))
    box = box.filter(ImageFilter.GaussianBlur(0.5))
    base.alpha_composite(box, (90, wish_box_top - 22))

    line_y = wish_box_top
    for line in wish_lines:
        draw.text((540, line_y), line, font=wish_font, fill=theme['text'], anchor='ma')
        line_y += 44

    draw.text((540, height - 89), '...a home of grace, truth and refuge in Christ', font=small_font, fill=theme['accent_soft'], anchor='mm')
    draw.text((540, height - 62), 'RCCG City of Refuge Parish', font=small_font, fill=theme['accent'], anchor='mm')

    if church_logo_path and Path(church_logo_path).exists():
        logo = Image.open(church_logo_path).convert('RGBA').resize((105, 105), Image.Resampling.LANCZOS)
        base.alpha_composite(logo, (80, 78))

    out_dir = Path(settings.MEDIA_ROOT) / 'generated_flyers'
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f'flyer_{uuid.uuid4().hex[:12]}.png'
    output_path = out_dir / filename

    base.convert('RGB').save(output_path, 'PNG', optimize=True)

    record.generated_flyer.name = f'generated_flyers/{filename}'
    record.save(update_fields=['generated_flyer'])
    return record.generated_flyer.url
