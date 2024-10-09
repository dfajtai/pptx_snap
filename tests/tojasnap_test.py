import sys
import os

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from pptx_snapper.pptx_reader import PPTXReader
from pptx_snapper.snappable_object import SnappableObject
from pptx_snapper.kmeans_grid import KMeansGrid
from pptx_snapper.grid import Grid
from pptx_snapper.snapping import SnappingSearch, SnappingManager
from pptx_snapper.object_recognizer import ObjectRecognizer
from pptx_snapper.templates import ObjectTemplates
from pptx_snapper.utils import AnchorPoint

def test_1():
    # Load and read the PowerPoint file
    pptx_reader = PPTXReader('../examples/KepalkotasTojasnap2024_v241002.pptx')

    if len(pptx_reader.slides)==0:
        return

    basic_grid = Grid(pptx_reader.slide_width,
                      pptx_reader.slide_height,
                      3,3
                      )
    basic_snapping = SnappingSearch()
    basic_snapping.set_joint_grid(basic_grid)

    SnappableObject.active_anchor_points = [AnchorPoint.CENTER]

    # Iterate over slides and snappable objects
    for slide_index, slide in enumerate(pptx_reader.slides):
        print(slide)

        kmeans_grid = KMeansGrid(slide)
        kmeans_grid.calculate_kmeans_grid(anchor_point=AnchorPoint.TOP_LEFT,axis='y')
        
        kmeans_snapping = SnappingSearch()
        kmeans_snapping.set_joint_grid(kmeans_grid)
        

        for obj in slide.snappable_objects:
            print(obj)


        basic_snapping.calculate_candidates_for_all_obj(slide,"x",  grid_type="basic_x")
        # kmeans_snapping.calculate_candidates_for_all_obj(slide,"y",grid_type="kmeans")
        
    SM = SnappingManager(pptx_reader, x_relative_limit=.1, y_relative_limit=.1)
    SM.apply_snaps()
    SM.save_at("../examples/KepalkotasTojasnap2024_v241002_v2.pptx")


def test_2():
    # Load and read the PowerPoint file
    pptx_reader = PPTXReader('../examples/KepalkotasTojasnap2024_v241002.pptx')

    recognizer = ObjectRecognizer.get_size_with_dice_recognizer(1.0,0.8)
    ObjectTemplates.recognize_templates(SnappableObject.catalog, recognizer)


if __name__ == "__main__":
    # test_1()
    test_2()
