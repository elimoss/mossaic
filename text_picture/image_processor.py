# plottext/image_processor.py

from PIL import Image
import numpy as np


def process_image(image_path, grid_columns, grid_rows, boldness_levels):
    img = Image.open(image_path).convert('L')  # Grayscale
    img = img.resize((grid_columns, grid_rows))
    img_array = np.array(img) / 255.0  # Normalize to 0-1

    # Invert brightness so that darker = lower boldness
    inverted = 1.0 - img_array

    # Map brightness to boldness levels
    thresholds = np.linspace(0, 1, boldness_levels + 1)
    boldness_map = np.digitize(inverted, thresholds) - 1  # 0-indexed

    return boldness_map
