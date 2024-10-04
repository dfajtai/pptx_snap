
import numpy as np

class Grid:
    def __init__(self, slide_width, slide_height, x_depth=0, y_depth=0):
        self.slide_width = slide_width
        self.slide_height = slide_height
        self.x_depth = x_depth
        self.y_depth = y_depth
        self.x_grid_lines = self.calculate_grid_lines(self.slide_width, self.x_depth)
        self.y_grid_lines = self.calculate_grid_lines(self.slide_height, self.y_depth)

    def calculate_grid_lines(self, axis_length, depth) -> list[int]:
        """Recursively calculate grid lines based on depth level."""
        
        if depth == -1: # no grid at all if depth is -1
            return set()
        
        grid_lines = {0, axis_length}  # Start with borders
        self.recursively_add_grid_lines(grid_lines, 0, axis_length, depth)
        return sorted(grid_lines)
    

    def recursively_add_grid_lines(self, grid_lines, start, end, depth) -> None:
        """Recursively divide the segment between start and end by powers of 2."""
        if depth == 0:
            return
        midpoint = (start + end) // 2
        grid_lines.add(midpoint)
        self.recursively_add_grid_lines(grid_lines, start, midpoint, depth - 1)
        self.recursively_add_grid_lines(grid_lines, midpoint, end, depth - 1)


    def snap_to_grid(self, x, y) -> tuple[int,int]:
        """Snap the given x, y coordinates to the nearest grid points."""
        nearest_x = self.find_nearest(self.x_grid_lines, x)
        nearest_y = self.find_nearest(self.y_grid_lines, y)
        return nearest_x, nearest_y

    def find_nearest(self, grid_lines, value) -> int:
        """Find the nearest value in the grid lines."""
        array = np.array(grid_lines)
        idx = (np.abs(array - value)).argmin()
        return array[idx]

    def add_custom_x_grid_line(self, custom_x) -> None:
        """Add a custom X grid line and keep the list sorted."""
        self.x_grid_lines = sorted(set(self.x_grid_lines).union({custom_x}))

    def add_custom_y_grid_line(self, custom_y) -> None:
        """Add a custom Y grid line and keep the list sorted."""
        self.y_grid_lines = sorted(set(self.y_grid_lines).union({custom_y}))

    def extend(self, other_grid):
        """Extend the current grid with another grid's lines."""
        assert isinstance(other_grid,Grid)
        
        if self.slide_width != other_grid.slide_width:
            raise ValueError(f"Cannot add grids: Slide widths differ (this: {self.slide_width}, other: {other_grid.slide_width}).")

        if self.slide_height != other_grid.slide_height:
            raise ValueError(f"Cannot add grids: Slide widths differ (this: {self.slide_height}, other: {other_grid.slide_height}).")
        
        self.x_grid_lines = sorted(set(self.x_grid_lines).union(other_grid.x_grid_lines))
        self.y_grid_lines = sorted(set(self.y_grid_lines).union(other_grid.y_grid_lines))
        self.x_depth = max(self.x_depth, other_grid.x_depth)
        self.y_depth = max(self.y_depth, other_grid.y_depth)
        

    def get_x_grid(self):
        x_grid = self.copy()
        x_grid.y_grid_lines = []
        return x_grid
    
    def get_y_grid(self):
        y_grid = self.copy()
        y_grid.x_grid_lines = []
        return y_grid
    
    def copy(self):
        new_grid = Grid(self.slide_width,self.slide_height,self.x_depth,self.y_depth)
        new_grid.x_grid_lines = [gl for gl in self.x_grid_lines]
        new_grid.y_grid_lines = [gl for gl in self.y_grid_lines]
        
        return new_grid
    
    @classmethod
    def merge_grids(cls, grid_1, grid_2):
        assert isinstance(grid_1,Grid)
        assert isinstance(grid_2,Grid)
        
        merged_grid = grid_1.copy()
        merged_grid.extend(grid_2)
        return merged_grid
    
    def __str__(self) -> str:
        return (f"Grid with x depth {self.x_depth}, y depth {self.y_depth}:\n"
                f"X grid lines: {self.x_grid_lines}\n"
                f"Y grid lines: {self.y_grid_lines}")
        
        
