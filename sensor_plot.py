#!/usr/bin/env python
# Plot a graph of Data which is comming in on the fly
# uses pylab
# Author: Norbert Feurle
# Date: 12.1.2012
# License: if you get any profit from this then please share it with me
import time
import threading
import random
import sys, select, os
import pylab
from pylab import *
import nxt
from nxt import *

# size of plot array to keep as we generate new data
num_plotted = 100
num_retained = 1000 # unused at moment
samples_per_s = 10

# mutex for sensor thread and graph access to data
lock = threading.Lock()

# detect Lego brick
brick = nxt.locator.find_one_brick(debug=False)

# ultrasonic sensor
u = nxt.sensor.Ultrasonic(brick, nxt.PORT_2)

# Touch button
t = nxt.sensor.Touch(brick, nxt.PORT_4)

# global index for latest timevalue
data_index = -1

# create a plot figure, 1 row, 1 col, subplot 1
fig = pylab.figure(1)
ax = fig.add_subplot(1,1,1)
ax.grid(True)
ax.set_title("Lego sensor realtime plot")
ax.set_xlabel("Time")
ax.set_ylabel("Value")
ax.axis([0, num_plotted, 0, 100])
line_u=ax.plot([],[],'-')
line_t=ax.plot([],[],'-')

manager = pylab.get_current_fig_manager()

# Global values arrays will be filled and drawn by timers
u_values=[]
t_values=[]

# This just simulates reading from a sensor
def data_listener():
    global u_values, t_values, data_index, lock, samples_per_s
    while True:
        v = 0
        for i in range(0,5):
            v += random()
        v = v/5.0
        lock.acquire()
        u_values.append(v)
        data_index += 1
        lock.release()
        time.sleep(1.0/samples_per_s)

def get_sensor_data():
    global u, t, u_values, t_values, data_index, lock, samples_per_s
    while True:
        for i in range(0,5):
            val = u.get_sample()
        touch = t.is_pressed()
        # lock and write data
        lock.acquire()
        u_values.append(val)
        t_values.append(60 if touch else 40)
        data_index += 1
        lock.release()
        print val, touch
        time.sleep(1.0/samples_per_s)

def RealtimePlotter():
    global u_values, data_index, lock
    if (data_index<0):
        return
    lock.acquire()
    min_index = max(data_index + 1 - num_plotted, 0)
    max_index = max(num_plotted, data_index + 1)
    xdata = pylab.arange(min_index, data_index + 1, 1)
    line_u[0].set_data(xdata, pylab.array(u_values[-num_plotted:]))
    line_t[0].set_data(xdata, pylab.array(t_values[-num_plotted:]))
    lock.release()
#    ax.axis([min_index, max_index, -1.5, 1.5])
    ax.axis([min_index, max_index, 0, 100])
    manager.canvas.draw()

# disable blocking
pylab.ion()
pylab.show(block=False)

if __name__ == '__main__':
#    thread1 = threading.Thread(target=data_listener)
    thread1 = threading.Thread(target=get_sensor_data)
    thread1.daemon = True
    thread1.start()


    try:
        while True:
            RealtimePlotter()
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass

