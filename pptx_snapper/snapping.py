from abc import abstractmethod
from typing import Optional
import numpy as np

from .grid import Grid
from .snappable_object import SnappableObject
from .slide import Slide

class SnapCandidate:
    def __init__(self, object: SnappableObject, anchor_name: str, snap_x_position: Optional[int] = None, snap_y_position: Optional[int] = None):
        self.object = object
        self.anchor_name = anchor_name      # Name of the anchor point (e.g., "top-left")
        
        self.anchor_position = object.get_anchor_point(anchor_name)
        
        x = snap_x_position if not isinstance(snap_x_position,type(None)) else self.anchor_position[0]
        y = snap_y_position if not isinstance(snap_y_position,type(None)) else self.anchor_position[1]
        
        self.snap_position = (x,y)    # New snapped position (x, y)

    def __str__(self) -> str:
        return (f"{self.anchor_name} anchor at {self.anchor_position} "
                f"snapped to {self.snap_position}")
        
    @property
    def displacement_vector(self):
        return np.array(self.snap_position) - np.array(self.anchor_position)
    
    @property
    def displacement(self):
        return np.linalg.norm(self.displacement_vector)
    

class Snapping:
    def __init__(self, grid: Grid) -> None:
        self.grid = grid
        
    @abstractmethod
    def snap(self,obj:SnappableObject) -> None:
        pass


class XSnapping(Snapping):
    def __init__(self, grid: Grid):
        super().__init__(grid)

    def snap(self, obj: SnappableObject):
        """Apply x-axis snapping to the object."""
        for anchor_name in obj.snap_candidates.keys():
            closest_x = min(self.grid.x_grid_lines, key=lambda gx: abs(gx - obj.get_anchor_point(anchor_name)[0]))
            obj.snap_candidates[anchor_name] = SnapCandidate(obj, anchor_name, snap_x_position=closest_x)


class YSnapping(Snapping):
    def __init__(self, grid: Grid) -> None:
        super().__init__(grid)

    def snap(self, obj: SnappableObject) -> None:
        """Apply y-axis snapping to the object."""
        for anchor_name in obj.snap_candidates.keys():
            closest_y = min(self.grid.y_grid_lines, key=lambda gy: abs(gy - obj.get_anchor_point(anchor_name)[1]))
            obj.snap_candidates[anchor_name] = SnapCandidate(obj, anchor_name, snap_y_position=closest_y)


class JointSnapping(Snapping):
    def __init__(self, grid: Grid) -> None:
        super().__init__(grid)

    def snap(self, obj: SnappableObject) -> None:
        """Apply simultaneous x and y snapping to the object."""
        for anchor_name in obj.snap_candidates.keys():
            closest_x = min(self.grid.x_grid_lines, key=lambda gx: abs(gx - obj.get_anchor_point(anchor_name)[0]))
            closest_y = min(self.grid.y_grid_lines, key=lambda gy: abs(gy - obj.get_anchor_point(anchor_name)[1]))
            obj.snap_candidates[anchor_name] = SnapCandidate(obj, anchor_name, snap_x_position=closest_x, snap_y_position=closest_y)
        
        
class SnappingManager:
    def __init__(self, slide: Slide, allow_x_snap = True, allow_y_snap = True):
        self.slide = slide    

        self.allow_x_snap = allow_x_snap
        self.allow_y_snap = allow_y_snap
        
        self.x_grid = None
        self.y_grid = None
        self.joint_grid = None
        
        self.snapping_strategies = {}
        
    def _update_strategies(self)-> None:
        self.snapping_strategies = {}
        if isinstance(self.x_grid,Grid):
            self.snapping_strategies["x"] = XSnapping(self.x_grid)
            
        if isinstance(self.y_grid,Grid):
            self.snapping_strategies["y"] = XSnapping(self.y_grid)
            
        if isinstance(self.x_grid,Grid) and isinstance(self.y_grid,Grid):
            x_grid = self.x_grid.get_x_grid()
            y_grid = self.y_grid.get_y_grid()
            
            self.joint_grid = Grid.merge_grids(x_grid, y_grid)
            
            self.snapping_strategies["joint"] = JointSnapping(self.joint_grid)
    
        
    def set_x_grid(self,grid:Grid) -> None:
        self.x_grid = grid
        self._update_strategies()
    
        
    def set_y_grid(self, grid:Grid)-> None:
        self.y_grid = grid
        self._update_strategies()
    
        
    def extend_x_grid(self, grid:Grid)-> None:
        self.x_grid.extend(grid)
        self._update_strategies()
    
    
    def extend_y_grid(self, grid:Grid)-> None:
        self.y_grid.extend(grid)
        self._update_strategies()
    
    
    def apply_snapping(self, obj: SnappableObject, strategy_type: str):
        """Apply the given snapping strategy (x, y, or joint)."""
        strategy = self.snapping_strategies.get(strategy_type)
        if strategy:
            strategy.snap(obj)
    
    