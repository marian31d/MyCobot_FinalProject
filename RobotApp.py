import math
import json
import socket
import threading
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import mainthread
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from pymycobot.mycobot280 import MyCobot280
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import StringProperty, ObjectProperty

Config.set('graphics', 'width', '800')  # Set fixed width
Config.set('graphics', 'height', '600')  # Set fixed height

from robot_client import RobotClient


class RobotGUI(BoxLayout):
    pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.client = RobotClient()
        self.robot_powered_on = False

        # Start the periodic position update
        Clock.schedule_interval(self.monitor_checkbox_state, 0.5)  # Update every 0.5 seconds

        # scrollview for points
        self.popup_height = 0
        self.saved_points = {}  # Dictionary to store saved points
        self.toggleable_box = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=30,
            padding=(0, 0, 0, 0),
            spacing=10
        )

        self.list = Popup(content=self.toggleable_box,
                          title='', background='',
                          separator_color=[0, 0, 0, 0], title_size='0sp',
                          size_hint=(0.07, None), height=self.toggleable_box.height + 30,
                          pos_hint={'right': 0.23, 'top': 0.93}, padding=(0, 0, 0, 0))


    @mainthread
    def Homing(self):
        self.reset_stop_flag()
        self.client.execute("self.mc.send_angles([0, 0, 0, 0, 0, 0], 20)")

    def toggle_power(self, button):

        if button.state == 'down':  # If button is pressed and in 'down' state (Power Off)
            self.robot_powered_on = False
            button.background_normal = 'poweroff.png'  # Update to "Power Off" image
            button.background_down = 'poweroff.png'  # Update while pressed
            self.client.execute("self.mc.power_off()")  # Turn off the robot

        else:  # If button is not pressed (Power On)
            self.robot_powered_on = True
            button.background_normal = 'poweron.png'  # Update to "Power On" image
            button.background_down = 'poweron.png'  # Update while pressed
            self.client.execute("self.mc.power_on()")
            # Turn on the robot

    def move1_left(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            self.client.execute("self.mc.jog_increment_angle(1,2,20)")

    def move1_right(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            self.client.execute("self.mc.jog_increment_angle(1,-2,20)")

    def move2_right(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            self.client.execute("self.mc.jog_increment_angle(2,-2,20)")

    def move2_left(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            self.client.execute("self.mc.jog_increment_angle(2,2,20)")

    def move3_right(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            self.client.execute("self.mc.jog_increment_angle(3,-2,20)")

    def move3_left(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            self.client.execute("self.mc.jog_increment_angle(3,2,20)")

    def move4_right(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            self.client.execute("self.mc.jog_increment_angle(4,-2,20)")

    def move4_left(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            self.client.execute("self.mc.jog_increment_angle(4,2,20)")

    def move5_right(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            self.client.execute("self.mc.jog_increment_angle(5,-2,20)")

    def move5_left(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            self.client.execute("self.mc.jog_increment_angle(5,2,20)")

    def move6_up(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            self.client.execute("self.mc.jog_increment_angle(6,-2,20)")

    def move6_down(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            coords = self.client.execute("self.mc.jog_increment_angle(6,2,20)")

    def release_arms(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            coords = self.client.execute("self.mc.release_all_servos()")

    def open_gripper(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            coords = self.client.execute("self.mc.set_gripper_value(60, 20, 4)")

    def close_gripper(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            coords = self.client.execute("self.mc.set_gripper_value(0, 20, 4)")

    def axis_x_positive(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            response = self.client.execute("self.mc.get_coords()")
            coords = json.loads(response)
            updated_coords = f"self.mc.send_coords([{coords[0] + 3}, {coords[1]}, {coords[2]}, {coords[3]}, {coords[4]}, {coords[5]}], 10, 0)"
            self.client.execute("{}".format(updated_coords))

    def axis_y_positive(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            response = self.client.execute("self.mc.get_coords()")
            coords = json.loads(response)
            updated_coords = f"self.mc.send_coords([{coords[0]}, {coords[1] + 3}, {coords[2]}, {coords[3]}, {coords[4]}, {coords[5]}], 10, 0)"
            self.client.execute("{}".format(updated_coords))

    def axis_z_positive(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            response = self.client.execute("self.mc.get_coords()")
            coords = json.loads(response)
            updated_coords = f"self.mc.send_coords([{coords[0]}, {coords[1]}, {coords[2] + 3}, {coords[3]}, {coords[4]}, {coords[5]}], 10, 0)"
            self.client.execute("{}".format(updated_coords))

    def axis_x_negative(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            response = self.client.execute("self.mc.get_coords()")
            coords = json.loads(response)
            updated_coords = f"self.mc.send_coords([{coords[0] - 3}, {coords[1]}, {coords[2]}, {coords[3]}, {coords[4]}, {coords[5]}], 10, 0)"
            self.client.execute("{}".format(updated_coords))

    def axis_y_negative(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            response = self.client.execute("self.mc.get_coords()")
            coords = json.loads(response)
            updated_coords = f"self.mc.send_coords([{coords[0]}, {coords[1] - 3}, {coords[2]}, {coords[3]}, {coords[4]}, {coords[5]}], 10, 0)"
            self.client.execute("{}".format(updated_coords))

    def axis_z_negative(self):
        if self.robot_powered_on:
            self.reset_stop_flag()
            response = self.client.execute("self.mc.get_coords()")
            coords = json.loads(response)
            updated_coords = f"self.mc.send_coords([{coords[0]}, {coords[1]}, {coords[2] - 3}, {coords[3]}, {coords[4]}, {coords[5]}], 10, 0)"
            self.client.execute("{}".format(updated_coords))

    def update_position(self, dt):
        """
        Periodically check if the robot is moving and update the position fields.
        """

        if self.robot_powered_on:

            try:
                response = self.client.execute("self.mc.get_coords()")
                coords = json.loads(response)
                if coords:
                    # Update the GUI fields with the latest coordinates
                    self.ids.x.text = f"{coords[0]:.1f}"
                    self.ids.y.text = f"{coords[1]:.1f}"
                    self.ids.z.text = f"{coords[2]:.1f}"
                    self.ids.rx.text = f"{coords[3]:.1f}"
                    self.ids.ry.text = f"{coords[4]:.1f}"
                    self.ids.rz.text = f"{coords[5]:.1f}"



            except Exception as e:
                print(f"Error fetching robot coordinates: {e}")

    def SavePoint(self):
        self.reset_stop_flag()
        self.axis_labels = ['x', 'y', 'z', 'rx', 'ry', 'rz']
        self.axis_inputs = {}
        self.axis_inputs['x'] = float(self.ids.x.text)
        self.axis_inputs['y'] = float(self.ids.y.text)
        self.axis_inputs['z'] = float(self.ids.z.text)
        self.axis_inputs['rx'] = float(self.ids.rx.text)
        self.axis_inputs['ry'] = float(self.ids.ry.text)
        self.axis_inputs['rz'] = float(self.ids.rz.text)
        for value in self.axis_inputs.values():
            if value == '\0':
                self.show_popup("Error", "Please fill all axis inputs.")
                return
        if not self.ids.number.text.isdigit():
            self.show_popup("Error", "Please enter a valid point number.")
            return
        point_number = self.ids.number.text
        self.saved_points[point_number] = self.axis_inputs
        self.save_saved_points_to_json()
        if point_number not in [btn.text for btn in self.toggleable_box.children]:
            self.new_button = Button(
                # id=point_number,
                text=point_number,
                size_hint=(1, None),
                pos_hint={'center_x': 0.5, 'center_y': 1},
                height=20,
                color=(0, 0, 0, 1),
                background_color=(1, 1, 1, 0),
                on_press=lambda btn: self.handle_button_click(btn, point_number),
            )
            self.popup_height += 1
            self.toggleable_box.height = 30 * self.popup_height
            self.toggleable_box.add_widget(self.new_button)
            self.toggleable_box.pos = (self.list.pos[0], self.list.pos[1] + 5)
            self.ids.number.text = ""

    def save_saved_points_to_json(self):
        """Save the saved points to a JSON file."""
        with open('saved_points.json', 'w') as json_file:
            json.dump(self.saved_points, json_file)

    def DeletePoint(self):
        self.reset_stop_flag()
        if not self.ids.number.text.isdigit():
            self.show_popup("Error", "Please enter a valid point number.")
            return
        point_number = self.ids.number.text
        for btn in self.toggleable_box.children:
            if point_number == btn.text:
                self.toggleable_box.remove_widget(btn)
                del self.saved_points[point_number]
        self.popup_height -= 1
        self.toggleable_box.height = 30 * self.popup_height
        self.toggleable_box.pos = (self.list.pos[0], self.list.pos[1] + 5)
        self.ids.number.text = ""


    def toggle_points_list(self, instance):
        if self.popup_height:
            self.reset_stop_flag()
            if self.popup_height == 1:
                self.list.height = self.toggleable_box.height + 30
            else:
                self.list.height = self.toggleable_box.height
            self.list.open()
            self.list.pos = (
                Window.width * 0.3 - self.list.width / 2,  # Horizontal position
                Window.height * 0.88 - self.list.height,  # Vertical position
            )
        instance.state = "normal"

    def show_popup(self, title, message):
        popup_content = BoxLayout(orientation="vertical")
        popup_label = Label(text=message)
        close_button = Button(text="Close", size_hint_y=None, height=40)
        popup_content.add_widget(popup_label)
        popup_content.add_widget(close_button)
        popup = Popup(title=title, content=popup_content, size_hint=(0.4, 0.4), separator_color=[1, 1, 1, 1])
        close_button.bind(on_release=popup.dismiss)
        popup.open()

    def handle_button_click(self, instance, point_number):
        self.list.dismiss()
        self.ids.number.text = point_number
        if self.ids.input_coords.active:
            self.ids.x.text = str(self.saved_points[point_number]['x'])
            self.ids.y.text = str(self.saved_points[point_number]['y'])
            self.ids.z.text = str(self.saved_points[point_number]['z'])
            self.ids.rx.text = str(self.saved_points[point_number]['rx'])
            self.ids.ry.text = str(self.saved_points[point_number]['ry'])
            self.ids.rz.text = str(self.saved_points[point_number]['rz'])

    def monitor_checkbox_state(self, dt):
        checkbox = self.ids.input_coords
        if checkbox.active:
            Clock.unschedule(self.update_position)  # Stop updates if checked
        else:
            Clock.schedule_once(self.update_position)

    def robot_pos(self, instance):
        self.ids.number.disabled = False
        self.ids.x.disabled = True
        self.ids.y.disabled = True
        self.ids.z.disabled = True
        self.ids.rx.disabled = True
        self.ids.ry.disabled = True
        self.ids.rz.disabled = True

    def input_pos(self, instance):
        self.ids.number.disabled = True
        self.ids.x.disabled = False
        self.ids.y.disabled = False
        self.ids.z.disabled = False
        self.ids.rx.disabled = False
        self.ids.ry.disabled = False
        self.ids.rz.disabled = False

    def move_linear(self):
        if self.ids.input_coords.active:
            self.reset_stop_flag()
            x = float(self.ids.x.text)
            y = float(self.ids.y.text)
            z = float(self.ids.z.text)
            rx = float(self.ids.rx.text)
            ry = float(self.ids.ry.text)
            rz = float(self.ids.rz.text)
            coords = [x, y, z, rx, ry, rz]
            print(coords)
            self.client.execute("self.mc.send_coords({}, 10, 1)".format(coords))
        elif self.ids.robot_coords.active:
            point_number = self.ids.number.text
            if point_number in self.saved_points.keys():
                x = self.saved_points[point_number]['x']
                y = self.saved_points[point_number]['y']
                z = self.saved_points[point_number]['z']
                rx = self.saved_points[point_number]['rx']
                ry = self.saved_points[point_number]['ry']
                rz = self.saved_points[point_number]['rz']
                coords = [x, y, z, rx, ry, rz]
                self.client.execute("self.mc.send_coords({}, 10, 1)".format(coords))
            else:
                self.show_popup("Error", "Point doess not exist.")

    def move_nonlinear(self):
        if self.ids.input_coords.active:
            self.reset_stop_flag()
            x = float(self.ids.x.text)
            y = float(self.ids.y.text)
            z = float(self.ids.z.text)
            rx = float(self.ids.rx.text)
            ry = float(self.ids.ry.text)
            rz = float(self.ids.rz.text)
            coords = [x, y, z, rx, ry, rz]
            self.client.execute("self.mc.send_coords({}, 10, 0)".format(coords))
        elif self.ids.robot_coords.active:
            point_number = self.ids.number.text
            if point_number in self.saved_points.keys():
                x = self.saved_points[point_number]['x']
                y = self.saved_points[point_number]['y']
                z = self.saved_points[point_number]['z']
                rx = self.saved_points[point_number]['rx']
                ry = self.saved_points[point_number]['ry']
                rz = self.saved_points[point_number]['rz']
                coords = [x, y, z, rx, ry, rz]
                self.client.execute("self.mc.send_coords({}, 10, 0)".format(coords))
            else:
                self.show_popup("Error", "Point doess not exist.")

    def stop_robot(self):
        """
        Triggers the stop functionality in the robot client.
        """
        try:
            self.client.stop_task()
            self.show_popup("Success", "Robot operations halted.\nplease stop any running program first\nand press the homming button or \nany of the moving arrows to reset")
        except Exception as e:
            self.show_popup("Error", f"Failed to stop robot: {e}")

    def reset_stop_flag(self):
        """
        Resets the stop flag to allow further commands to execute.
        """
        if self.client.stop_flag:
            self.client.reset_stop()
            print("Stop flag reset automatically.")


class RobotApp(App):
    def build(self):
        self.robot_gui = RobotGUI()
        return self.robot_gui

    def get_robot_controller(self):
        return self.robot_gui.mc  # Expose the MyCobot280 instance


if __name__ == "__main__":
    app = RobotApp()
    app.run()

    # Safely access mc after app.run()
    mc = app.get_robot_controller()