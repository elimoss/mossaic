import pandas as pd

class MosaicDesign:
    """Loads the mosaic design."""
    def __init__(self, file):
        self.design_matrix = pd.read_csv(file, header=None)

    def get_tile_color(self, x, y):
        return self.design_matrix.at[y, x]
