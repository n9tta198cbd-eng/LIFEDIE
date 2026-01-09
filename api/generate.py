from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import date, datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import math


def generate_life_calendar(birth_str: str, lifespan: int, w: int, h: int) -> bytes:
    """Generate life calendar - each box = 1 week of life"""
    birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
    today = date.today()

    lived_days = (today - birth_date).days
    lived_weeks = lived_days // 7

    # Colors
    bg_color = (10, 10, 10)
    lived_color = (255, 255, 255)
    future_color = (50, 50, 50)
    text_color = (120, 120, 120)

    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    # Grid: 52 columns x lifespan rows
    cols = 52
    rows = lifespan

    # Padding for iPhone clock at top
    clock_padding = h * 0.12
    title_area = h * 0.05
    axis_padding_left = w * 0.05
    axis_padding_top = h * 0.02
    padding_bottom = h * 0.06
    padding_right = w * 0.02

    grid_start_x = axis_padding_left
    grid_start_y = clock_padding + title_area + axis_padding_top
    grid_width = w - axis_padding_left - padding_right
    grid_height = h - grid_start_y - padding_bottom

    cell_w = grid_width / cols
    cell_h = grid_height / rows
    cell_size = min(cell_w, cell_h)

    gap = cell_size * 0.08
    dot_size = cell_size - gap

    actual_grid_width = cols * cell_size
    actual_grid_height = rows * cell_size

    # Center grid horizontally considering left axis
    offset_x = axis_padding_left + (grid_width - actual_grid_width) / 2
    offset_y = grid_start_y

    # Load fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(w * 0.038))
        axis_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(w * 0.018))
    except:
        try:
            title_font = ImageFont.truetype("arial.ttf", int(w * 0.038))
            axis_font = ImageFont.truetype("arial.ttf", int(w * 0.018))
        except:
            title_font = ImageFont.load_default()
            axis_font = title_font

    # Draw title
    title = "Your life in weeks."
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_x = (w - bbox[2]) / 2
    title_y = clock_padding + (title_area - bbox[3]) / 2
    draw.text((title_x, title_y), title, fill=(255, 255, 255), font=title_font)

    # Draw top axis (week numbers: 5, 10, 15... 50)
    for week_label in range(5, 51, 5):
        x = offset_x + (week_label - 0.5) * cell_size
        label = str(week_label)
        bbox = draw.textbbox((0, 0), label, font=axis_font)
        draw.text((x - bbox[2] / 2, offset_y - axis_padding_top * 0.8), label, fill=text_color, font=axis_font)

    # Draw left axis (year numbers: 5, 10, 15... lifespan)
    for year_label in range(5, lifespan + 1, 5):
        y = offset_y + (year_label - 0.5) * cell_size
        label = str(year_label)
        bbox = draw.textbbox((0, 0), label, font=axis_font)
        draw.text((offset_x - bbox[2] - cell_size * 0.5, y - bbox[3] / 2), label, fill=text_color, font=axis_font)

    # Draw weeks grid
    for year in range(rows):
        for week in range(cols):
            week_num = year * 52 + week
            x = offset_x + week * cell_size + gap / 2
            y = offset_y + year * cell_size + gap / 2

            if week_num < lived_weeks:
                color = lived_color
            else:
                color = future_color

            draw.rectangle([x, y, x + dot_size, y + dot_size], fill=color)

    # Draw logo at bottom center
    logo_size = int(w * 0.035)
    logo_x = w / 2
    logo_y = h - padding_bottom * 0.4
    draw.ellipse([logo_x - logo_size/2, logo_y - logo_size/2,
                  logo_x + logo_size/2, logo_y + logo_size/2],
                 outline=(80, 80, 80), width=int(logo_size * 0.05))
    dot_r = logo_size * 0.12
    draw.ellipse([logo_x + logo_size*0.18 - dot_r, logo_y - logo_size*0.18 - dot_r,
                  logo_x + logo_size*0.18 + dot_r, logo_y - logo_size*0.18 + dot_r],
                 fill=(80, 80, 80))

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

    bg_color = (10, 10, 10)
    passed_color = (255, 255, 255)
    future_color = (50, 50, 50)
    text_color = (120, 120, 120)

    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    # Padding for iPhone clock at top
    clock_padding = h * 0.12
    title_area = h * 0.06
    padding_x = w * 0.08
    padding_bottom = h * 0.06

    grid_start_y = clock_padding + title_area
    grid_width = w - (2 * padding_x)
    grid_height = h - grid_start_y - padding_bottom

    # Grid layout for year (weeks as columns, 7 rows for days)
    cols = 53  # weeks in year
    rows = 7   # days in week

    cell_w = grid_width / cols
    cell_h = grid_height / rows
    cell_size = min(cell_w, cell_h)

    gap = cell_size * 0.08
    dot_size = cell_size - gap

    actual_grid_width = cols * cell_size
    actual_grid_height = rows * cell_size
    offset_x = (w - actual_grid_width) / 2
    offset_y = grid_start_y + (grid_height - actual_grid_height) / 2

    # Load fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(w * 0.05))
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(w * 0.022))
    except:
        try:
            title_font = ImageFont.truetype("arial.ttf", int(w * 0.05))
            small_font = ImageFont.truetype("arial.ttf", int(w * 0.022))
        except:
            title_font = ImageFont.load_default()
            small_font = title_font

    # Draw year
    year_text = str(today.year)
    bbox = draw.textbbox((0, 0), year_text, font=title_font)
    draw.text(((w - bbox[2]) / 2, clock_padding + (title_area - bbox[3]) / 2), year_text, fill=(255, 255, 255), font=title_font)

    # Draw days left at bottom
    days_left = total_days - elapsed_days - 1
    days_text = f"{days_left} days left"
    bbox2 = draw.textbbox((0, 0), days_text, font=small_font)
    draw.text(((w - bbox2[2]) / 2, h - padding_bottom * 0.5), days_text, fill=text_color, font=small_font)

    # Draw days (column = week number, row = day of week)
    for day_num in range(total_days):
        day_date = year_start + timedelta(days=day_num)
        week_num = day_date.isocalendar()[1] - 1
        day_of_week = day_date.weekday()  # 0=Monday

        if week_num >= cols:
            week_num = cols - 1

        x = offset_x + week_num * cell_size + gap / 2
        y = offset_y + day_of_week * cell_size + gap / 2

        if day_num < elapsed_days:
            color = passed_color
        else:
            color = future_color

        draw.rectangle([x, y, x + dot_size, y + dot_size], fill=color)

    # Draw logo at bottom center
    logo_size = int(w * 0.035)
    logo_x = w / 2
    logo_y = h - padding_bottom * 0.4
    draw.ellipse([logo_x - logo_size/2, logo_y - logo_size/2,
                  logo_x + logo_size/2, logo_y + logo_size/2],
                 outline=(80, 80, 80), width=int(logo_size * 0.05))
    dot_r = logo_size * 0.12
    draw.ellipse([logo_x + logo_size*0.18 - dot_r, logo_y - logo_size*0.18 - dot_r,
                  logo_x + logo_size*0.18 + dot_r, logo_y - logo_size*0.18 + dot_r],
                 fill=(80, 80, 80))

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

    bg_color = (10, 10, 10)
    passed_color = (255, 255, 255)
    future_color = (50, 50, 50)
    text_color = (120, 120, 120)

    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    # Padding for iPhone clock at top
    clock_padding = h * 0.12
    title_area = h * 0.06
    padding_x = w * 0.08
    padding_bottom = h * 0.06

    grid_start_y = clock_padding + title_area
    grid_width = w - (2 * padding_x)
    grid_height = h - grid_start_y - padding_bottom

    # Calculate optimal grid
    aspect = grid_width / grid_height
    cols = max(7, int(math.sqrt(total_days * aspect)))
    rows = math.ceil(total_days / cols)

    cell_w = grid_width / cols
    cell_h = grid_height / rows
    cell_size = min(cell_w, cell_h)

    gap = cell_size * 0.08
    dot_size = cell_size - gap

    actual_grid_width = cols * cell_size
    actual_grid_height = rows * cell_size
    offset_x = (w - actual_grid_width) / 2
    offset_y = grid_start_y + (grid_height - actual_grid_height) / 2

    # Load fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(w * 0.035))
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(w * 0.022))
    except:
        try:
            title_font = ImageFont.truetype("arial.ttf", int(w * 0.035))
            small_font = ImageFont.truetype("arial.ttf", int(w * 0.022))
        except:
            title_font = ImageFont.load_default()
            small_font = title_font

    # Goal name
    bbox = draw.textbbox((0, 0), goal, font=title_font)
    draw.text(((w - bbox[2]) / 2, clock_padding + (title_area - bbox[3]) / 2), goal, fill=(255, 255, 255), font=title_font)

    # Days left at bottom
    days_text = f"{days_left} days to go"
    bbox2 = draw.textbbox((0, 0), days_text, font=small_font)
    draw.text(((w - bbox2[2]) / 2, h - padding_bottom * 0.5), days_text, fill=text_color, font=small_font)

    # Draw days
    for i in range(total_days):
        row = i // cols
        col = i % cols
        x = offset_x + col * cell_size + gap / 2
        y = offset_y + row * cell_size + gap / 2

        if i < elapsed_days:
            color = passed_color
        else:
            color = future_color

        draw.rectangle([x, y, x + dot_size, y + dot_size], fill=color)

    # Draw logo at bottom center
    logo_size = int(w * 0.035)
    logo_x = w / 2
    logo_y = h - padding_bottom * 0.4
    draw.ellipse([logo_x - logo_size/2, logo_y - logo_size/2,
                  logo_x + logo_size/2, logo_y + logo_size/2],
                 outline=(80, 80, 80), width=int(logo_size * 0.05))
    dot_r = logo_size * 0.12
    draw.ellipse([logo_x + logo_size*0.18 - dot_r, logo_y - logo_size*0.18 - dot_r,
                  logo_x + logo_size*0.18 + dot_r, logo_y - logo_size*0.18 + dot_r],
                 fill=(80, 80, 80))

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
