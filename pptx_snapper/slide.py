from pptx.slide import Slide as PptxSlide
from .snappable_object import SnappableObject

class Slide:
    def __init__(self, slide: PptxSlide, slide_index: int, slide_width: int, slide_height: int):
        self.slide = slide
        
        self.slide_index = slide_index
        self.slide_name = slide.name
        
        self.slide_width = slide_width
        self.slide_height = slide_height
        
        self.snappable_objects = self.extract_snappable_objects()

    def extract_snappable_objects(self) -> list[SnappableObject]:
        """Extract snappable objects from the slide."""
        snappable_objects = []
        for shape in self.slide.shapes:
            # Add only visible snappable objects (exclude connectors, invisible shapes, etc.)
            # if not shape.has_text_frame and not shape.is_placeholder:
            snappable_objects.append(SnappableObject(shape, self.slide_index))
        return snappable_objects
    
    def __str__(self) -> str:
        return f"Slide {self.slide_index} with size of [{self.slide_width} x {self.slide_height}] with {len(self.snappable_objects)} SnappableObject"