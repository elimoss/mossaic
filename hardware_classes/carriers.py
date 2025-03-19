import pandas as pd
import numpy as np
from .tile import Tile

class SourceTileCarrier:
    """3D stacked tile source enforcing LIFO removal order."""
    def __init__(self, name, color, position, width, depth, height, tile_size, tile_spacing):
        self.name = name
        self.color = color
        self.position = position
        self.width = width
        self.depth = depth
        self.height = height
        self.tile_size = tile_size
        self.tile_spacing = tile_spacing

        self.stack = [pd.DataFrame(np.full((depth, width), Tile(color, tile_size), dtype=object)) for _ in range(height)]

    def get_tile_position(self, x, y):
        return (self.position[0] + x * self.tile_spacing[0], self.position[1] + y * self.tile_spacing[1])

    def remove_tile(self, x, y):
        for z in reversed(range(self.height)):
            if self.stack[z].at[y, x] is not None:
                tile = self.stack[z].at[y, x]
                self.stack[z].at[y, x] = None
                return tile
        raise ValueError("No tile available at this position.")

class DestinationTileCarrier:
    """Represents the final mosaic grid."""
    def __init__(self, position, width, height, tile_size, tile_spacing):
        self.position = position
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tile_spacing = tile_spacing
        self.grid = pd.DataFrame(np.full((height, width), None, dtype=object))

    def get_tile_position(self, x, y):
        return (self.position[0] + x * self.tile_spacing[0], self.position[1] + y * self.tile_spacing[1])

    def place_tile(self, tile, x, y):
        if self.grid.at[y, x] is None:
            self.grid.at[y, x] = tile
        else:
            raise ValueError("Tile already placed at this position.")
