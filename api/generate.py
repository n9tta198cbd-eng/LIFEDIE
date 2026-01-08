from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import date, datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import math


def generate_calendar(goal: str, start_str: str, deadline_str: str, w: int, h: int) -> bytes:
    """Generate goal progress calendar PNG image"""

    # Parse dates
    start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
    deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
    today = date.today()

    # Calculate days
    total_days = (deadline_date - start_date).days
    elapsed_days = (today - start_date).days

    # Ensure valid range
    if total_days <= 0:
        total_days = 30

    elapsed_days = max(0, min(elapsed_days, total_days))

    # Colors
    bg_color = (0, 0, 0)  # black
    passed_color = (255, 255, 255)  # white
    future_color = (40, 40, 40)  # dark gray
    today_color = (76, 175, 80)  # green
    text_color = (255, 255, 255)  # white

    # Create image
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    # Grid layout - calculate optimal grid
    # We want roughly square cells that fit the screen well
    padding_x = w * 0.06
    padding_y_top = h * 0.12  # More space at top for goal text
    padding_y_bottom = h * 0.06

    grid_width = w - (2 * padding_x)
    grid_height = h - padding_y_top - padding_y_bottom

    # Calculate grid dimensions
    # Try to make cells roughly square
    aspect = grid_width / grid_height

    # Start with sqrt of total_days and adjust
    cols = max(7, int(math.sqrt(total_days * aspect)))
    rows = math.ceil(total_days / cols)

    # Adjust to fit nicely
    while rows * cols < total_days:
        rows += 1

    # Cell size
    cell_w = grid_width / cols
    cell_h = grid_height / rows
    cell_size = min(cell_w, cell_h)

    # Gap between cells
    gap = cell_size * 0.12
    dot_size = cell_size - gap

    # Center the grid
    actual_grid_width = cols * cell_size
    actual_grid_height = rows * cell_size
    offset_x = (w - actual_grid_width) / 2
    offset_y = padding_y_top + (grid_height - actual_grid_height) / 2

    # Draw goal text at top
    try:
        # Try to use a nice font
        font_size = int(w * 0.045)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", int(w * 0.045))
        except:
            font = ImageFont.load_default()

    # Draw goal text centered
    text_bbox = draw.textbbox((0, 0), goal, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (w - text_width) / 2
    text_y = padding_y_top * 0.35
    draw.text((text_x, text_y), goal, fill=text_color, font=font)

    # Draw days progress text
    try:
        small_font_size = int(w * 0.028)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", small_font_size)
    except:
        try:
            small_font = ImageFont.truetype("arial.ttf", int(w * 0.028))
        except:
            small_font = font

    days_left = max(0, total_days - elapsed_days)
    progress_text = f"{days_left} days left"
    progress_bbox = draw.textbbox((0, 0), progress_text, font=small_font)
    progress_width = progress_bbox[2] - progress_bbox[0]
    progress_x = (w - progress_width) / 2
    progress_y = text_y + font_size + 10
    draw.text((progress_x, progress_y), progress_text, fill=(128, 128, 128), font=small_font)

    # Draw cells
    for i in range(total_days):
        row = i // cols
        col = i % cols

        x = offset_x + col * cell_size + gap / 2
        y = offset_y + row * cell_size + gap / 2

        # Determine color
        if i < elapsed_days:
            color = passed_color
        elif i == elapsed_days:
            color = today_color
        else:
            color = future_color

        # Draw rounded rectangle
        if dot_size < 4:
            draw.rectangle(
                [x, y, x + dot_size, y + dot_size],
                fill=color
            )
        else:
            radius = dot_size * 0.2
            draw.rounded_rectangle(
                [x, y, x + dot_size, y + dot_size],
                radius=radius,
                fill=color
            )

    # Save to bytes
    buffer = BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    buffer.seek(0)

    return buffer.getvalue()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        try:
            goal = params.get('goal', ['My Goal'])[0]
            start = params.get('start', [''])[0]
            deadline = params.get('deadline', [''])[0]
            w = int(params.get('w', ['1179'])[0])
            h = int(params.get('h', ['2556'])[0])

            if not start or not deadline:
                self.send_response(400)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Missing start or deadline parameter')
                return

            # Validate dimensions
            w = max(100, min(5000, w))
            h = max(100, min(5000, h))

            # Generate image
            image_bytes = generate_calendar(goal, start, deadline, w, h)

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Disposition', f'inline; filename=goal-calendar.png')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(image_bytes)

        except ValueError as e:
            self.send_response(400)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Invalid parameter: {str(e)}'.encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Error: {str(e)}'.encode())
