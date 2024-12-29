import setup_path

import numpy as np
import binvox_rw

def load_binvox(file_path):
    """Load a .binvox file and return the voxel grid as a numpy array."""
    with open(file_path, 'rb') as f:
        model = binvox_rw.read_as_3d_array(f)
    return model

def voxel_to_topographical_data(voxel_data):
    """Convert voxel data to a format usable for visualization."""
    points = []
    for x in range(voxel_data.data.shape[0]):
        for y in range(voxel_data.data.shape[1]):
            for z in range(voxel_data.data.shape[2]):
                if voxel_data.data[x, y, z]:  # Active voxel
                    points.append((x, y, z))
    return np.array(points).T  # shape (3, number_of_points) -> [x_array, y_array, z_array]

def rotate_90_clockwise(x, y, z):
    """
    Rotate the (x, y, z) coordinates by 90 degrees clockwise in the x-y plane.
    That means:
        new_x = old_y
        new_y = -old_x
        new_z = old_z
    """
    new_x = y
    new_y = -x
    new_z = z
    return new_x, new_y, new_z

def save_topographical_data(file_path, x, y, z):
    """Save the topographical data to a numpy file."""
    np.savez(file_path, x=x, y=y, z=z)

if __name__ == "__main__":
    voxel_file = "environment_voxel.binvox"  # Input voxel file
    output_file = "topographical_data.npz"   # Output numpy file

    print(f"Loading voxel file: {voxel_file}")
    voxel_data = load_binvox(voxel_file)
    print("Processing voxel data...")

    x, y, z = voxel_to_topographical_data(voxel_data)

    # Rotate 90 degrees clockwise in the x-y plane
    x_rot, y_rot, z_rot = rotate_90_clockwise(x, y, z)

    print(f"Saving rotated data to {output_file}")
    save_topographical_data(output_file, x_rot, y_rot, z_rot)
    print("Done.")
