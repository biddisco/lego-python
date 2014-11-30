#!/usr/bin/env python

import time
import threading
import random
import sys, select, os
import pylab
from pylab import *
import nxt
from nxt import *

# always check ports before use
lmotport  = nxt.PORT_A
gmotport  = nxt.PORT_B
rmotport  = nxt.PORT_C
lightport = nxt.PORT_3
usndport  = nxt.PORT_4
touchport = nxt.PORT_1
soundport = nxt.PORT_2

# size of plot array to keep as we generate new data
num_plotted = 100
num_retained = 1000 # unused at moment
samples_per_s = 10

# mutex for sensor thread and graph access to data
lock = threading.Lock()

# detect Lego brick
brick = nxt.locator.find_one_brick(debug=False)
print brick

# ultrasonic sensor
#u = nxt.sensor.Ultrasonic(brick, usndport)

# Touch button
#t = nxt.sensor.Touch(brick, touchport)

# Sound sensor
s = nxt.sensor.Sound(brick, soundport)
print s

# Light sensor
l = nxt.sensor.Light(brick, lightport)
print l

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
line_s=ax.plot([],[],'-')
line_l=ax.plot([],[],'-')

manager = pylab.get_current_fig_manager()

# Global values arrays will be filled and drawn by timers
u_values=[]
t_values=[]
s_values=[]
l_values=[]

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
    global u, s, t, l, l_values, u_values, s_values, t_values, data_index, lock, samples_per_s
    while True:
#        for i in range(0,5):
#            val = u.get_sample()
#        touch = t.is_pressed()
        snd = s.get_sample()*100.0/255.0
        lght = l.get_sample()
        # lock and write data
        lock.acquire()
#        u_values.append(val)
        s_values.append(snd)
        l_values.append(lght)
        print lght
#        t_values.append(60 if touch else 40)
        data_index += 1
        lock.release()
        print snd
#val, touch
        time.sleep(1.0/samples_per_s)

def RealtimePlotter():
    global l_values, u_values, s_values, t_values, data_index, lock, samples_per_s
    if (data_index<0):
        return
    lock.acquire()
    min_index = max(data_index + 1 - num_plotted, 0)
    max_index = max(num_plotted, data_index + 1)
    xdata = pylab.arange(min_index, data_index + 1, 1)
#    line_u[0].set_data(xdata, pylab.array(u_values[-num_plotted:]))
#    line_t[0].set_data(xdata, pylab.array(t_values[-num_plotted:]))
    line_s[0].set_data(xdata, pylab.array(s_values[-num_plotted:]))
    line_l[0].set_data(xdata, pylab.array(l_values[-num_plotted:]))
    lock.release()
#    ax.axis([min_index, max_index, -1.5, 1.5])
    ax.axis([min_index, max_index, 0, 100])
    manager.canvas.draw()

def forward(b, power, time):
    left  = Motor(b, lmotport) 
    right = Motor(b, rmotport)
    both = nxt.SynchronizedMotors(left, right, 0)
    both.turn(power, time, brake=False)

def reverse(b, power, time):
    left  = Motor(b, lmotport) 
    right = Motor(b, rmotport)
    both = nxt.SynchronizedMotors(left, right, 0)
    both.turn(-power, time, brake=False)

# disable blocking
pylab.ion()
pylab.show(block=False)


if __name__ == '__main__':
    thread1 = threading.Thread(target=get_sensor_data)
    thread1.daemon = True
    thread1.start()

    state = 0
    try:
        while True:
            RealtimePlotter()
            if (s.get_sample()*100.0/255.0)>99:
                if (state==0):
                    forward(brick,100,100)
                    state = 1
                    time.sleep(1)
                elif (state==1):
                    reverse(brick,100,100)
                    state = 0
                    time.sleep(1)

    except KeyboardInterrupt:
        pass

