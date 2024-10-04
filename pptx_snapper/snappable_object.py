from collections import OrderedDict

from pptx.shapes.base import BaseShape
from pptx.shapes.picture import Picture
from pptx.shapes.group import GroupShape

class SnappableObject:
    def __init__(self, shape: BaseShape, slide_index: int):
        self.shape = shape
        self.slide_index = slide_index
        
        self.id = shape.shape_id
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
        
        self.template = None  # Initially None, will be set later
        
        # Calculate center point and corner points
        self.center = (self.left + self.width // 2, self.top + self.height // 2)
        
        self.snapping_candidates = None



    @property
    def corners(self)-> list[tuple[int,int]]:
        """Calculate the corner points of the object."""
        return [
            (self.left, self.top),  # Top-left
            (self.left + self.width, self.top),  # Top-right
            (self.left, self.top + self.height),  # Bottom-left
            (self.left + self.width, self.top + self.height),  # Bottom-right
        ]
    
    @property
    def anchor_points(self)->dict[str,tuple[int,int]]:
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
    def shape_type(self) -> str:
        shape_type = "Shape"
        if self.is_picture: shape_type = "Picture"
        if self.is_table: shape_type = "Table"
        if self.is_chart: shape_type = "Chart"
        if self.is_text: shape_type = "Text"
        if self.is_group: shape_type = "Group"
        
        return shape_type
        
    def __str__(self) -> str:
        return f"On [Slide {self.slide_index}] Shape with type of '{self.shape_type}' called '{self.name}' @ [{self.left};{self.top}] with size of [{self.width} x {self.height}]"