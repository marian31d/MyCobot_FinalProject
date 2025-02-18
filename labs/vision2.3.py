from robot_client import RobotClient
import vision
import json
import time
client = RobotClient(host="localhost", port=5000)


def main():
    # vision.savePic()
    # crop = vision.Crop()

    camera_p1, camera_p2, camera_p3, camera_p4 = [556, 296], [192, 274], [72, 161], [586, 189]
    robot_p1, robot_p2, robot_p3, robot_p4 = (
        [262.7, 94, 156, -171.8, -0.2, -57.4],
        [233.1, -153.1, 156, -171.8, 0.3, -110.4],
        [142, -240.1, 156, -171.8, -0.1, -136.5],
        [185.6, 130.7, 151.3, -171.7, 0.1, -39],
    )
    M = client.calibrate(camera_p1, camera_p2, camera_p3, camera_p4,
                         robot_p1, robot_p2, robot_p3, robot_p4)
    input_image_path = "saved_image.jpg"  # Replace with your image path
    cropped_image_path = "cropped_image.jpg"  # Path to save the cropped region
    # Create an instance of the Crop class
    num_contours=2

     # Detect contours for two objects in the cropped region
    contour_tool = vision.Crop(path=cropped_image_path, n=num_contours)
    contour_tool.main(input_image_path, cropped_image_path)
    contour_tool.compute()  # Detect contours in the cropped region

    contour_tool.show()  # Display results

    client.load_saved_points()

    coords = list(client.saved_points['1'].values())
    client.saved_points['2'] = {'x': coords[0], 'y':coords[1], 'z':coords[2] , 'rx':coords[3], 'ry':coords[4], 'rz':coords[5]}
    client.save_saved_points_to_json()
    # robot.teach_relative_xyz_position(2, 0, 0, 10, 0, 0, 1)
    crds2 = list(client.saved_points['2'].values())
    # crds = robot.get_position_coordinates(2)
    fm = contour_tool.get_cm()

    print(fm)
    for i in range(2):
        crds = client.transform([fm[i][0], fm[i][1]], M)
        client.saved_points['3'] = {'x': crds[0], 'y': crds[1], 'z': crds2[2], 'rx': crds2[3], 'ry': crds2[4],
                                    'rz': crds2[5]}
        client.save_saved_points_to_json()
        # robot.teach_absolute_xyz_position(3, fm.cms.x, fm.cms.y, crds[2] + 10, crds[3], crds[4])
        crds3 = list(client.saved_points['3'].values())
        client.execute("self.mc.send_coords({}, 10, 0)".format(crds3))
        time.sleep(5)
        # robot.move(3)
        client.execute("self.mc.set_gripper_value(60, 20, 4)")
        # robot.open_gripper()
        client.saved_points['4'] = {'x': crds3[0], 'y': crds3[1], 'z': crds3[2]-30, 'rx': crds3[3], 'ry': crds3[4],
                                    'rz': crds3[5]}
        client.save_saved_points_to_json()
        # robot.teach_relative_xyz_position(4, 0, 0, -10, 0, 0, 3)
        crds4 = list(client.saved_points['4'].values())
        client.execute("self.mc.send_coords({}, 10, 0)".format(crds4))
        time.sleep(5)
        # robot.move(4)
        client.execute("self.mc.set_gripper_value(0, 20, 4)")
        time.sleep(1)
        # robot.close_gripper()
        client.execute("self.mc.send_coords({}, 10, 0)".format(crds3))
        time.sleep(2)
        # robot.move(3)
        client.execute("self.mc.send_coords({}, 10, 0)".format(crds2))
        time.sleep(2)
        # robot.move(2)
        client.execute("self.mc.send_coords({}, 10, 0)".format(coords))
        # robot.move(1)
        client.execute("self.mc.set_gripper_value(60, 20, 4)")
        client.execute("self.mc.send_angles([0, 0, 0, 0, 0, 0], 20)")
        time.sleep(1)
        client.execute("self.mc.set_gripper_value(0,20,4)")

    # robot.open_gripper()


if __name__ == '__main__':
    main()