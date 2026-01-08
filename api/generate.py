from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import date, datetime
from PIL import Image, ImageDraw
from io import BytesIO
import base64


def generate_calendar(birth_str: str, lifespan: int, w: int, h: int) -> bytes:
    """Generate life calendar PNG image"""

    # Parse birth date
    birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()

    # Calculate weeks
    today = date.today()
    lived_days = (today - birth_date).days
    lived_weeks = lived_days // 7
    total_weeks = lifespan * 52

    # Colors
    bg_color = (26, 26, 26)  # #1a1a1a
    lived_color = (255, 255, 255)  # white
    future_color = (51, 51, 51)  # #333333
    current_color = (76, 175, 80)  # #4CAF50

    # Create image
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    # Grid layout: 52 columns (weeks) x lifespan rows (years)
    cols = 52
    rows = lifespan

    # Calculate cell size with padding
    padding_x = w * 0.08
    padding_y = h * 0.06

    grid_width = w - (2 * padding_x)
    grid_height = h - (2 * padding_y)

    # Cell size (square cells)
    cell_w = grid_width / cols
    cell_h = grid_height / rows
    cell_size = min(cell_w, cell_h)

    # Gap between cells
    gap = cell_size * 0.15
    dot_size = cell_size - gap

    # Center the grid
    actual_grid_width = cols * cell_size
    actual_grid_height = rows * cell_size
    offset_x = (w - actual_grid_width) / 2
    offset_y = (h - actual_grid_height) / 2

    # Draw weeks
    for year in range(rows):
        for week in range(cols):
            week_number = year * 52 + week

            x = offset_x + week * cell_size + gap / 2
            y = offset_y + year * cell_size + gap / 2

            # Determine color
            if week_number < lived_weeks:
                color = lived_color
            elif week_number == lived_weeks:
                color = current_color
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
            birth = params.get('birth', [''])[0]
            lifespan = int(params.get('lifespan', ['90'])[0])
            w = int(params.get('w', ['1290'])[0])
            h = int(params.get('h', ['2796'])[0])

            if not birth:
                self.send_response(400)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Missing birth parameter')
                return

            # Validate dimensions
            w = max(100, min(5000, w))
            h = max(100, min(5000, h))
            lifespan = max(50, min(120, lifespan))

            # Generate image
            image_bytes = generate_calendar(birth, lifespan, w, h)

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Disposition', f'inline; filename=life-calendar-{birth}.png')
            self.send_header('Cache-Control', 'public, max-age=86400')
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
