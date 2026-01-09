from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import date, datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import math


def generate_life_calendar(birth_str: str, lifespan: int, w: int, h: int) -> bytes:
    """Generate life calendar - each box = 1 week of life"""
    birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
    today = date.today()

    lived_days = (today - birth_date).days
    lived_weeks = lived_days // 7
    total_weeks = lifespan * 52

    # Colors
    bg_color = (0, 0, 0)
    lived_color = (255, 255, 255)
    future_color = (40, 40, 40)
    current_color = (76, 175, 80)
    text_color = (140, 140, 140)

    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    # Grid: 52 columns x lifespan rows
    cols = 52
    rows = lifespan

    padding_x = w * 0.06
    padding_y_top = h * 0.08
    padding_y_bottom = h * 0.04

    grid_width = w - (2 * padding_x)
    grid_height = h - padding_y_top - padding_y_bottom

    cell_w = grid_width / cols
    cell_h = grid_height / rows
    cell_size = min(cell_w, cell_h)

    gap = cell_size * 0.12
    dot_size = cell_size - gap

    actual_grid_width = cols * cell_size
    actual_grid_height = rows * cell_size
    offset_x = (w - actual_grid_width) / 2
    offset_y = padding_y_top + (grid_height - actual_grid_height) / 2

    # Draw label
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(w * 0.022))
    except:
        try:
            font = ImageFont.truetype("arial.ttf", int(w * 0.022))
        except:
            font = ImageFont.load_default()

    label = "LIFE IN WEEKS"
    bbox = draw.textbbox((0, 0), label, font=font)
    draw.text(((w - bbox[2]) / 2, padding_y_top * 0.3), label, fill=text_color, font=font)

    # Draw weeks
    for year in range(rows):
        for week in range(cols):
            week_num = year * 52 + week
            x = offset_x + week * cell_size + gap / 2
            y = offset_y + year * cell_size + gap / 2

            if week_num < lived_weeks:
                color = lived_color
            elif week_num == lived_weeks:
                color = current_color
            else:
                color = future_color

            radius = dot_size * 0.15 if dot_size >= 4 else 0
            if radius > 0:
                draw.rounded_rectangle([x, y, x + dot_size, y + dot_size], radius=radius, fill=color)
            else:
                draw.rectangle([x, y, x + dot_size, y + dot_size], fill=color)

    buffer = BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    buffer.seek(0)
    return buffer.getvalue()


def generate_year_calendar(w: int, h: int) -> bytes:
    """Generate year calendar - each box = 1 day of current year"""
    today = date.today()
    year_start = date(today.year, 1, 1)
    year_end = date(today.year, 12, 31)

    total_days = (year_end - year_start).days + 1
    elapsed_days = (today - year_start).days

    bg_color = (0, 0, 0)
    passed_color = (255, 255, 255)
    future_color = (40, 40, 40)
    current_color = (76, 175, 80)
    text_color = (140, 140, 140)

    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    # Calculate grid
    padding_x = w * 0.08
    padding_y_top = h * 0.1
    padding_y_bottom = h * 0.08

    grid_width = w - (2 * padding_x)
    grid_height = h - padding_y_top - padding_y_bottom

    # Try to make roughly 7 columns (days of week)
    cols = 7
    rows = math.ceil(total_days / cols)

    cell_w = grid_width / cols
    cell_h = grid_height / rows
    cell_size = min(cell_w, cell_h)

    gap = cell_size * 0.08
    dot_size = cell_size - gap

    actual_grid_width = cols * cell_size
    actual_grid_height = rows * cell_size
    offset_x = (w - actual_grid_width) / 2
    offset_y = padding_y_top + (grid_height - actual_grid_height) / 2

    # Draw year label
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(w * 0.035))
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(w * 0.022))
    except:
        try:
            font = ImageFont.truetype("arial.ttf", int(w * 0.035))
            small_font = ImageFont.truetype("arial.ttf", int(w * 0.022))
        except:
            font = ImageFont.load_default()
            small_font = font

    year_text = str(today.year)
    bbox = draw.textbbox((0, 0), year_text, font=font)
    draw.text(((w - bbox[2]) / 2, padding_y_top * 0.25), year_text, fill=(255, 255, 255), font=font)

    # Draw days left
    days_left = total_days - elapsed_days - 1
    days_text = f"{days_left} days left"
    bbox2 = draw.textbbox((0, 0), days_text, font=small_font)
    draw.text(((w - bbox2[2]) / 2, h - padding_y_bottom * 0.7), days_text, fill=text_color, font=small_font)

    # Draw days
    for i in range(total_days):
        row = i // cols
        col = i % cols
        x = offset_x + col * cell_size + gap / 2
        y = offset_y + row * cell_size + gap / 2

        if i < elapsed_days:
            color = passed_color
        elif i == elapsed_days:
            color = current_color
        else:
            color = future_color

        radius = dot_size * 0.15 if dot_size >= 4 else 0
        if radius > 0:
            draw.rounded_rectangle([x, y, x + dot_size, y + dot_size], radius=radius, fill=color)
        else:
            draw.rectangle([x, y, x + dot_size, y + dot_size], fill=color)

    buffer = BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    buffer.seek(0)
    return buffer.getvalue()


