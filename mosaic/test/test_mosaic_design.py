import os

import pandas as pd
import pytest

from mosaic.generation import process_image


@pytest.fixture(scope="module")
def cleanup_outputs():
    """Fixture to clean up output files after tests."""
    yield
    # Clean up generated files after tests
    if os.path.exists('output/test_output.csv'):
        os.remove('output/test_output.csv')
    if os.path.exists('output/test_output.png'):
        os.remove('output/test_output.png')
    # remove output directory
    if os.path.exists('output'):
        os.rmdir('output')


def test_process_image():  # cleanup_outputs):
    """Test the process_image function with a small test image."""
    tiles_x, tiles_y = 100, 100

    available_colors = {
        "red_0": (255, 200, 200),
        "red_1": (255, 150, 150),
        "red_2": (255, 100, 100),
        "red_3": (255, 50, 50),
        "red_4": (255, 0, 0),
        "blue_0": (200, 200, 255),
        "blue_1": (150, 150, 255),
        "blue_2": (100, 100, 255),
        "blue_3": (50, 50, 255),
        "blue_4": (0, 0, 255),
        # five greys
        "gray_0": (255, 255, 255),
        "gray_1": (192, 192, 192),
        "gray_2": (128, 128, 128),
        "gray_3": (64, 64, 64),
        "gray_4": (0, 0, 0),
        # four greens
        "green_0": (200, 255, 200),
        "green_1": (150, 255, 150),
        "green_2": (100, 255, 100),
        "green_3": (50, 255, 50),


}
    test_input_img = 'img/test_image_flowers.jpeg'
    test_output_csv = 'output/test_output.csv'
    test_output_png = 'output/test_output.png'

    # Ensure output directory exists
    os.makedirs(os.path.dirname(test_output_csv), exist_ok=True)

    # Run image processing
    process_image(
        test_input_img,
        test_output_csv,
        test_output_png,
        tiles_x,
        tiles_y,
        available_colors,
    )

    # Validate CSV output
    assert os.path.exists(test_output_csv), "Mosaic CSV file was not created!"

    mosaic_data = pd.read_csv(test_output_csv, header=None)
    assert mosaic_data.shape == (tiles_y, tiles_x), "Mosaic CSV has incorrect dimensions!"

    # Check that colors are in the available palette
    unique_colors = mosaic_data.values.flatten()
    for color in unique_colors:
        assert color in available_colors, f"Unexpected color '{color}' in mosaic!"

    # Validate PNG output
    assert os.path.exists(test_output_png), "Preview PNG file was not created!"

    from PIL import Image
    preview_img = Image.open(test_output_png)
    assert preview_img.size == (tiles_x * 20, tiles_y * 20), "Preview image has incorrect size!"
