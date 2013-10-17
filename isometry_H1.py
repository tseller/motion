#!/usr/bin/env python

import sys, re
import datetime as dt

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import numpy as np
from quaternion import Quaternion as H
#-------------------------------------

class Config:
  def __init__(self, delta_t, a_f, r_f, a_i=H(), v_i=H(), p_i=H(), r_i=H(), o_i=H(1,0,0,0)):
    self.delta_t = delta_t

    self.a_i = a_i # initial acceleration of primed origin wrt unprimed origin
    self.v_i = v_i # initial velocity of primed origin wrt unprimed origin
    self.p_i = p_i # initial location of primed origin wrt unprimed origin
    self.r_i = r_i # initial rotational velocity of primed coords wrt unprimed coords
    self.o_i = o_i # initial orientation of primed coords wrt unprimed coords

    self.a_f = a_f # final acceleration of primed origin wrt unprimed origin
    self.r_f = r_f # final rotational velocity of primed coords wrt unprimed coords

    self.updateOrientation()
    self.updatePosition()

  def updatePosition(self):
    self.a_f = self.o_i * self.a_f * ~self.o_i
    self.v_f = self.v_i + (self.a_i + self.a_f)/2.0 * self.delta_t
    self.p_f = self.p_i + (self.v_i + self.v_f)/2.0 * self.delta_t

  def updateOrientation(self):
    # r_n units are radians per second.
    # to get the current orientation, exponentiate the _previous_ rotational rate
    # for a time of self.delta_t, starting from the previous orientation
    self.o_f = ((self.r_i * self.delta_t).exp() * self.o_i).normalize()

  def getInitialConfig(self):
    return (self.a_i, self.v_i, self.p_i, self.r_i, self.o_i)

  def getFinalConfig(self):
    return (self.a_f, self.v_f, self.p_f, self.r_f, self.o_f)

  def setFinalConfig(self, a_f, v_f, p_f, r_f, o_f):
    self.a_f = a_f
    self.v_f = v_f
    self.v_f = p_f
    self.r_f = r_f
    self.o_f = o_f

  def printConfig(self):
    print 'a_i: %s' % (self.a_i)
    print 'v_i: %s' % (self.v_i)
    print 'p_i: %s' % (self.p_i)
    print 'r_i: %s' % (self.r_i)
    print 'o_i: %s' % (self.o_i)
    print 'a_f: %s' % (self.a_f)
    print 'v_f: %s' % (self.v_f)
    print 'p_f: %s' % (self.p_f)
    print 'r_f: %s' % (self.r_f)
    print 'o_f: %s' % (self.o_f)

#===============================================
class Configs:
  def __init__(self, a_f=H(), v_f=H(), p_f=H(), r_f=H(), o_f=H(1,0,0,0)):
    self.aConfigs = []
    initConfig = Config(0, H(), H())
    initConfig.setFinalConfig(a_f, v_f, p_f, r_f, o_f)
    self.aConfigs.append(initConfig)

  def addConfig(self, delta_t, a_f, r_f):
    finalConfig = self.aConfigs[len(self.aConfigs)-1].getFinalConfig()

    self.aConfigs.append(Config(delta_t, a_f, r_f, *finalConfig))

  def cancelGravity(self):
    window_size = 15

    self.gravity = H()

    for c in self.aConfigs:
      self.gravity += c.a_f

    self.gravity /= float(len(self.aConfigs))

  def plotConfigs(self):
    x_axis = H(0,1,0,0)
    y_axis = H(0,0,1,0)
    z_axis = H(0,0,0,1)

    fig = plt.figure()
    ax = Axes3D(fig)

    # plot boundaries, so that all axes are on the same scale
    max_edge = max([max(c.p_f.x, c.p_f.y, c.p_f.z) for c in self.aConfigs])
    min_edge = min([min(c.p_f.x, c.p_f.y, c.p_f.z) for c in self.aConfigs])
    ax.scatter(min_edge, min_edge, min_edge)
    ax.scatter(max_edge, max_edge, max_edge)

    # plot path
    ax.plot([c.p_f.x for c in self.aConfigs], [c.p_f.y for c in self.aConfigs], [c.p_f.z for c in self.aConfigs])

    for c in self.aConfigs:
      ax.scatter([c.p_f.x], [c.p_f.y], [c.p_f.z], c='r')
    '''
    # plot moving frames
    for c in self.aConfigs:
      x_frame = c.p_f + c.o_f * x_axis * ~c.o_f * 100.0
      y_frame = c.p_f + c.o_f * y_axis * ~c.o_f * 100.0
      z_frame = c.p_f + c.o_f * z_axis * ~c.o_f * 100.0

      ax.plot([c.p_f.x, x_frame.x], [c.p_f.y, x_frame.y], [c.p_f.z, x_frame.z], c='r')
      ax.plot([c.p_f.x, y_frame.x], [c.p_f.y, y_frame.y], [c.p_f.z, y_frame.z], c='g')
      ax.plot([c.p_f.x, z_frame.x], [c.p_f.y, z_frame.y], [c.p_f.z, z_frame.z], c='b')
      #plt.plot([x_frame.x, c['p'].x, y_frame.x], [x_frame.y, c['p'].y, y_frame.y])
    '''
    plt.axis('equal')
    #outfilename = 'img/motion_%s.png' % (re.sub("\..*$", "", sys.argv[1]))
    outfilename = 'img/motion_%s.png' % (re.sub("\..*$", "", sys.argv[0]))
    plt.savefig(outfilename)