def generate_goal_calendar(goal: str, start_str: str, deadline_str: str, w: int, h: int) -> bytes:
    """Generate goal calendar - countdown to deadline"""
    start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
    deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
    today = date.today()

    total_days = (deadline_date - start_date).days
    if total_days <= 0:
        total_days = 30

    elapsed_days = max(0, min((today - start_date).days, total_days))
    days_left = max(0, total_days - elapsed_days)

    bg_color = (0, 0, 0)
    passed_color = (255, 255, 255)
    future_color = (40, 40, 40)
    current_color = (76, 175, 80)
    text_color = (140, 140, 140)

    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    padding_x = w * 0.08
    padding_y_top = h * 0.12
    padding_y_bottom = h * 0.08

    grid_width = w - (2 * padding_x)
    grid_height = h - padding_y_top - padding_y_bottom

    # Calculate optimal grid
    aspect = grid_width / grid_height
    cols = max(7, int(math.sqrt(total_days * aspect)))
    rows = math.ceil(total_days / cols)

    cell_w = grid_width / cols
    cell_h = grid_height / rows
    cell_size = min(cell_w, cell_h)

    gap = cell_size * 0.1
    dot_size = cell_size - gap

    actual_grid_width = cols * cell_size
    actual_grid_height = rows * cell_size
    offset_x = (w - actual_grid_width) / 2
    offset_y = padding_y_top + (grid_height - actual_grid_height) / 2

    # Draw goal label
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(w * 0.028))
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(w * 0.022))
    except:
        try:
            font = ImageFont.truetype("arial.ttf", int(w * 0.028))
            small_font = ImageFont.truetype("arial.ttf", int(w * 0.022))
        except:
            font = ImageFont.load_default()
            small_font = font

    # Goal name
    bbox = draw.textbbox((0, 0), goal.upper(), font=font)
    draw.text(((w - bbox[2]) / 2, padding_y_top * 0.3), goal.upper(), fill=text_color, font=font)

    # Days left
    days_text = f"{days_left} DAYS TO GO"
    bbox2 = draw.textbbox((0, 0), days_text, font=small_font)
    draw.text(((w - bbox2[2]) / 2, h - padding_y_bottom * 0.6), days_text, fill=text_color, font=small_font)

    # Draw days
    for i in range(total_days):
        row = i // cols
        col = i % cols
        x = offset_x + col * cell_size + gap / 2
        y = offset_y + row * cell_size + gap / 2

        if i < elapsed_days:
            color = passed_color
        elif i == elapsed_days:
            color = current_color
        else:
            color = future_color

        radius = dot_size * 0.15 if dot_size >= 4 else 0
        if radius > 0:
            draw.rounded_rectangle([x, y, x + dot_size, y + dot_size], radius=radius, fill=color)
        else:
            draw.rectangle([x, y, x + dot_size, y + dot_size], fill=color)

    buffer = BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    buffer.seek(0)
    return buffer.getvalue()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        try:
            cal_type = params.get('type', ['goal'])[0]
            w = int(params.get('w', ['1179'])[0])
            h = int(params.get('h', ['2556'])[0])
            w = max(100, min(5000, w))
            h = max(100, min(5000, h))

            if cal_type == 'life':
                birth = params.get('birth', [''])[0]
                lifespan = int(params.get('lifespan', ['90'])[0])
                if not birth:
                    raise ValueError("Missing birth parameter")
                image_bytes = generate_life_calendar(birth, lifespan, w, h)

            elif cal_type == 'year':
                image_bytes = generate_year_calendar(w, h)

            elif cal_type == 'goal':
                goal = params.get('goal', ['My Goal'])[0]
                start = params.get('start', [''])[0]
                deadline = params.get('deadline', [''])[0]
                if not start or not deadline:
                    raise ValueError("Missing start or deadline")
                image_bytes = generate_goal_calendar(goal, start, deadline, w, h)

            else:
                raise ValueError(f"Unknown type: {cal_type}")

            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(image_bytes)

        except ValueError as e:
            self.send_response(400)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Error: {str(e)}'.encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Server error: {str(e)}'.encode())
