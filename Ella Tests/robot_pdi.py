from turtle import *
import random
import time
from simple_pid import PID


objectMiddle = 70

class robot:
    def __init__(self):
        self.crosshair = objectMiddle # crosshair starts at the middle
    def update(self, steering, dt): # update crosshair location according to pid to steer correctly
        if steering:
            self.crosshair += 1 * steering * dt


if __name__ == '__main__':
    bot = robot()
    crosshair = bot.crosshair

    pid = PID(1, 0.1, 0.05, setpoint=crosshair)
    pid.output_limits = (-100, 100)

    start_time = time.time()
    last_time = start_time

    while time.time() - start_time < 5: # run the thing for some seconds
        current_time = time.time()
        dt = current_time - last_time

        steerPower = pid(crosshair)
        crosshair = bot.update(steerPower, dt)

        last_time = current_time



    #pid.sample_time = 1 # update every second

    speed('slowest')
    teleport(-350, 0)

    change = random.randint(3, 9)
    target = (0, 0)

    for x in range(10):
        fd(50) # go forward
        # change the angle
        if x % 2:
            left(change)
        else:
            right(change)
        # reroll angle for next time
        change = random.randint(3, 9)

    angle = towards(target)
    print(angle) # print angle to target (straight on), if >180, change is to the left, <180 to the right


