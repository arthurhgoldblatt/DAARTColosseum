import setup_path

import numpy as np
import matplotlib.pyplot as plt
import airsim

# Load topographical data
npz_file = "topographical_data.npz"
data = np.load(npz_file)
x, y, z = data["x"], data["y"], data["z"]

# Center the npz data at (0, 0) beforehand
x_centered = x - (x.max() + x.min()) / 2
y_centered = y - (y.max() + y.min()) / 2

# Define PlayerStart position in AirSim
player_start_x = -42.26017367  # from player start / transform / location in Unreal Engine
player_start_y = 116.27425705

# Load and preprocess data
voxel_resolution = 2  # meters per voxel
x_scaled = x_centered * voxel_resolution
y_scaled = -y_centered * voxel_resolution  # Flip Y-axis

# Shift to align with PlayerStart in AirSim
x_aligned = x_scaled - player_start_x
y_aligned = y_scaled - player_start_y

# Find the Z value at (0, 0) in the aligned coordinates
distances = np.sqrt(x_aligned**2 + y_aligned**2)
closest_idx = np.argmin(distances)
z_at_origin = z[closest_idx]

# Compute the Z adjustment to normalize and scale around -10
z_scaled = z * 2  # Scale Z values by 2
z_shift = z_scaled[closest_idx] - (-10)  # Adjust so that z at (0, 0) becomes -10
z_aligned = z_scaled - z_shift + 3 # add buffer of 3 to avoid collisions

print(f"Z value at (0, 0) before adjustment (scaled): {z_scaled[closest_idx]}")
print(f"Z shift applied: {z_shift}")

# Save updated topographical data
output_file = "aligned_topographical_data.npz"
np.savez(output_file, x=x_aligned, y=y_aligned, z=z_aligned)

# Visualization
fig, ax = plt.subplots(figsize=(10, 8))
sc = ax.scatter(x_aligned, y_aligned, c=z_aligned, cmap="viridis", s=2, label="Topography")
plt.colorbar(sc, label="Elevation")
ax.scatter(0, 0, color="red", label="Player Start", s=50)
ax.set_title("Aligned Topographical Map for AirSim")
ax.set_xlabel("X (AirSim Coordinates)")
ax.set_ylabel("Y (AirSim Coordinates)")
ax.legend()
ax.grid(True)
ax.axis("equal")

# Update coordinate display to include Z
def update_status_bar(event):
    if event.inaxes == ax:
        # Find the closest point to the cursor
        x_mouse, y_mouse = event.xdata, event.ydata
        distances = np.sqrt((x_aligned - x_mouse) ** 2 + (y_aligned - y_mouse) ** 2)
        closest_idx = np.argmin(distances)
        z_value = z_aligned[closest_idx]
        # Update the status bar
        ax.format_coord = lambda x, y: f"X={x:.2f}, Y={y:.2f}, Z={z_value:.2f}"

fig.canvas.mpl_connect("motion_notify_event", update_status_bar)

plt.show()
