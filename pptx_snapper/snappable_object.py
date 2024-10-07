from copy import deepcopy
from typing import Any
import numpy as np

from collections import OrderedDict

from numpy.ma.core import shape
from pptx.shapes.base import BaseShape
from pptx.shapes.picture import Picture
from pptx.shapes.group import GroupShape


class SnappableObject:
    def __init__(self, shape: BaseShape, slide_index: int, shape_index: int, is_template:bool = False):
        self.shape = shape
        self.slide_index = slide_index
        self.shape_index = shape_index

        self.is_template = is_template

        self.shape_id = shape.shape_id
        self.name = shape.name
        
        self.is_placeholder = shape.is_placeholder
        self.is_table = shape.has_table
        self.is_chart = shape.has_chart
        self.is_text = shape.has_text_frame
        self.is_picture = isinstance(shape,Picture)
        self.is_group = isinstance(shape,GroupShape)
        
        if self.is_text:
            self.text = shape.text

        self.left = shape.left
        self.top = shape.top
        self.width = shape.width
        self.height = shape.height

        self._left = shape.left
        self._top = shape.top
        self._width = shape.width
        self._height= shape.height

        self._template_snap_id = None  # Initially None, will be set later

        self.snapping_candidates = []


    @property
    def sizes(self) -> np.ndarray:
        return np.array([max(self.width,1), max(self.height,1)])

    @property
    def center(self)->tuple[int,...]:
        return self.left + self.width // 2, self.top + self.height // 2

    @property
    def right(self):
        return self.left + self.width

    @property
    def bottom(self):
        return self.top + self.height

    @property
    def corners(self)-> list[tuple[int,...]]:
        """Calculate the corner points of the object."""
        return [
            (self.left, self.top),  # Top-left
            (self.left + self.width, self.top),  # Top-right
            (self.left, self.top + self.height),  # Bottom-left
            (self.left + self.width, self.top + self.height),  # Bottom-right
        ]

    @property
    def anchor_points(self)->dict[str,tuple[int,...]]:
        corners = self.corners
        
        return OrderedDict({
            "top-left":corners[0],
            "top-right": corners[1],
            "bottom-left": corners[2],
            "bottom-right": corners[3],
            "center": self.center,
        })
        
    def get_anchor_point(self, anchor_name: str) -> tuple[int, int]:
        """Get the position of a named anchor point."""
        return self.anchor_points.get(anchor_name, (None, None))
    
    
    @property
    def area(self):
        return self.width * self.height
    
    @property
    def orig_top(self) -> int:
        return self._top

    @property
    def orig_left(self) -> int:
        return self._left

    @property
    def orig_right(self) -> int:
        return self._left + self._width

    @property
    def orig_bottom(self) -> int:
        return self._top + self._height

    @property
    def orig_width(self) -> int:
        return self._width

    @property
    def orig_height(self) -> int:
        return self._height
    
    @property
    def shape_type(self) -> str:
        shape_type = "Shape"
        if self.is_picture: shape_type = "Picture"
        if self.is_table: shape_type = "Table"
        if self.is_chart: shape_type = "Chart"
        if self.is_text: shape_type = "Text"
        if self.is_group: shape_type = "Group"
        
        return shape_type


    @property
    def template_snap_id(self) -> str:
        return self._template_snap_id

    @template_snap_id.setter
    def template_snap_id(self, value:str):
        self._template_snap_id = value

    def intersection_area(self, other:'SnappableObject') -> float:
        x_left = max(self.left, other.left)
        y_top = max(self.top, other.top)
        x_right = min(self.right, other.right)
        y_bottom = min(self.bottom, other.bottom)

        overlap_width = max(0, x_right - x_left)
        overlap_height = max(0, y_bottom - y_top)

        return overlap_width * overlap_height

    
    def size_match_score(self, other: 'SnappableObject') -> float:
        width_diff = abs(self.width - other.width)
        height_diff = abs(self.height - other.height)
        score = 1 - (width_diff / max(self.width, other.width)) * (height_diff / max(self.height, other.height))
        return max(0, min(1, score))  # Clamp between 0 and 1
    
    
    def dice_coefficient(self, other: 'SnappableObject') -> float:
        intersection_area = self.intersection_area(other)
        if self.area + other.area == 0:
            return 0
        return (2 * intersection_area) / (self.area + other.area)
    
    def overlap_percentage(self, other: 'SnappableObject') -> float:
        intersection_area = self.intersection_area(other)
        min_area = min(self.area, other.area)
        if min_area == 0:
            return 0
        return (intersection_area / min_area) * 100
    
    
    def size_corrected_dice(self, other: 'SnappableObject') -> float:
        """Calculate the size-corrected Dice score between two SnappableObjects."""
        # Compute the area of each object
        area1 = self.area
        area2 = other.area

        # Compute the overlap area between the objects
        overlap_area = self.intersection_area(other)

        # Calculate the standard Dice coefficient
        dice_coefficient = (2 * overlap_area) / (area1 + area2)

        # Calculate the size correction factor
        size_correction = 1 - abs(area1 - area2) / max(area1, area2)

        # Compute the size-corrected Dice score
        size_corrected_dice = dice_coefficient * size_correction

        return size_corrected_dice

    
    def __str__(self) -> str:
        return f"On [Slide {self.slide_index}] Shape with type of '{self.shape_type}' called '{self.name}' @ [{self.left};{self.top}] with size of [{self.width} x {self.height}]"