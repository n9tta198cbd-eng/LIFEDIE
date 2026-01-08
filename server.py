from fastapi import FastAPI, Query
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import date, datetime
from PIL import Image, ImageDraw
from io import BytesIO
import math

app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/")
async def root():
    return FileResponse("index.html")


@app.get("/generate")
async def generate_calendar(
    birth: str = Query(..., description="Birth date YYYY-MM-DD"),
    lifespan: int = Query(90, description="Expected lifespan in years"),
    w: int = Query(1290, description="Image width"),
    h: int = Query(2796, description="Image height"),
):
    """Generate life calendar wallpaper PNG"""

    # Parse birth date
    try:
        birth_date = datetime.strptime(birth, "%Y-%m-%d").date()
    except ValueError:
        return Response(content="Invalid date format", status_code=400)

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
    padding_x = w * 0.08  # 8% padding on each side
    padding_y = h * 0.06  # 6% padding top/bottom

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

            # Draw rounded rectangle (or circle for small cells)
            if dot_size < 4:
                # Too small for rounded rect, draw simple rect
                draw.rectangle(
                    [x, y, x + dot_size, y + dot_size],
                    fill=color
                )
            else:
                # Draw rounded rectangle
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

    return Response(
        content=buffer.getvalue(),
        media_type="image/png",
        headers={
            "Content-Disposition": f"inline; filename=life-calendar-{birth}.png"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
