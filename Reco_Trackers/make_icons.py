from pathlib import Path
from PIL import Image, ImageDraw

Path("docs").mkdir(exist_ok=True)

for size in (192, 512):
    s = size / 512
    img = Image.new("RGB", (size, size), "#0f172a")
    d = ImageDraw.Draw(img)
    # 3 barres montantes vertes
    for i, h in enumerate((140, 220, 320)):
        x = 112 + i * 104
        d.rounded_rectangle([x * s, (400 - h) * s, (x + 72) * s, 400 * s],
                            radius=14 * s, fill="#22c55e")
    img.save(f"docs/icon-{size}.png")
print("Icônes créées.")
