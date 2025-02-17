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

In addition to all the packages in python, you'll need to download the driver of the Robot, instructions on how to do that can be found in the link 
https://docs.elephantrobotics.com/docs/mycobot_280_m5_en/3-FunctionsAndApplications/5.BasicFunction/5.2-Softwarelnstructions/
In the link you can also find instructions on how to get started working with the robot.
The GUI code uses a special font that also should be downloaded, the font is WINGDNG3 it should be copied to the location "Lib > site-packages > kivy > data > fonts" in project folder.

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
