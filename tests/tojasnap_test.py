import sys
import os

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from pptx_snapper.pptx_reader import PPTXReader
from pptx_snapper.kmeans_grid import KMeansGrid

# Load and read the PowerPoint file
pptx_reader = PPTXReader('examples/KepalkotasTojasnap2024_v241002.pptx')

# Iterate over slides and snappable objects
for slide in pptx_reader.slides:
    print(slide)
    # for obj in slide.snappable_objects:
        # print(obj)
        
    grid = KMeansGrid(slide)
    grid.calculate_kmeans_grid()
    print()
