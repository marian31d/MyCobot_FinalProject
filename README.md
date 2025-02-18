# MyCobot_FinalProject
This is a robot-arm communication and graphical user interface code.
below are instructions on how to run the interface and the communication server for MyCobot.

## Installation
In the project we used Python 3.10.7.
The packages used in the code are:
- Kivy
- pip
- pymycobot
- pyserial
- numpy
- opencv
The GUI code uses a special font that should also be downloaded, the font is WINGDNG3 it should be copied to the location "Lib > site-packages > kivy > data > fonts" in project folder.

In addition to all the packages in python, you'll need to download the driver of the Robot, instructions on how to do that can be found in the link:
https://docs.elephantrobotics.com/docs/mycobot_280_m5_en/3-FunctionsAndApplications/5.BasicFunction/5.2-Softwarelnstructions/
Instructions on how to get started working with the robot and to download the API pymycobot mentioned above:
https://docs.elephantrobotics.com/docs/mycobot_280_m5_en/3-FunctionsAndApplications/6.developmentGuide/python/1_download.html

## Robot_client - server
This is the sever that handles the communications to and from the robot.
In order to send commands to the robot, import the class RobotClient 

```bash
from robot_client import RobotClient
```
And then connect to the server by
```bash
client = RobotClient()
```
By using client you can send commands to the robot as a string using the function client.execute()
```bash
client.execute("self.mc.power_on()")
```
**Note:** all the commands to the robot must be in strings, so in order to send a command that uses parameters you should format them into a string. (see the example)
```bash
client.execute("self.mc.send_coords({}, 10, 1)".format(coords))
```
The server also contains two functions in order to calibrate the robot to a camera and transform a point from the camera plain to the robot plain.
```bash
#provide 4 robot plain points (6-axis) and 4 camera plain points (2-axis)
#the function returns the transform matrix M

client.calibrate(camera_p1, camera_p2, camera_p3, camera_p4, robot_p1, robot_p2, robot_p3, robot_p4)

#pass the point from camera plaint you want to transform and the transform matrix M
#returns the point in the robot plain

client.transform(camera_point, M)
```
The points saved by the GUI or by the user can be loaded or saved using the functions 
```bash
client.load_saved_points()

client.set_saved_points(saved_points)

client.save_saved_points_to_json()
```

