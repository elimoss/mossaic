import argparse
import numpy as np
import pandas as pd
from PIL import Image

# Base color definitions (pure colors)
BASE_COLOR_MAP = {
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "green": (0, 255, 0),
    "yellow": (255, 255, 0),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
    "pink": (255, 192, 203),
    "gray": (128, 128, 128),
}


def generate_color_shades(base_color, levels):
    """Generates N levels of a given color from light to dark."""
    r, g, b = BASE_COLOR_MAP[base_color]
    shades = {}
    for i in range(levels):
        factor = (i / (levels - 1)) if levels > 1 else 1
        new_color = (int(r * factor), int(g * factor), int(b * factor))
        shades[f"{base_color}_{i}"] = new_color
    return shades


def generate_greyscale_palette(levels):
    """Generates an N-level greyscale palette from black to white."""
    greyscale_palette = {}
    for i in range(levels):
        intensity = int((i / (levels - 1)) * 255) if levels > 1 else 255
        greyscale_palette[f"gray_{i}"] = (intensity, intensity, intensity)
    return greyscale_palette


def closest_color(rgb, available_colors):
    """Finds the closest available color to an input RGB value."""
    min_dist = float("inf")
    best_color = None
    for color_name, color_rgb in available_colors.items():
        dist = np.linalg.norm(np.array(rgb) - np.array(color_rgb))
        if dist < min_dist:
            min_dist = dist
            best_color = color_name
    return best_color


def process_image(image_path, output_csv, output_png, tiles_x, tiles_y, available_colors):
    """Converts an image into a mosaic CSV file and generates a PNG preview."""

    # Load image and convert to RGB
    img = Image.open(image_path).convert("RGB")
    img_width, img_height = img.size

    # Calculate pixel sampling size per tile
    tile_w = img_width // tiles_x
    tile_h = img_height // tiles_y

    # Create mosaic data and preview image array
    mosaic = pd.DataFrame(index=range(tiles_y), columns=range(tiles_x))
    preview_array = np.zeros((tiles_y, tiles_x, 3), dtype=np.uint8)

    # Process each tile by averaging pixel colors
    img_data = np.array(img)
    for y in range(tiles_y):
        for x in range(tiles_x):
            # Extract the subregion of pixels for this tile
            subregion = img_data[y * tile_h: (y + 1) * tile_h, x * tile_w: (x + 1) * tile_w]

            # Compute the average color of this region
            avg_color = np.mean(subregion, axis=(0, 1)).astype(int)

            # Find the closest available color
            closest = closest_color(avg_color, available_colors)
            mosaic.at[y, x] = closest
            preview_array[y, x] = available_colors[closest]

    # Save to CSV
    mosaic.to_csv(output_csv, index=False, header=False)
    print(f"Mosaic saved to {output_csv}")

    # Save preview image
    preview_img = Image.fromarray(preview_array)
    preview_img = preview_img.resize((tiles_x * 20, tiles_y * 20), Image.NEAREST)  # Scale up for visibility
    preview_img.save(output_png)
    print(f"Preview saved to {output_png}")


def build_args():
    parser = argparse.ArgumentParser(description="Convert an image into a mosaic CSV and preview PNG.")
    parser.add_argument("--image", required=True, help="Path to the input image")
    parser.add_argument("--output", required=True, help="Output CSV file")
    parser.add_argument("--preview", required=True, help="Output PNG preview file")
    parser.add_argument("--tiles_x", type=int, required=True, help="Number of tiles along the x-axis")
    parser.add_argument("--tiles_y", type=int, required=True, help="Number of tiles along the y-axis")
    parser.add_argument("--colors", required=False,
                        help="Comma-separated list of colors with levels, e.g. 'red:5,blue:3'")
    parser.add_argument("--greyscale_levels", type=int, required=False, help="Number of greyscale levels (optional)")

    args = parser.parse_args()
    return args

def build_palette(args):

    # Build available color palette
    available_colors = {}

    if args.colors:
        color_definitions = args.colors.split(",")
        for color_def in color_definitions:
            parts = color_def.split(":")
            color_name = parts[0]
            levels = int(parts[1]) if len(parts) > 1 else 1
            if color_name in BASE_COLOR_MAP:
                available_colors.update(generate_color_shades(color_name, levels))

    if args.greyscale_levels:
        available_colors.update(generate_greyscale_palette(args.greyscale_levels))

    if not available_colors:
        raise ValueError("No valid colors provided. Use --colors or --greyscale_levels.")

    return available_colors

def main():
    args = build_args()
    available_colors = build_palette(args)
    # Process image
    process_image(args.image, args.output, args.preview, args.tiles_x, args.tiles_y, available_colors)

if __name__ == "__main__":
    main()
