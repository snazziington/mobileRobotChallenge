#!/usr/bin/env python

import os
import sys
import time
import matplotlib.pyplot as plt
from simple_pid import PID

import turtle as ttl

import random


class WaterBoiler:
    """
    Simple simulation of a water boiler which can heat up water
    and where the heat dissipates slowly over time
    """

    def __init__(self):
        self.water_temp = 20 # starting temp

    def update(self, boiler_power, dt): # update the waterboiler using pid values
        if boiler_power:
            self.water_temp += 1 * boiler_power * dt
        
        # Some heat dissipation
        # self.water_temp -= 0.02 * dt
        return self.water_temp


boiler = WaterBoiler()
water_temp = boiler.water_temp

pid = PID(10, 0.01, 0.1, setpoint=water_temp)
pid.output_limits = (-100, 100)

start_time = time.time()
last_time = start_time

# Keep track of values for plotting
setpoint, y, x = [], [], []

def turt():
    ttl.forward(10)
    if power < 0:
        ttl.right(power)
    elif power > 0:
        ttl.left(power)


while time.time() - start_time < 5: # run the thing for some seconds
    current_time = time.time()
    dt = current_time - last_time

    power = pid(water_temp)
    #turt()

    water_temp = boiler.update(power, dt)

    x += [current_time - start_time]
    y += [water_temp]
    setpoint += [pid.setpoint]

    # pid set point (target) 1s after time has started
    #if current_time - start_time > 1:
        #cs = current_time - start_time
        #while cs < 5:
            #pid.setpoint = (current_time - start_time) * 10
            #pid.setpoint = 80

    # print values for testing
    if current_time - start_time > 1.2:
        print(power)

    if current_time - start_time > 4:
        pid.setpoint = 10
    elif current_time - start_time > 3:
        pid.setpoint = 80
    elif current_time - start_time > 1:
        pid.setpoint = 60
    
    last_time = current_time
        
# plotting
plt.plot(x, y, label='measured')

print(len(y))

plt.plot(x, setpoint, label='target')
plt.xlabel('time')
plt.ylabel('temperature')
plt.legend()
if os.getenv('NO_DISPLAY'):
    # If run in CI the plot is saved to file instead of shown to the user
    plt.savefig(f"result-py{'.'.join([str(x) for x in sys.version_info[:2]])}.png")
else:
    plt.show()