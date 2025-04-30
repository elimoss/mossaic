# plottext/main.py

import argparse
from config_loader import load_config
from image_processor import process_image
from text_generator import TextGenerator
from svg_writer import create_svg
from font_manager import FontManager

def main(config_path):
    config = load_config(config_path)

    boldness_map = process_image(
        config['image_path'],
        config['grid_columns'],
        config['grid_rows'],
        config['boldness_levels']
    )

    text_gen = TextGenerator(config['text_path'])
    font = FontManager(config['font_path'])

    create_svg(
        config['output_svg_path'],
        boldness_map,
        text_gen,
        config,
        font
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    main(args.config)
