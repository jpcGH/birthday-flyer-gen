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
        o_draw.ellipse((740, 990, 1080, 1320), fill=(ar, ag, ab, 24))
    elif texture == 'diagonal':
        o_draw.polygon([(-160, 20), (450, 20), (150, 420), (-220, 420)], fill=(255, 255, 255, 18))
        o_draw.polygon([(700, 920), (1260, 920), (980, 1360), (620, 1360)], fill=(ar, ag, ab, 20))
    else:
        o_draw.ellipse((70, 90, 410, 430), fill=(255, 255, 255, 25))
        o_draw.ellipse((720, 120, 1040, 440), fill=(255, 255, 255, 20))

    return overlay


def generate_birthday_flyer(record, church_logo_path=None):
    style = THEME_STYLES.get(record.theme, THEME_STYLES['royal_grace'])
    width, height = 1080, 1350

    base = _draw_vertical_gradient((width, height), style['bg_top'], style['bg_bottom']).convert('RGBA')
    overlay = _add_texture_overlay(
        width,
        height,
        tuple(int(style['accent'][i:i + 2], 16) for i in (1, 3, 5)),
        texture=style['texture'],
    )
    o_draw = ImageDraw.Draw(overlay)

    o_draw.rounded_rectangle((38, 32, width - 38, height - 32), radius=36, outline=style['accent_soft'], width=3)
    o_draw.line((84, 250, width - 84, 250), fill=style['accent'], width=2)
    o_draw.line((84, height - 126, width - 84, height - 126), fill=style['accent'], width=2)

    base = Image.alpha_composite(base, overlay)
    draw = ImageDraw.Draw(base)

    heading_font = _get_font(64, bold=True)
    title_font = _get_font(30, bold=True)
    name_font = _get_font(60, bold=True)
    meta_font = _get_font(34)
    wish_font = _get_font(31)
    small_font = _get_font(21)

    draw.text((540, 98), 'Celebrating You', font=heading_font, fill=style['accent_soft'], anchor='mm')
    draw.text((540, 156), 'Redeemed Christian Church of God', font=title_font, fill=style['accent'], anchor='mm')
    draw.text((540, 196), 'City of Refuge Parish', font=title_font, fill=style['accent'], anchor='mm')

    photo = Image.open(record.uploaded_photo.path).convert('RGB').resize((410, 410), Image.Resampling.LANCZOS)
    frame_size = 436
    framed = Image.new('RGBA', (frame_size, frame_size), (0, 0, 0, 0))
    f_draw = ImageDraw.Draw(framed)

    if style['photo_shape'] == 'circle':
        mask = Image.new('L', (410, 410), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 410, 410), fill=255)
        f_draw.ellipse((0, 0, frame_size, frame_size), fill=style['accent'])
        f_draw.ellipse((11, 11, frame_size - 11, frame_size - 11), fill=style['bg_top'])
        framed.paste(photo, (13, 13), mask)
    else:
        radius = 74 if style['photo_shape'] == 'rounded' else 26
        mask = Image.new('L', (410, 410), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, 410, 410), radius=radius, fill=255)
        f_draw.rounded_rectangle((0, 0, frame_size, frame_size), radius=radius + 20, fill=style['accent'])
        f_draw.rounded_rectangle((10, 10, frame_size - 10, frame_size - 10), radius=radius + 14, fill=style['bg_top'])
        framed.paste(photo, (13, 13), mask)

    shadow = Image.new('RGBA', framed.size, (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.ellipse((18, 24, frame_size - 14, frame_size - 8), fill=(0, 0, 0, 118))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))

    px = (width - frame_size) // 2
    py = 273
    base.alpha_composite(shadow, (px, py + 9))
    base.alpha_composite(framed, (px, py))

    name_lines = textwrap.wrap(record.celebrant_name.strip().upper(), width=20)[:2]
    y_pos = 748
    for line in name_lines:
        draw.text((540, y_pos), line, font=name_font, fill=style['text'], anchor='mm')
        y_pos += 66

    draw.text((540, y_pos + 10), _format_date(record.birthday_date), font=meta_font, fill=style['accent_soft'], anchor='mm')

    wish_text = (record.wish or '').strip() or DEFAULT_BIRTHDAY_WISH
    wish_lines = _fit_text(draw, wish_text, wish_font, max_width=860)[:5]

    wish_box_top = y_pos + 78
    box = Image.new('RGBA', (900, 258), (255, 255, 255, style['wish_alpha'])).filter(ImageFilter.GaussianBlur(0.5))
    base.alpha_composite(box, (90, wish_box_top - 22))

    line_y = wish_box_top
    for line in wish_lines:
        draw.text((540, line_y), line, font=wish_font, fill=style['text'], anchor='ma')
        line_y += 44

    draw.text((540, height - 89), '...a home of grace, truth and refuge in Christ', font=small_font, fill=style['accent'], anchor='mm')
    draw.text((540, height - 62), 'With love from RCCG City of Refuge Parish', font=small_font, fill=style['accent_soft'], anchor='mm')

    if church_logo_path and Path(church_logo_path).exists():
        logo = Image.open(church_logo_path).convert('RGBA').resize((102, 102), Image.Resampling.LANCZOS)
        base.alpha_composite(logo, (84, 82))

    out_dir = Path(settings.MEDIA_ROOT) / 'generated_flyers'
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f'flyer_{uuid.uuid4().hex[:12]}.png'
    output_path = out_dir / filename

    base.convert('RGB').save(output_path, 'PNG', optimize=True)

    record.generated_flyer.name = f'generated_flyers/{filename}'
    record.save(update_fields=['generated_flyer'])
    return record.generated_flyer.url
