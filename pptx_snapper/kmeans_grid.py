from typing import Optional

from sklearn.cluster import KMeans
import numpy as np
from .grid import Grid
from .slide import Slide

class KMeansGrid(Grid):
    def __init__(self, slide: Slide, x_depth = -1, y_depth = -1):
        # Initialize with slide dimensions and 0 depth
        super().__init__(slide_width=slide.slide_width, slide_height=slide.slide_height, x_depth=x_depth, y_depth=y_depth)
        self.slide = slide

    def calculate_kmeans_grid(self, anchor_name = "center", axis: str = 'both', n_clusters: Optional[int] = None) -> Grid:
        """
        Convert the clustered positions into a grid using K-means.
        
        Args:
            anchor_name: name of the anchor point
            axis: 'x', 'y', or 'both'. Determines the axis along which clustering is performed.
            n_clusters: Number of clusters (K) for the K-means algorithm. 
                        If None, the number of clusters is optimized based on the number of objects.
        
        Returns:
            A new Grid instance based on the K-means cluster centers.
        """
        # Get the positions of all snappable objects in the slide
        positions = np.array([obj.get_anchor_point(anchor_name=anchor_name) for obj in self.slide.snappable_objects])

        if axis == 'x':
            data = positions[:, 0].reshape(-1, 1)  # Only use x-axis data
        elif axis == 'y':
            data = positions[:, 1].reshape(-1, 1)  # Only use y-axis data
        else:
            data = positions  # Use both x and y axes

        # If n_clusters is not provided, set it to a reasonable value based on object count
        if n_clusters is None:
            n_clusters = min(len(self.slide.snappable_objects) // 3, 10)

        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters)
        kmeans.fit(data)
        cluster_centers = np.sort(kmeans.cluster_centers_.flatten())
        
        
        # Create grid lines from the cluster centers
        if axis == 'x':
            self.x_grid_lines = sorted(set(self.x_grid_lines).union(cluster_centers))
        elif axis == 'y':
            self.y_grid_lines = sorted(set(self.y_grid_lines).union(cluster_centers))
        else:
            # For both axes, split the cluster centers into x and y grid lines
            x_centers, y_centers = zip(*cluster_centers.reshape(-1, 2))
            self.x_grid_lines = sorted(set(self.x_grid_lines).union(x_centers))
            self.y_grid_lines = sorted(set(self.y_grid_lines).union(y_centers))

    
    def to_grid(self):   
        return self.copy()