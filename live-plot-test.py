#!/usr/bin/python
import time
import threading
import random
import sys, select, os
import pylab
from pylab import *

# size of plot array to keep as we generate new data
num_plotted = 50
num_retained = 1000 # unused at moment
samples_per_s = 20

lock = threading.Lock()


# global index for latest timevalue
data_index = -1

# generate initial x,y data {x,0}
xaxis=pylab.arange(0,num_plotted,1)
yaxis=pylab.array([0]*num_plotted)
xaxis = []
yaxis = []

# create a plot figure, 1 row, 1 col, subplot 1
fig = pylab.figure(1)
ax = fig.add_subplot(1,1,1)
ax.grid(True)
ax.set_title("Realtime Sensor Plot")
ax.set_xlabel("Time")
ax.set_ylabel("Value")
ax.axis([0, num_plotted, -1.5, 1.5])
line1=ax.plot(xaxis,yaxis,'-')

manager = pylab.get_current_fig_manager()

# Global values array will be filled and drawn by timers
values=[]

# This just simulates reading from a sensor
def data_listener():
    global values, data_index, lock, samples_per_s
    while True:
        v = 0
        for i in range(0,5):
            v += random()
        v = v/5.0
        lock.acquire()
        values.append(v)
        data_index += 1
        lock.release()
        time.sleep(1.0/samples_per_s)

def RealtimePlotter():
    global values, data_index, lock
    if (data_index<0):
        return
    lock.acquire()
    min_index = max(data_index + 1 - num_plotted, 0)
    max_index = max(num_plotted, data_index + 1)
    xdata = pylab.arange(min_index, data_index + 1, 1)
    line1[0].set_data(xdata, pylab.array(values[-num_plotted:]))
    lock.release()
    ax.axis([min_index, max_index, -1.5, 1.5])
    manager.canvas.draw()

# disable blocking
pylab.ion()
pylab.show(block=False)

if __name__ == '__main__':
    thread1 = threading.Thread(target=data_listener)
    thread1.daemon = True
    thread1.start()

    try:
        while True:
            RealtimePlotter()
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass

