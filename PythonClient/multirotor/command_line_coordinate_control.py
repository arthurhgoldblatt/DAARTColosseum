import setup_path

import airsim
import argparse
import math
from airsim import Pose, Vector3r, Quaternionr

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Command a drone to fly to specified positions.")
    parser.add_argument("drone_name", type=str, help="Name of the drone (vehicle_name in AirSim).")
    parser.add_argument("--speed", type=float, default=5.0, help="Speed of the drone (default: 5 m/s).")

    args = parser.parse_args()

    # Connect to AirSim
    client = airsim.MultirotorClient()
    client.confirmConnection()

    # Enable API control and arm the drone
    drone = args.drone_name
    client.enableApiControl(True, drone)
    client.armDisarm(True, drone)
    client.takeoffAsync(vehicle_name=drone).join()

    try:
        while True:
            # Get target position from user
            try:
                x = float(input("Enter target X-coordinate (or 'q' to quit): "))
                y = float(input("Enter target Y-coordinate: "))
                z = float(input("Enter target Z-coordinate: "))
            except ValueError:
                print("Exiting the loop.")
                break

            # Reset the camera pose
            forward_pose = Pose(Vector3r(0, 0, 0), Quaternionr(0, 0, 0, 1))  # Default forward-facing pose
            client.simSetCameraPose("front_center", forward_pose, vehicle_name=drone)
            print(f"Resetting 'front_center' camera pose for drone '{drone}'.")

            # Calculate desired yaw
            current_pose = client.simGetVehiclePose(vehicle_name=drone)
            dx = x - current_pose.position.x_val
            dy = y - current_pose.position.y_val
            desired_yaw = math.degrees(math.atan2(dy, dx))

            # Move to position with yaw alignment
            print(f"Sending drone '{drone}' to position ({x}, {y}, {z}) at speed {args.speed} m/s...")
            client.moveToPositionAsync(
                x, y, z, args.speed,
                yaw_mode=airsim.YawMode(is_rate=False, yaw_or_rate=desired_yaw),
                vehicle_name=drone
            ).join()
            print(f"Drone '{drone}' successfully reached the target position.")

    except KeyboardInterrupt:
        print("Exiting due to keyboard interrupt.")

    finally:
        # Disarm and release control
        client.armDisarm(False, drone)
        client.enableApiControl(False, drone)

if __name__ == "__main__":
    main()
