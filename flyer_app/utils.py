import textwrap
import uuid
from datetime import datetime
from pathlib import Path

from django.conf import settings
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .forms import DEFAULT_BIRTHDAY_WISH

THEME_STYLES = {
    'royal_grace': {
        'bg_top': '#0A1A45', 'bg_bottom': '#31235A', 'accent': '#D1AB62', 'accent_soft': '#F0DFB6', 'text': '#FDFCFF',
        'photo_shape': 'circle', 'wish_alpha': 40, 'texture': 'soft',
    },
    'refuge_light': {
        'bg_top': '#F8F4EB', 'bg_bottom': '#ECE0CA', 'accent': '#6D5322', 'accent_soft': '#2F3B4F', 'text': '#222D3F',
        'photo_shape': 'rounded', 'wish_alpha': 95, 'texture': 'minimal',
    },
    'covenant_bloom': {
        'bg_top': '#39142F', 'bg_bottom': '#7B2F52', 'accent': '#ECC08E', 'accent_soft': '#F7E0C3', 'text': '#FFF7EF',
        'photo_shape': 'circle', 'wish_alpha': 48, 'texture': 'ornate',
    },
    'emerald_peace': {
        'bg_top': '#11352F', 'bg_bottom': '#2B5B49', 'accent': '#D4B472', 'accent_soft': '#F0E1BF', 'text': '#F6FBF7',
        'photo_shape': 'rounded', 'wish_alpha': 46, 'texture': 'soft',
    },
    'ivory_majesty': {
        'bg_top': '#F6F1E6', 'bg_bottom': '#DDD0B8', 'accent': '#9D7A42', 'accent_soft': '#364154', 'text': '#293345',
        'photo_shape': 'rounded', 'wish_alpha': 103, 'texture': 'minimal',
    },
    'midnight_glory': {
        'bg_top': '#161922', 'bg_bottom': '#1F2D49', 'accent': '#B6BFCE', 'accent_soft': '#E8EDF5', 'text': '#F5F8FD',
        'photo_shape': 'square', 'wish_alpha': 52, 'texture': 'diagonal',
    },
    'wine_gold': {
        'bg_top': '#3B0F1E', 'bg_bottom': '#6F1F32', 'accent': '#D7B271', 'accent_soft': '#F4DFBA', 'text': '#FFF9F1',
        'photo_shape': 'circle', 'wish_alpha': 46, 'texture': 'ornate',
    },
    'graceful_lilac': {
        'bg_top': '#4D3A5F', 'bg_bottom': '#7F617F', 'accent': '#E0C28F', 'accent_soft': '#F5E7CF', 'text': '#FFF9FF',
        'photo_shape': 'rounded', 'wish_alpha': 55, 'texture': 'soft',
    },
}

EXPORT_WIDTH = 1080
EXPORT_HEIGHT = 1200


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


def _fit_text_with_max_lines(draw, text, max_width, max_lines, start_size, min_size, bold=False):
    cleaned = ' '.join((text or '').split())
    if not cleaned:
        return _get_font(start_size, bold=bold), ['']

    for size in range(start_size, min_size - 1, -2):
        font = _get_font(size, bold=bold)
        lines = _fit_text(draw, cleaned, font, max_width)
        if len(lines) <= max_lines:
            return font, lines

    font = _get_font(min_size, bold=bold)
    wrapped = textwrap.wrap(cleaned, width=max(12, int(max_width / max(min_size * 0.57, 1))))
    return font, wrapped[:max_lines]


def _format_date(date_obj):
    return datetime.strftime(date_obj, '%d %B %Y')


def _add_texture_overlay(width, height, accent_rgb, texture='soft'):
    overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    o_draw = ImageDraw.Draw(overlay)
    ar, ag, ab = accent_rgb

    if texture == 'minimal':
        o_draw.rectangle((0, 0, width, int(height * 0.25)), fill=(255, 255, 255, 20))
        o_draw.rectangle((0, int(height * 0.72), width, height), fill=(255, 255, 255, 16))
    elif texture == 'ornate':
        o_draw.ellipse((35, 65, 420, 430), fill=(255, 255, 255, 26))
        o_draw.ellipse((680, 60, 1050, 380), fill=(255, 255, 255, 20))
        o_draw.ellipse((740, 860, 1080, 1180), fill=(ar, ag, ab, 24))
    elif texture == 'diagonal':
        o_draw.polygon([(-160, 20), (450, 20), (150, 420), (-220, 420)], fill=(255, 255, 255, 18))
        o_draw.polygon([(700, 810), (1260, 810), (980, 1230), (620, 1230)], fill=(ar, ag, ab, 20))
    else:
        o_draw.ellipse((70, 90, 410, 430), fill=(255, 255, 255, 25))
        o_draw.ellipse((720, 120, 1040, 440), fill=(255, 255, 255, 20))

    return overlay


