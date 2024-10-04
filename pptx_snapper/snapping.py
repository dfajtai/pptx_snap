from abc import abstractmethod
from typing import Optional
import numpy as np

from .grid import Grid
from .snappable_object import SnappableObject
from .slide import Slide

class SnapCandidate:
    def __init__(self, object: SnappableObject, anchor_name: str, snap_type:str, grid_type:str, snap_x_position: Optional[int] = None, snap_y_position: Optional[int] = None):
        self.object = object
        self.anchor_name = anchor_name      # Name of the anchor point (e.g., "top-left")
        self.snap_type = snap_type
        self.grid_type = grid_type
        
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
    def snap(self,obj:SnappableObject, grid_type:str) -> None:
        pass


class XSnapping(Snapping):
    def __init__(self, grid: Grid):
        super().__init__(grid)
        self.snap_type = "x"

    def snap(self, obj: SnappableObject, grid_type:str):
        """Apply x-axis snapping to the object."""
        for anchor_name in obj.anchor_points.keys():
            closest_x = min(self.grid.x_grid_lines, key=lambda gx: abs(gx - obj.get_anchor_point(anchor_name)[0]))
            obj.snapping_candidates.append(SnapCandidate(obj, anchor_name, snap_x_position=closest_x,
                                                         snap_type = self.snap_type,
                                                         grid_type=grid_type))


class YSnapping(Snapping):
    def __init__(self, grid: Grid) -> None:
        super().__init__(grid)
        self.snap_type = "y"

    def snap(self, obj: SnappableObject, grid_type:str) -> None:
        """Apply y-axis snapping to the object."""
        for anchor_name in obj.anchor_points.keys():
            closest_y = min(self.grid.y_grid_lines, key=lambda gy: abs(gy - obj.get_anchor_point(anchor_name)[1]))
            obj.snapping_candidates.append(SnapCandidate(obj, anchor_name, snap_y_position=closest_y,
                                                         snap_type = self.snap_type,
                                                         grid_type=grid_type))


class JointSnapping(Snapping):
    def __init__(self, grid: Grid) -> None:
        super().__init__(grid)
        self.snap_type = "joint"

    def snap(self, obj: SnappableObject, grid_type:str) -> None:
        """Apply simultaneous x and y snapping to the object."""
        for anchor_name in obj.anchor_points.keys():
            closest_x = min(self.grid.x_grid_lines, key=lambda gx: abs(gx - obj.get_anchor_point(anchor_name)[0]))
            closest_y = min(self.grid.y_grid_lines, key=lambda gy: abs(gy - obj.get_anchor_point(anchor_name)[1]))
            obj.snapping_candidates.append(SnapCandidate(obj, anchor_name, snap_x_position=closest_x, snap_y_position=closest_y,
                                                         snap_type = self.snap_type,
                                                         grid_type=grid_type))
        
        
class SnappingManager:
    def __init__(self, allow_x_snap = True, allow_y_snap = True):  

        self.allow_x_snap = allow_x_snap
        self.allow_y_snap = allow_y_snap
        
        self.x_grid = None
        self.y_grid = None
        self.joint_grid = None
        
        self.snapping_strategies = {}
        
        
    def _update_strategies(self)-> None:
        self.snapping_strategies = {}
        if isinstance(self.x_grid,Grid) and self.allow_x_snap:
            self.snapping_strategies["x"] = XSnapping(self.x_grid)
            
        if isinstance(self.y_grid,Grid) and self.allow_y_snap:
            self.snapping_strategies["y"] = XSnapping(self.y_grid)
            
        if isinstance(self.x_grid,Grid) and isinstance(self.y_grid,Grid) and self.allow_x_snap and self.allow_y_snap:
            x_grid = self.x_grid.get_x_grid()
            y_grid = self.y_grid.get_y_grid()
            
            self.joint_grid = Grid.merge_grids(x_grid, y_grid)
            
            self.snapping_strategies["joint"] = JointSnapping(self.joint_grid)
    
    
    def set_joint_grid(self,grid:Grid) -> None:
        assert isinstance(grid,Grid)
        self.x_grid = grid.get_x_grid()
        self.y_grid = grid.get_y_grid()
        self._update_strategies()
            
    def set_x_grid(self,grid:Grid) -> None:
        assert isinstance(grid,Grid)
        self.x_grid = grid
        self._update_strategies()
    
        
    def set_y_grid(self, grid:Grid)-> None:
        assert isinstance(grid,Grid)
        self.y_grid = grid
        self._update_strategies()
    
        
    def extend_x_grid(self, grid:Grid)-> None:
        assert isinstance(grid,Grid)
        self.x_grid.extend(grid)
        self._update_strategies()
    
    
    def extend_y_grid(self, grid:Grid)-> None:
        assert isinstance(grid,Grid)
        self.y_grid.extend(grid)
        self._update_strategies()
    
    
    def calculate_candidates_for_all_obj(self, slide:Slide, strategy_type: str, flush = False, grid_type:str = "unknown"):
        """Apply the given snapping strategy (x, y, or joint) for all SnappableObject on a given Slide"""
        assert isinstance(slide,Slide)
        
        for so in slide.snappable_objects:
            self.calculate_candidates(so,strategy_type=strategy_type,flush=flush, grid_type= grid_type)
            
    
    def calculate_candidates(self, obj: SnappableObject, strategy_type: str, flush = False, grid_type:str = "unknown"):
        """Apply the given snapping strategy (x, y, or joint) for a given SnappableObject"""
        assert isinstance(obj,SnappableObject)
        
        strategy = self.snapping_strategies.get(strategy_type)
        if strategy:
            if isinstance(strategy,Snapping):
                if flush:
                    obj.snapping_candidates.clear()
                    
                strategy.snap(obj,grid_type=grid_type)
    
    