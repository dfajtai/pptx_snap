import sys
import os

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from pptx_snapper.pptx_reader import PPTXReader
from pptx_snapper.kmeans_grid import KMeansGrid
from pptx_snapper.grid import Grid
from pptx_snapper.snapping import SnappingManager


def main():
    # Load and read the PowerPoint file
    pptx_reader = PPTXReader('examples/KepalkotasTojasnap2024_v241002.pptx')

    if len(pptx_reader.slides)==0:
        return

    basic_grid = Grid(pptx_reader.slide_width,
                      pptx_reader.slide_height,
                      2,2
                      )
    basic_snapping = SnappingManager()
    basic_snapping.set_joint_grid(basic_grid)
       
    

    # Iterate over slides and snappable objects
    for slide in pptx_reader.slides:
        print(slide)

        kmeans_grid = KMeansGrid(slide)
        kmeans_grid.calculate_kmeans_grid()
        
        kmeans_snapping = SnappingManager()
        kmeans_snapping.set_joint_grid(kmeans_grid)
        
        
        for obj in slide.snappable_objects:
            print(obj)
        
        basic_snapping.calculate_candidates_for_all_obj(slide,"joint",grid_type="basic")    
        kmeans_snapping.calculate_candidates_for_all_obj(slide,"joint",grid_type="kmeans")            
        
        print()


if __name__ == "__main__":
    main()
    
