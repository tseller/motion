#!/usr/bin/env python

import sys, re
import datetime as dt

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import numpy as np
#-------------------------------------

class Config:
  def __init__(self):
    self.delta_t = .1

    self.aConfigs = []

    self.p = 0 # location of primed origin wrt unprimed origin
    self.v = 0 # velocity of primed origin wrt unprimed origin
    self.a = 0 # acceleration of primed origin wrt unprimed origin
    self.o = 1 # orientation of primed coords wrt unprimed coords
    self.r = 0 # rotational velocity of primed coords wrt unprimed coords

    self.aConfigs.append({'p': self.p, 'v': self.v, 'a': self.a, 'o': self.o, 'r': self.r})

  def updateConfig(self, a_n, r_n):
    # Upon receiving updated acceleration and rotation data,
    # use this and the previous data to calculate the current position and orientation.
    self.updateOrientation(r_n)
    self.updatePosition(a_n)

    self.aConfigs.append({'p': self.p, 'v': self.v, 'a': self.a, 'o': self.o, 'r': self.r})

  def updatePosition(self, a_n):
    a_n = self.o * a_n
    v_n = self.v + (self.a + a_n)/2.0 * self.delta_t
    p_n = self.p + (self.v + v_n)/2.0 * self.delta_t

    self.a = a_n
    self.v = v_n
    self.p = p_n

  def updateOrientation(self, r_n):
    # r_n units are radians per second.

    #theta = (self.r + r_n)/2.0 * self.delta_t
    theta = self.r * self.delta_t
    self.o = (np.cos(theta) + np.sin(theta) * 1j) * self.o 
    self.o /= abs(self.o)

    self.r = r_n

  def printConfig(self):
    print 'position:\n %s' % (self.p)
    print 'velocity:\n %s' % (self.v)
    print 'acceleration:\n %s' % (self.a)
    print 'orientation:\n %s' % (self.o)
    print 'rotation: %s' % (self.r)


  def plotConfigs(self):
    fig = plt.figure()
    #ax = Axes3D(fig)
    #ax.plot([i['p'][0] for i in self.aConfigs], [i['p'][1] for i in self.aConfigs], [i['p'][2] for i in self.aConfigs])
    #plt.scatter([i['p'].item(0) for i in self.aConfigs], [i['p'].item(1) for i in self.aConfigs])
    for i in self.aConfigs:
      frame_x = i['p'] + i['o']/500.0
      frame_y = i['p'] + i['o']*1j/500.0
      plt.plot([frame_x.real, i['p'].real, frame_y.real], [frame_x.imag, i['p'].imag, frame_y.imag])


    plt.axis('equal')
    outfilename = 'img/%s.png' % (re.sub("\..*$", "", sys.argv[0]))
    plt.savefig(outfilename)
    

c = Config()

c.updateConfig(.1,0)
c.updateConfig(0,0)
c.updateConfig(0,0)
c.updateConfig(0,0)
c.updateConfig(0,0)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)
c.updateConfig(.01j, 1)

c.plotConfigs()
