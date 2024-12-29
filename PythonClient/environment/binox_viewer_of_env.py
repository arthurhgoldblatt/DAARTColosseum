import setup_path

import numpy as np
import open3d as o3d
import binvox_rw
import airsim
from airsim.types import Vector3r
import os

def generate_voxel_grid(client, output_file, center_position, grid_size_x, grid_size_y, grid_size_z, voxel_resolution):
    """Generate a voxel grid from the AirSim environment."""
    print("Generating voxel grid from AirSim environment...")
    success = client.simCreateVoxelGrid(
        position=center_position,
        x=grid_size_x,
        y=grid_size_y,
        z=grid_size_z,
        res=voxel_resolution,
        of=output_file,
    )
    if success:
        print(f"Voxel grid successfully saved to {output_file}")
    else:
        print("Failed to create voxel grid.")
    return success

def load_binvox(file_path):
    """Load a .binvox file and return the voxel grid as a numpy array."""
    with open(file_path, 'rb') as f:
        model = binvox_rw.read_as_3d_array(f)
    return model

import open3d as o3d
import numpy as np

def create_voxel_grid_with_topography(voxel_data, voxel_size=1.0, interval=5):
    """Create an Open3D voxel grid with topographic line coloring based on Z values."""
    points = []
    colors = []

    # Get the voxel grid dimensions
    shape_x, shape_y, shape_z = voxel_data.data.shape

    # Define a colormap for topographic lines (repeatable pattern)
    colormap = [
        [0.0, 0.0, 1.0],  # Blue
        [0.0, 1.0, 0.0],  # Green
        [1.0, 1.0, 0.0],  # Yellow
        [1.0, 0.5, 0.0],  # Orange
        [1.0, 0.0, 0.0],  # Red
    ]
    num_colors = len(colormap)

    # Create the voxel grid points with topographic coloring
    for x in range(shape_x):
        for y in range(shape_y):
            for z in range(shape_z):
                if voxel_data.data[x, y, z]:
                    points.append([x * voxel_size, y * voxel_size, z * voxel_size])
                    # Assign color based on z level (discrete intervals)
                    level = (z // interval) % num_colors
                    colors.append(colormap[level])

    # Convert points to a PointCloud with colors
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(np.array(points))
    point_cloud.colors = o3d.utility.Vector3dVector(np.array(colors))

    # Create VoxelGrid from the PointCloud
    voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(point_cloud, voxel_size)

    return voxel_grid

def create_voxel_grid_with_contour_lines(voxel_data, voxel_size=1.0, interval=5):
    """Create an Open3D voxel grid with black topographic contour lines over a light gray base."""
    points = []
    colors = []

    # Get the voxel grid dimensions
    shape_x, shape_y, shape_z = voxel_data.data.shape

    # Create the voxel grid points with light gray and contour lines
    for x in range(shape_x):
        for y in range(shape_y):
            for z in range(shape_z):
                if voxel_data.data[x, y, z]:
                    points.append([x * voxel_size, y * voxel_size, z * voxel_size])
                    
                    # Light gray base color
                    base_color = [0.8, 0.8, 0.8]
                    
                    # Add thin black contour lines at interval levels
                    if z % interval == 0:
                        colors.append([0.0, 0.0, 0.0])  # Black for contours
                    else:
                        colors.append(base_color)  # Light gray otherwise

    # Convert points to a PointCloud with colors
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(np.array(points))
    point_cloud.colors = o3d.utility.Vector3dVector(np.array(colors))

    # Create VoxelGrid from the PointCloud
    voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(point_cloud, voxel_size)

    return voxel_grid

def visualize_voxel(file_path):
    """Load a .binvox file and visualize it using Open3D."""
    print(f"Loading .binvox file: {file_path}")
    voxel_data = load_binvox(file_path)

    print(f"Creating Open3D voxel grid for visualization.")
    voxel_grid = create_voxel_grid_with_contour_lines(voxel_data)

    print(f"Displaying voxel grid.")
    o3d.visualization.draw_geometries([voxel_grid])

if __name__ == "__main__":
    # Connect to AirSim
    client = airsim.VehicleClient()
    client.confirmConnection()

    # Define voxel grid parameters
    center_position = Vector3r(0, 0, 0)  # Adjust as needed
    grid_size_x = 1000  # Width in meters
    grid_size_y = 1000  # Depth in meters
    grid_size_z = 200  # Height in meters
    voxel_resolution = 2  # meters per voxel

    # Set output file path relative to current working directory
    output_file = os.path.join(os.getcwd(), "environment_voxel.binvox")  # Output file name

    # Generate the voxel grid
    if generate_voxel_grid(client, output_file, center_position, grid_size_x, grid_size_y, grid_size_z, voxel_resolution):
        # Visualize the voxel grid
        try:
            visualize_voxel(output_file)
        except FileNotFoundError:
            print(f"Error: File {output_file} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
