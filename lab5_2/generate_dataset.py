"""
Генератор стабильного датасета геометрических фигур.
"""
import os
import csv
import random
import numpy as np
from PIL import Image, ImageDraw

FIGURES = {
    'circle':    'draw_circle',
    'cross':     'draw_cross',
    'line':      'draw_line',
    'rectangle': 'draw_rectangle',
    'rhombus':   'draw_rhombus',
    'square':    'draw_square',
    'star':      'draw_star',
    'triangle':  'draw_triangle',
}

IMAGE_SIZE = 64
SAMPLES_PER_CLASS = 100  # 800 примеров — оптимально для обучения за секунды
OUTPUT_CSV = os.path.join('datasets', 'datasets.csv')

def render_figure(fig_type):
    img = Image.new('L', (IMAGE_SIZE, IMAGE_SIZE), color=255)
    draw = ImageDraw.Draw(img)

    # Фиксированные, но вариативные рамки, чтобы фигуры не сливались
    margin = random.randint(12, 16)
    x1, y1 = margin, margin
    x2, y2 = IMAGE_SIZE - margin, IMAGE_SIZE - margin
    line_width = 6

    if fig_type == 'circle':
        draw.ellipse([x1, y1, x2, y2], outline=0, width=line_width)
    elif fig_type == 'cross':
        cx, cy = (x1+x2)//2, (y1+y2)//2
        draw.line([cx, y1, cx, y2], fill=0, width=line_width)
        draw.line([x1, cy, x2, cy], fill=0, width=line_width)
    elif fig_type == 'line':
        draw.line([x1, y1, x2, y2], fill=0, width=line_width)
    elif fig_type == 'square':
        draw.rectangle([x1, y1, x2, y2], outline=0, width=line_width)
    elif fig_type == 'rectangle':
        draw.rectangle([x1, y1+6, x2, y2-6], outline=0, width=line_width)
    elif fig_type == 'rhombus':
        cx, cy = (x1+x2)//2, (y1+y2)//2
        draw.polygon([(cx, y1), (x2, cy), (cx, y2), (x1, cy)], outline=0)
    elif fig_type == 'star':
        cx, cy = (x1+x2)//2, (y1+y2)//2
        draw.line([x1, y1, x2, y2], fill=0, width=line_width)
        draw.line([x1, y2, x2, y1], fill=0, width=line_width)
        draw.line([cx, y1, cx, y2], fill=0, width=line_width)
        draw.line([x1, cy, x2, cy], fill=0, width=line_width)
    elif fig_type == 'triangle':
        pts = [((x1+x2)//2, y1), (x1, y2), (x2, y2)]
        draw.polygon(pts, outline=0)

    # Легкий поворот для разнообразия
    angle = random.uniform(-10, 10)
    img = img.rotate(angle, fillcolor=255)

    arr = np.array(img, dtype=np.float32) / 255.0
    return arr

def main():
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    rows = []

    for label in FIGURES.keys():
        print(f"Генерация фигуры '{label}'...")
        for i in range(SAMPLES_PER_CLASS):
            pixels = render_figure(label)
            row = [label] + [int(p * 255) for p in pixels.flatten()]
            rows.append(row)

    header = ['label'] + [f'pixel {i+1}' for i in range(IMAGE_SIZE * IMAGE_SIZE)]
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"\nГотово! Сохранено {len(rows)} примеров в {OUTPUT_CSV}")

if __name__ == '__main__':
    main()