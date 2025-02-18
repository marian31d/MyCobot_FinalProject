import json
import socket
import threading
from pymycobot.mycobot280 import MyCobot280
import os
import atexit  # To automatically clean up on program exit
import numpy as np
import time

class RobotClient:
    # Paths to flag files that track robot initialization and server status
    initialized_flag_file = "robot_initialized.flag"
    server_flag_file = "server_running.flag"
    saved_points_file = "saved_points.json"
    process_counter_file = "process_counter.txt"

    def __init__(self, host="localhost", port=5000):
        # Initialize connection and server address
        self.server_address = (host, port)
        # Increment process counter
        self.increment_process_counter()
        # Initialize the robot at the start
        self.initialize_robot()
        self.stop_flag = False

        # Register the cleanup function to delete the flag files when the program ends
        atexit.register(self.clean_up)

        # Start server in a separate thread if the server flag doesn't exist
        if not self.is_server_running():
            self.set_server_running(True)
            self.server_thread = threading.Thread(target=self.start_server, daemon=True)
            self.server_thread.start()

    def start_server(self):
        """
        Starts the server and listens for incoming commands.
        """
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(self.server_address)
            server.listen(1)
            print(f"Server running on {self.server_address}...")

            while True:
                conn, addr = server.accept()
                command = conn.recv(1024).decode()

                # Stop processing commands if stop_flag is set
                if self.stop_flag:
                    response = json.dumps({"error": "Robot stopped. Command ignored."})
                    conn.send(response.encode())
                    conn.close()
                    continue

                try:
                    # Execute the command
                    result = eval(command)
                    response = json.dumps(result) if result is not None else "Success"
                except Exception as e:
                    response = json.dumps({"error": str(e)})

                conn.send(response.encode())
                conn.close()
        except Exception as e:
            print(f"Error in server: {e}")

    def initialize_robot(self):
        """
        Initializes the robot by creating an instance of MyCobot280.
        This will only happen once, even across multiple processes or threads.
        """
        if not self.is_robot_initialized():
            try:
                # Initialize robot connection
                self.mc = MyCobot280("COM5", 115200)
                self.set_robot_initialized(True)
                print("Robot initialized successfully!")
            except Exception as e:
                print(f"Error initializing robot: {e}")
        else:
            print("Robot has already been initialized.")

    def is_robot_initialized(self):
        """
        Checks if the robot has already been initialized by checking the flag file.
        """
        return os.path.exists(self.initialized_flag_file)

    def set_robot_initialized(self, value):
        """
        Sets the flag file to indicate that the robot has been initialized.
        """
        if value:
            with open(self.initialized_flag_file, 'w') as f:
                f.write("initialized")
        else:
            if os.path.exists(self.initialized_flag_file):
                os.remove(self.initialized_flag_file)

    def is_server_running(self):
        """
        Checks if the server is running by checking the flag file.
        """
        return os.path.exists(self.server_flag_file)

    def set_server_running(self, value):
        """
        Sets the flag file to indicate that the server is running.
        """
        if value:
            with open(self.server_flag_file, 'w') as f:
                f.write("server_running")
        else:
            if os.path.exists(self.server_flag_file):
                os.remove(self.server_flag_file)

    def increment_process_counter(self):
        count = self.get_process_counter()
        with open(self.process_counter_file, 'w') as f:
            f.write(str(count + 1))

    def decrement_process_counter(self):
        count = self.get_process_counter()
        new_count = max(0, count - 1)
        with open(self.process_counter_file, 'w') as f:
            f.write(str(new_count))
        return new_count

    def get_process_counter(self):
        if os.path.exists(self.process_counter_file):
            with open(self.process_counter_file, 'r') as f:
                return int(f.read().strip())
        return 0

    def clean_up(self):
        # Decrement process counter and check if it reaches zero
        remaining_processes = self.decrement_process_counter()
        print(f"Remaining processes: {remaining_processes}")

        if remaining_processes == 0:
            # Cleanup flags and saved points only if no processes are active
            if os.path.exists(self.initialized_flag_file):
                os.remove(self.initialized_flag_file)
                print("Cleanup: Robot flag file removed.")

            if os.path.exists(self.server_flag_file):
                os.remove(self.server_flag_file)
                print("Cleanup: Server flag file removed.")

            if os.path.exists(self.saved_points_file):
                os.remove(self.saved_points_file)
                print("Cleanup: Saved points file removed.")

            if os.path.exists(self.process_counter_file):
                os.remove(self.process_counter_file)
                print("Cleanup: Process counter file removed.")

    def execute(self, command):
        """
        Executes a robot command unless the stop flag is set.
        """
        if self.stop_flag:
            print(f"Command '{command}' ignored because the robot is stopped.")
            return "Command ignored because the robot is stopped."

        if not self.is_robot_initialized():
            return "Robot is not initialized."

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(self.server_address)
            client.send(command.encode())
            response = client.recv(1024).decode()
            client.close()
            return response
        except Exception as e:
            return f"Error: {str(e)}"

    def stop_task(self):
            """
            Immediately stops all robot actions and prevents further commands.
            """
            self.stop_flag = True
            try:
                while self.mc and self.mc.is_moving():
                    self.mc.pause()  # Stop robot movement
                    print("Stopping robot...")
                    time.sleep(0.1)
                print("Robot halted successfully.")
            except Exception as e:
                print(f"Failed to halt robot: {e}")

    def reset_stop(self):
        """
        Resets the stop flag to allow further commands to be executed.
        """
        self.stop_flag = False
        print("Stop flag reset. Commands can now be executed.")

    def load_saved_points(self):
        """Load saved points from a JSON file."""
        try:
            with open('saved_points.json', 'r') as json_file:
                self.saved_points = json.load(json_file)
        except FileNotFoundError:
            print("No saved points found. Starting with an empty set.")
        except json.JSONDecodeError:
            print("Error decoding saved points JSON.")


    def set_saved_points(self, saved_points):
        """Update saved points."""
        self.saved_points = saved_points
        self.save_saved_points_to_json()
    def save_saved_points_to_json(self):
        """Save the saved points to a JSON file."""
        with open('saved_points.json', 'w') as json_file:
            json.dump(self.saved_points, json_file)


    def calibrate(self,camera_p1, camera_p2, camera_p3, camera_p4,
                  robot_p1, robot_p2, robot_p3, robot_p4):
        """
        Calibrates the transformation matrix from camera to robot coordinates.

        Args:
            camera_p1, camera_p2, camera_p3, camera_p4: [x, y] camera coordinates for four points.
            robot_p1, robot_p2, robot_p3, robot_p4: [x, y, z, rx, ry, rz] robot coordinates for four points.

        Returns:
            Transformation matrix M (3x6) that maps camera coordinates to robot coordinates.
        """
        # Combine the input points into arrays
        camera_points = np.array([camera_p1, camera_p2, camera_p3, camera_p4])
        robot_points = np.array([robot_p1, robot_p2, robot_p3, robot_p4])

        # Add a 1 to each camera point to make it homogeneous coordinates
        camera_coords = np.array([[x, y, 1] for x, y in camera_points])  # 4x3 matrix
        robot_coords = np.array(robot_points)  # 4x6 matrix

        # Solve for transformation matrix M using least squares
        M, _, _, _ = np.linalg.lstsq(camera_coords, robot_coords, rcond=None)

        return M

    def transform(self,camera_point, M):

        # Add 1 to the camera point for homogeneous coordinates
        camera_point_h = np.array(camera_point + [1])

        robot_point = np.dot(M.T, camera_point_h)
        return robot_point

    def draw_square_relative(self):

        try:
            # Ensure the robot is in linear interpolation mode
            self.execute("self.mc.set_fresh_mode(0)")  # Linear interpolation
            time.sleep(0.5)

            # Move to initial angles
            initial_angles = [0, -18.9, -61.69, 0, 0, 0]
            self.execute(f"self.mc.send_angles({initial_angles}, 50)")
            print("Robot moved to the initial angles.")
            time.sleep(3)  # Wait for the robot to complete the movement

            # Retrieve the robot's initial coordinates
            response = self.execute("self.mc.get_coords()")
            initial_coords = eval(response) if response else None
            if not initial_coords:
                print("Error: Failed to retrieve robot's initial coordinates.")
                return
            print(f"Initial coordinates: {initial_coords}")

            gcode_movements = [

                [204.06, -18.33, 120.0, initial_coords[3], initial_coords[4], initial_coords[5]],
                [204.06, 40.67, 120.0, initial_coords[3], initial_coords[4], initial_coords[5]],
                [139.06, 40.67, 120.0, initial_coords[3], initial_coords[4], initial_coords[5]],
                [139.06, -18.33, 120.0, initial_coords[3], initial_coords[4], initial_coords[5]],
                [204.06, -18.33, 120.0, initial_coords[3], initial_coords[4], initial_coords[5]],
                [186.56, -0.83, 145.0, initial_coords[3], initial_coords[4], initial_coords[5]],
            ]

            # Execute movements
            for movement in gcode_movements:
                # Send the coordinates to the robot
                self.execute(f"self.mc.send_coords({movement}, 10, 1)")
                time.sleep(3)  # Simulate movement delay

            print("Drawing task completed successfully.")

        except Exception as e:
            print(f"Error in draw_square_relative: {e}")



