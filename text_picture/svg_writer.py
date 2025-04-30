# plottext/svg_writer.py

import svgwrite
from tqdm import tqdm


def draw_glyph(dwg, glyph_data, insert_point, scale, stroke_color, stroke_width):
    if not glyph_data:
        return

    group = dwg.g(stroke=stroke_color, fill="none", stroke_width=stroke_width)

    for start, end in glyph_data:
        start_x = insert_point[0] + start[0] * scale
        start_y = insert_point[1] - start[1] * scale  # Y-flip because SVG y-down
        end_x = insert_point[0] + end[0] * scale
        end_y = insert_point[1] - end[1] * scale

        group.add(dwg.line(start=(start_x, start_y), end=(end_x, end_y)))

    dwg.add(group)

def create_svg(output_path, boldness_map, text_gen, config, font_manager):
    dwg = svgwrite.Drawing(output_path, size=(config['canvas_width'], config['canvas_height']))
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=config['background_color']))

    cell_width = config['canvas_width'] / config['grid_columns']
    cell_height = config['canvas_height'] / config['grid_rows']

    for row in tqdm(list(range(config['grid_rows'])), desc="Processing Rows"):
        for col in range(config['grid_columns']):
            char = text_gen.next_char()
            glyph = font_manager.get_glyph(char.upper())  # Hershey is typically uppercase
            boldness = boldness_map[row, col] + 1  # 1-based

            x_center = col * cell_width + cell_width / 2
            y_center = row * cell_height + cell_height / 2

            for i in range(boldness):
                offset = (i - (boldness - 1) / 2) * config['stroke_width']

                insert_point = (x_center + offset, y_center)
                draw_glyph(
                    dwg,
                    glyph,
                    insert_point,
                    scale=config['char_height'] / 20,  # scale normalized to ~20 unit tall glyph
                    stroke_color=config['text_color'],
                    stroke_width=0.4  # Fine plotter line
                )

    dwg.save()