def generate_birthday_flyer(record, church_logo_path=None):
    style = THEME_STYLES.get(record.theme, THEME_STYLES['royal_grace'])
    width, height = EXPORT_WIDTH, EXPORT_HEIGHT

    base = _draw_vertical_gradient((width, height), style['bg_top'], style['bg_bottom']).convert('RGBA')
    overlay = _add_texture_overlay(
        width,
        height,
        tuple(int(style['accent'][i:i + 2], 16) for i in (1, 3, 5)),
        texture=style['texture'],
    )
    o_draw = ImageDraw.Draw(overlay)

    o_draw.rounded_rectangle((38, 30, width - 38, height - 30), radius=34, outline=style['accent_soft'], width=3)
    o_draw.line((84, 225, width - 84, 225), fill=style['accent'], width=2)
    o_draw.line((84, height - 112, width - 84, height - 112), fill=style['accent'], width=2)

    base = Image.alpha_composite(base, overlay)
    draw = ImageDraw.Draw(base)

    heading_font = _get_font(57, bold=True)
    title_font = _get_font(27, bold=True)
    meta_font = _get_font(31)
    wish_font = _get_font(28)
    small_font = _get_font(19)

    draw.text((540, 132), 'Happy Birthday', font=heading_font, fill=style['accent_soft'], anchor='mm')

    photo = Image.open(record.uploaded_photo.path).convert('RGB').resize((372, 372), Image.Resampling.LANCZOS)
    frame_size = 396
    framed = Image.new('RGBA', (frame_size, frame_size), (0, 0, 0, 0))
    f_draw = ImageDraw.Draw(framed)

    if style['photo_shape'] == 'circle':
        mask = Image.new('L', (372, 372), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 372, 372), fill=255)
        f_draw.ellipse((0, 0, frame_size, frame_size), fill=style['accent'])
        f_draw.ellipse((11, 11, frame_size - 11, frame_size - 11), fill=style['bg_top'])
        framed.paste(photo, (12, 12), mask)
    else:
        radius = 66 if style['photo_shape'] == 'rounded' else 23
        mask = Image.new('L', (372, 372), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, 372, 372), radius=radius, fill=255)
        f_draw.rounded_rectangle((0, 0, frame_size, frame_size), radius=radius + 16, fill=style['accent'])
        f_draw.rounded_rectangle((10, 10, frame_size - 10, frame_size - 10), radius=radius + 11, fill=style['bg_top'])
        framed.paste(photo, (12, 12), mask)

    shadow = Image.new('RGBA', framed.size, (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.ellipse((16, 18, frame_size - 12, frame_size - 6), fill=(0, 0, 0, 116))
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))

    px = (width - frame_size) // 2
    py = 238
    base.alpha_composite(shadow, (px, py + 7))
    base.alpha_composite(framed, (px, py))

    max_name_width = 870
    name_font, name_lines = _fit_text_with_max_lines(
        draw,
        record.celebrant_name.strip().upper(),
        max_width=max_name_width,
        max_lines=2,
        start_size=54,
        min_size=36,
        bold=True,
    )

    y_pos = 676
    name_step = int(name_font.size * 1.18)
    for line in name_lines:
        draw.text((540, y_pos), line, font=name_font, fill=style['text'], anchor='mm')
        y_pos += name_step

    date_y = y_pos + 10
    draw.text((540, date_y), _format_date(record.birthday_date), font=meta_font, fill=style['accent_soft'], anchor='mm')

    wish_text = (record.wish or '').strip() or DEFAULT_BIRTHDAY_WISH
    wish_font, wish_lines = _fit_text_with_max_lines(
        draw,
        wish_text,
        max_width=840,
        max_lines=5,
        start_size=28,
        min_size=22,
    )

    wish_box_top = date_y + 62
    wish_box_height = 222
    box = Image.new('RGBA', (900, wish_box_height), (255, 255, 255, style['wish_alpha'])).filter(ImageFilter.GaussianBlur(0.5))
    base.alpha_composite(box, (90, wish_box_top - 20))

    line_height = int(wish_font.size * 1.35)
    content_height = len(wish_lines) * line_height
    line_y = wish_box_top + max((wish_box_height - content_height) // 2 - 10, 0)

    for line in wish_lines:
        draw.text((540, line_y), line, font=wish_font, fill=style['text'], anchor='ma')
        line_y += line_height

    draw.text((540, height - 78), '...a home of grace, truth and refuge in Christ', font=small_font, fill=style['accent'], anchor='mm')
    draw.text((540, height - 53), 'With love from RCCG City of Refuge Parish', font=small_font, fill=style['accent_soft'], anchor='mm')

    if church_logo_path and Path(church_logo_path).exists():
        logo = Image.open(church_logo_path).convert('RGBA').resize((92, 92), Image.Resampling.LANCZOS)
        base.alpha_composite(logo, (84, 72))

    out_dir = Path(settings.MEDIA_ROOT) / 'generated_flyers'
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f'flyer_{uuid.uuid4().hex[:12]}.png'
    output_path = out_dir / filename

    base.convert('RGB').save(output_path, 'PNG', optimize=True)

    record.generated_flyer.name = f'generated_flyers/{filename}'
    record.save(update_fields=['generated_flyer'])
    return record.generated_flyer.url
