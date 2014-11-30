#!/usr/bin/env python

import time
import threading
import random
import sys, select, os
import matplotlib
#matplotlib.use('Agg')
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
samples_per_s = 5

# mutex for sensor thread and graph access to data
lock = threading.Lock()

# detect Lego brick
try:
  brick = nxt.locator.find_one_brick(debug=False)
  print brick
except:
  brick = None
  print "Lego brick not found"
  
  
# ultrasonic sensor
if brick is not None:
  u = nxt.sensor.Ultrasonic(brick, usndport)
  print u

# Touch button
  t = nxt.sensor.Touch(brick, touchport)
  print t

# Sound sensor
  s = nxt.sensor.Sound(brick, soundport)
  print s

# Light sensor
  l = nxt.sensor.Light(brick, lightport)
  l.set_illuminated(True)
  print l
else:
  u = None
  t = None
  s = None
  l = None
  
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

def get_sensor_data():
    global u, s, t, l, l_values, u_values, s_values, t_values, data_index, lock, samples_per_s
    while True: 
      if brick is not None:
        for i in range(0,5):
            val = u.get_sample()
        touch = t.is_pressed()
        snd = s.get_sample()*100.0/255.0
        lght = l.get_lightness()
      else:
        val = 50 + random()*5
        touch = 0
        snd = 10 + random()*5
        lght = 30 + random()*10

      # lock and write data
      lock.acquire()
      u_values.append(val)
      s_values.append(snd)
      l_values.append(lght)
      t_values.append(60 if touch else 40)
      data_index += 1
      lock.release()
      print "\nsound ", snd, "\ndist ", val, "\nbutton ", touch, "\nlight ", lght
      time.sleep(1.0/samples_per_s)

def RealtimePlotter():
    global l_values, u_values, s_values, t_values, data_index, lock, samples_per_s
    if (data_index<0):
        return
    while True:
      lock.acquire()
      min_index = max(data_index + 1 - num_plotted, 0)
      max_index = max(num_plotted, data_index + 1)
      xdata = pylab.arange(min_index, data_index + 1, 1)
      line_u[0].set_data(xdata, pylab.array(u_values[-num_plotted:]))
      line_t[0].set_data(xdata, pylab.array(t_values[-num_plotted:]))
      line_s[0].set_data(xdata, pylab.array(s_values[-num_plotted:]))
      line_l[0].set_data(xdata, pylab.array(l_values[-num_plotted:]))
      lock.release()
      ax.axis([min_index, max_index, 0, 100])
      manager.canvas.draw()
      time.sleep(1.0/samples_per_s)

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
#RealtimePlotter()
#manager.canvas.draw()

if __name__ == '__main__':
  # start a thread which will sample all the lego sensors
  thread1 = threading.Thread(target=get_sensor_data)
  thread1.daemon = True
  thread1.start()
# start a thread which will continuously plot lege sensor data
  thread2 = threading.Thread(target=RealtimePlotter)
  thread2.daemon = True
  thread2.start()

  state = 0
  try:
      while True:
#            RealtimePlotter()
          if brick is not None:
            if (s.get_sample()*100.0/255.0)>99:
                if (state==0):
#                    forward(brick,60,10000)
                    state = 1
                    time.sleep(0.5)
                elif (state==1):
#                    reverse(brick,100,10)
                    state = 0
                    time.sleep(0.5)

  except KeyboardInterrupt:
      pass
