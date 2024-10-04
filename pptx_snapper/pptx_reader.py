from pptx import Presentation
from .slide import Slide

class PPTXReader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.presentation = Presentation(file_path)
        
        self.slide_width = self.presentation.slide_width
        self.slide_height = self.presentation.slide_height
    
        self.slides = self.read_slides()

    def read_slides(self):
        """Read all slides and store them as Slide objects."""
        slides = []
        for index, slide in enumerate(self.presentation.slides):
            slides.append(Slide(slide, index,slide_width= self.slide_width, slide_height= self.slide_height))
        return slides