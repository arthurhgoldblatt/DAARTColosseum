import setup_path

import airsim
import os
import numpy as np
import cv2
import time
from ultralytics import YOLO
from PIL import Image
from datetime import datetime
import keyboard  # For capturing keyboard input

# Path to the fire segmentation model
MODEL_PATH = "C:\\Users\\agoldblatt.ea\\source\\repos\\daart\\fire_segmentation\\runs\\segment\\train\\weights\\best.pt"

# Output directory for detection images
NO_FIRE_DIR = "C:\\Users\\agoldblatt.ea\\source\\repos\\daart\\airsim_drone_fire_detection\\no_fire_detected\\"
os.makedirs(NO_FIRE_DIR, exist_ok=True)
OUTPUT_DIR = "C:\\Users\\agoldblatt.ea\\source\\repos\\daart\\airsim_drone_fire_detection\\fire_detected\\"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize YOLO model
model = YOLO(MODEL_PATH)

# Initialize AirSim client
client = airsim.MultirotorClient()
client.confirmConnection()

# List of drones
drones = ["Drone0", "Drone1", "Drone2"]

# Initialize and arm drones
for drone in drones:
    client.enableApiControl(True, drone)
    client.armDisarm(True, drone)
    client.takeoffAsync(vehicle_name=drone).join()

# Function to capture an image from the drone and process it
def detect_fire(client, drone_name):
    responses = client.simGetImages([
        airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)
    ], vehicle_name=drone_name)

    if responses:
        # Convert image data to NumPy array
        img1d = np.frombuffer(responses[0].image_data_uint8, dtype=np.uint8)
        img_bgr = img1d.reshape(responses[0].height, responses[0].width, 3)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)  # Convert to RGB

        # # Display the image in OpenCV window
        # cv2.imshow(f"{drone_name} - Captured Image", img_rgb)
        # cv2.waitKey(1)  # Small delay for the display to update

        # Convert image to Pillow format
        img_pil = Image.fromarray(img_rgb)

        # Ensure Pillow image is RGB
        if img_pil.mode != "RGB":
            img_pil = img_pil.convert("RGB")

        # Save image to "no_fire_detected" folder
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = os.path.join(NO_FIRE_DIR, f"{drone_name}_{timestamp}.png")
        img_pil.save(filepath)

        # Run inference
        results = model(img_pil)

        # Check if fire is detected (example condition based on results)
        for result in results:
            if len(result.boxes) > 0 and any(box.conf > 0.6 for box in result.boxes):  # Assuming fire is detected if any bounding boxes exist
                save_detection_image(img_pil, drone_name, result, client.simGetVehiclePose(vehicle_name=drone_name).position)
                return True

    return False

# Function to save detection image
def save_detection_image(image, drone_name, result, position):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    x, y, z = position.x_val, position.y_val, position.z_val
    filename = f"{drone_name}_{timestamp}_x{x:.2f}_y{y:.2f}_z{z:.2f}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Draw boxes on the image (if needed, modify as per YOLO result API)
    result.save(filename=filepath)

# Main function for the drones to search for fire
try:
    for drone in drones:
        client.moveToPositionAsync(0,0,-2,40, vehicle_name=drone).join()
        print(f"{drone} is searching for fire...")
        found_fire = False
        while not found_fire:
            # Move drone to a random position for scanning
            x, y, z = np.random.uniform(-10, 10), np.random.uniform(-100, -10), np.random.uniform(-20, 5)
            print(f"{drone} moving to position: x={x:.2f}, y={y:.2f}, z={z:.2f}")
            client.moveToPositionAsync(x, y, z, 40, vehicle_name=drone).join()

            # Detect fire
            found_fire = detect_fire(client, drone)

            if found_fire:
                print(f"Fire detected by {drone} at position x={x:.2f}, y={y:.2f}, z={z:.2f}!")

            # Check for keyboard interrupt to reset
            if keyboard.is_pressed('r'):
                print("Reset command received. Resetting all drones.")
                break

except KeyboardInterrupt:
    print("KeyboardInterrupt detected. Resetting all drones.")

# Land and disarm drones
for drone in drones:
    client.landAsync(vehicle_name=drone).join()
    client.armDisarm(False, drone)
    client.enableApiControl(False, drone)

print("All drones have been reset and disarmed. Exiting script.")