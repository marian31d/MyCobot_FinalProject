from robot_client import RobotClient
import time
client = RobotClient()

def getAnumber():
    number = input('enter a number:')
    return number

if __name__ == "__main__":
    for i in range(2):


        client.load_saved_points()
        p0=list(client.saved_points['0'].values())
        print(p0)
        helper1 = f"self.mc.send_coords([{p0[0]}, {p0[1]}, {p0[2]-30}, {p0[3]}, {p0[4]}, {p0[5]}], 20, 1)"
        client.execute("self.mc.set_gripper_value(60,20,4)")
        client.execute(f"self.mc.send_coords({p0},20,1)")
        if i==1: client.execute("{}".format(helper1))
        number = getAnumber()

        client.execute("self.mc.set_gripper_value(0,20,4)")
        time.sleep(1)
        client.execute(f"self.mc.send_coords({p0},20,1)")
        p1 = list(client.saved_points[f'{number}'].values())
        client.execute(f"self.mc.send_coords({p1}, 20, 1)")
        time.sleep(5)
        client.execute("self.mc.set_gripper_value(60,20,4)")
        if i == 1:
            client.execute(f"self.mc.send_coords({p0},20,1)")
            time.sleep(2)
            client.execute("self.mc.set_gripper_value(0,20,4)")
            client.execute("self.mc.send_angles([0, 0, 0, 0, 0, 0], 20)")

