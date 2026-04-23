import textwrap
import uuid
from datetime import datetime
from pathlib import Path

from django.conf import settings
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .forms import DEFAULT_BIRTHDAY_WISH

THEME_COLORS = {
    'royal_gold': {'bg_top': '#0E1E44', 'bg_bottom': '#6E4B13', 'accent': '#D9B56D', 'text': '#FFFFFF'},
    'purple_grace': {'bg_top': '#24113A', 'bg_bottom': '#5C3573', 'accent': '#E0C37E', 'text': '#FFFFFF'},
    'burgundy_joy': {'bg_top': '#3A0E1C', 'bg_bottom': '#7F2342', 'accent': '#F3D7A3', 'text': '#FFF8F0'},
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


def generate_birthday_flyer(record, church_logo_path=None):
    theme = THEME_COLORS.get(record.theme, THEME_COLORS['royal_gold'])
    width, height = 1080, 1350

    base = _draw_vertical_gradient((width, height), theme['bg_top'], theme['bg_bottom'])
    overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    o_draw = ImageDraw.Draw(overlay)

    # Soft glowing circles for a premium celebratory look.
    o_draw.ellipse((60, 50, 420, 410), fill=(255, 255, 255, 28))
    o_draw.ellipse((700, 150, 1050, 500), fill=(255, 255, 255, 22))
    o_draw.rectangle((45, 40, width - 45, height - 40), outline=theme['accent'], width=4)

    base = Image.alpha_composite(base.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(base)

    heading_font = _get_font(78, bold=True)
    title_font = _get_font(34, bold=True)
    name_font = _get_font(62, bold=True)
    meta_font = _get_font(34)
    wish_font = _get_font(31)
    small_font = _get_font(24)

    draw.text((540, 95), 'Happy Birthday', font=heading_font, fill=theme['accent'], anchor='mm')
    draw.text((540, 165), 'Redeemed Christian Church of God', font=title_font, fill='white', anchor='mm')
    draw.text((540, 208), 'City of Refuge Parish', font=title_font, fill='white', anchor='mm')

    photo = Image.open(record.uploaded_photo.path).convert('RGB')
    photo_size = 420
    photo = photo.resize((photo_size, photo_size), Image.Resampling.LANCZOS)
    mask = Image.new('L', (photo_size, photo_size), 0)
    m_draw = ImageDraw.Draw(mask)
    m_draw.ellipse((0, 0, photo_size, photo_size), fill=255)

    bordered = Image.new('RGBA', (photo_size + 20, photo_size + 20), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(bordered)
    b_draw.ellipse((0, 0, photo_size + 20, photo_size + 20), fill=theme['accent'])
    bordered.paste(photo, (10, 10), mask)

    shadow = Image.new('RGBA', bordered.size, (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.ellipse((5, 8, photo_size + 16, photo_size + 18), fill=(0, 0, 0, 140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))

    px = (width - bordered.width) // 2
    py = 260
    base.alpha_composite(shadow, (px, py + 10))
    base.alpha_composite(bordered, (px, py))

    name = record.celebrant_name.strip().upper()
    name_lines = textwrap.wrap(name, width=18)[:2]
    y_pos = 740
    for line in name_lines:
        draw.text((540, y_pos), line, font=name_font, fill='white', anchor='mm')
        y_pos += 68

    formatted_date = datetime.strftime(record.birthday_date, '%d %B %Y')
    draw.text((540, y_pos + 14), formatted_date, font=meta_font, fill=theme['accent'], anchor='mm')

    wish_text = (record.wish or '').strip() or DEFAULT_BIRTHDAY_WISH
    wrapped = _fit_text(draw, wish_text, wish_font, max_width=880)[:5]
    wish_box_top = y_pos + 80

    box = Image.new('RGBA', (920, 260), (255, 255, 255, 28))
    box = box.filter(ImageFilter.GaussianBlur(0.8))
    base.alpha_composite(box, (80, wish_box_top - 20))

    line_y = wish_box_top
    for line in wrapped:
        draw.text((540, line_y), line, font=wish_font, fill=theme['text'], anchor='ma')
        line_y += 45

    draw.text((540, height - 70), 'RCCG City of Refuge Parish', font=small_font, fill=theme['accent'], anchor='mm')

    if church_logo_path and Path(church_logo_path).exists():
        logo = Image.open(church_logo_path).convert('RGBA').resize((110, 110), Image.Resampling.LANCZOS)
        base.alpha_composite(logo, (74, 74))

    out_dir = Path(settings.MEDIA_ROOT) / 'generated_flyers'
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f'flyer_{uuid.uuid4().hex[:12]}.png'
    output_path = out_dir / filename

    base.convert('RGB').save(output_path, 'PNG', optimize=True)

    record.generated_flyer.name = f'generated_flyers/{filename}'
    record.save(update_fields=['generated_flyer'])
    return record.generated_flyer.url
