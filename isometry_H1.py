#!/usr/bin/env python

import sys, re
import datetime as dt

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import statsmodels.api as sm
lowess = sm.nonparametric.lowess

import numpy as np
from quaternion import Quaternion as H
from scipy.optimize import fmin_cobyla
#-------------------------------------
datafile = sys.argv[1] if len(sys.argv) > 1 else 'circle_run.tsv'
p = re.compile('^(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))')
filename = p.match(datafile).group(2)
#-----------------------------------------------
class Config:
  def __init__(self, t_f, delta_t, delta_a, delta_r, t_i=0, a_i=H(), v_i=H(), p_i=H(), r_i=H(), o_i=H(1,0,0,0)):
    # we integrate the initial coordinates for a time delta_t.
    # the final coordinates are computed here and recorded
    # to become the initial values for the subsequent step.

    # all '*_i' and '*_f' variables are in earth coordinates.
    # the '*_d' varibles are deltas in the moving coordinates of the device.
    # thus, they should be applied to the initial (trans'd) coords to give the final transformed coords.

    self.delta_t = delta_t

    self.t_i = t_i # initial time
    self.a_i = a_i # initial acceleration in transformed coords
    self.v_i = v_i # initial velocity in transformed coords
    self.p_i = p_i # initial location in transformed coords
    self.r_i = r_i # initial rotational velocity in transformed coords
    self.o_i = o_i # initial orientation in transformed coords

    self.t_f = t_f # final time

    self.updateOrientation(delta_r)
    self.updatePosition(delta_a)

  def updatePosition(self, delta_a):
    self.a_f = self.o_f * delta_a * ~self.o_f
    self.v_f = self.v_i + (self.a_i + self.a_f)/2.0 * self.delta_t
    self.p_f = self.p_i + (self.v_i + self.v_f)/2.0 * self.delta_t

  def updateOrientation(self, delta_r):
    # r_n units are radians per second.
    # to get the current orientation, exponentiate the _previous_ rotational rate
    # for a time of self.delta_t, starting from the previous orientation
    self.r_f = (self.o_i * delta_r * ~self.o_i).imag()
    self.o_f = ((self.r_f * self.delta_t).exp() * self.o_i).normalize()

  def getAcceleration(self):
    return self.a_f.as_array()

  def getRotation(self):
    return self.r_f.as_array()

  def getInitialConfig(self):
    return (self.t_i, self.a_i, self.v_i, self.p_i, self.r_i, self.o_i)

  def getFinalConfig(self):
    return (self.t_f, self.a_f, self.v_f, self.p_f, self.r_f, self.o_f)

  def setFinalConfig(self, t_f, a_f, v_f, p_f, r_f, o_f):
    self.t_f = t_f
    self.a_f = a_f
    self.v_f = v_f
    self.v_f = p_f
    self.r_f = r_f
    self.o_f = o_f

  def printConfig(self):
    '''
    print 't_i: %s' % (self.t_i)
    print 'a_i: %s' % (self.a_i)
    print 'v_i: %s' % (self.v_i)
    print 'p_i: %s' % (self.p_i)
    print 'r_i: %s' % (self.r_i)
    print 'o_i: %s' % (self.o_i)
    '''
    print 't_f: %s' % (self.t_f)
    print 'a_f: %s, %s' % (self.a_f, abs(self.a_f))
    print 'v_f: %s, %s' % (self.v_f, abs(self.v_f))
    print 'p_f: %s' % (self.p_f)
    print 'r_f: %s' % (self.r_f)
    print 'o_f: %s' % (self.o_f)

#===============================================
CONST_GRAVITY = 9.78

def objective_gravity(x, d):
  return (np.sum(np.dot(d-x,x))/np.linalg.norm(x))**2

def grav_constraint(x):
  return np.linalg.norm(x) - CONST_GRAVITY

class Configs:

  def __init__(self, t_f=0, a_f=H(), v_f=H(), p_f=H(), r_f=H(), o_f=H(1,0,0,0)):
    self.aConfigs = []
    initConfig = Config(0, 0, H(), H())
    initConfig.setFinalConfig(t_f, a_f, v_f, p_f, r_f, o_f)
    self.aConfigs.append(initConfig)

  def addConfig(self, t_f, delta_t, a_f, r_f):
    initConfig = self.aConfigs[len(self.aConfigs)-1].getFinalConfig()

    self.aConfigs.append(Config(t_f, delta_t, a_f, r_f, *initConfig))

  def setGravity(self):
    window_size = 15
    d = self.aConfigs[len(self.aConfigs)-window_size:]

    def func(x):
      return (np.sum(np.dot(d-x,x))/np.linalg.norm(x))**2

    def constr(x):
      return np.linalg.norm(x) - CONST_GRAVITY

    self.gravity = fmin_cobyla(func, [0., 0., 0.], constr, rhoend=1e-7)

  def plotPositionE(self):
    x_axis = H(0,1,0,0)
    y_axis = H(0,0,1,0)
    z_axis = H(0,0,0,1)

    fig = plt.figure('position')
    ax = Axes3D(fig)

    # plot boundaries, so that all axes are on the same scale
    max_edge = max([max(c.p_f.x, c.p_f.y, c.p_f.z) for c in self.aConfigs[2:]])
    min_edge = min([min(c.p_f.x, c.p_f.y, c.p_f.z) for c in self.aConfigs[2:]])
    ax.scatter(min_edge, min_edge, min_edge)
    ax.scatter(max_edge, max_edge, max_edge)

    ax.scatter(0,0,0, c='white')

    # plot path
    ax.plot([c.p_f.x for c in self.aConfigs[2:]], [c.p_f.y for c in self.aConfigs[2:]], [c.p_f.z for c in self.aConfigs[2:]])

    '''
    for c in self.aConfigs:
      ax.scatter([c.p_f.x], [c.p_f.y], [c.p_f.z], c='r')
    '''
    # plot moving frames
    for c in self.aConfigs[2::10]:
      rescale = 100.0
      x_frame = c.p_f + c.o_f * x_axis * ~c.o_f * rescale
      y_frame = c.p_f + c.o_f * y_axis * ~c.o_f * rescale
      z_frame = c.p_f + c.o_f * z_axis * ~c.o_f * rescale

      ax.plot([c.p_f.x, x_frame.x], [c.p_f.y, x_frame.y], [c.p_f.z, x_frame.z], c='r')
      ax.plot([c.p_f.x, y_frame.x], [c.p_f.y, y_frame.y], [c.p_f.z, y_frame.z], c='g')
      ax.plot([c.p_f.x, z_frame.x], [c.p_f.y, z_frame.y], [c.p_f.z, z_frame.z], c='b')
      #plt.plot([x_frame.x, c['p'].x, y_frame.x], [x_frame.y, c['p'].y, y_frame.y])

    plt.title(filename + ' position, Earth frame')
    plt.axis('equal')
    outfilename = 'img/%s_positionE.png' % (filename)
    plt.savefig(outfilename)
#---------------------------------------------------------
  def plotRotationE(self):
    t = np.array([c.t_f for c in self.aConfigs[2:]])

    # rotation data as an array
    r_x = np.array([c.r_f.x for c in self.aConfigs[2:]])
    r_y = np.array([c.r_f.y for c in self.aConfigs[2:]])
    r_z = np.array([c.r_f.z for c in self.aConfigs[2:]])

    fig = plt.figure('rotation')
    ax = Axes3D(fig)

    # plot boundaries, so that all axes are on the same scale
    max_edge = max(max(r_x), max(r_y), max(r_z))
    min_edge = min(min(r_x), min(r_y), min(r_z))
    ax.scatter(min_edge, min_edge, min_edge)
    ax.scatter(max_edge, max_edge, max_edge)

    ax.scatter(0,0,0, c='white')

    ax.plot(r_x, r_y, r_z)

    plt.title(filename + ' rotation, Earth frame')
    plt.axis('equal')
    outfilename = 'img/%s_rotationE.png' % (filename)
    plt.savefig(outfilename)
#-----------------------------------------------------
  def plotAccelerationE(self):
    t = np.array([c.t_f for c in self.aConfigs[2:]])

    # acceleration data as an array
    a_x = np.array([c.a_f.x for c in self.aConfigs[2:]])
    a_y = np.array([c.a_f.y for c in self.aConfigs[2:]])
    a_z = np.array([c.a_f.z for c in self.aConfigs[2:]])

    fig = plt.figure('acceleration')
    ax = Axes3D(fig)

    # plot boundaries, so that all axes are on the same scale
    max_edge = max(max(a_x), max(a_y), max(a_z))
    min_edge = min(min(a_x), min(a_y), min(a_z))
    ax.scatter(min_edge, min_edge, min_edge)
    ax.scatter(max_edge, max_edge, max_edge)

    ax.scatter(0,0,0, c='white')

    ax.plot(a_x, a_y, a_z)

    plt.title(filename + ' acceleration, Earth frame')
    plt.axis('equal')
    outfilename = 'img/%s_accelerationE.png' % (filename)
    plt.savefig(outfilename)

#-----------------------------------------------------
  def plotVelocityE(self):
    t = np.array([c.t_f for c in self.aConfigs[2:]])

    # acceleration data as an array
    v_x = np.array([c.v_f.x for c in self.aConfigs[2:]])
    v_y = np.array([c.v_f.y for c in self.aConfigs[2:]])
    v_z = np.array([c.v_f.z for c in self.aConfigs[2:]])

    fig = plt.figure('velocity')
    ax = Axes3D(fig)

    # plot boundaries, so that all axes are on the same scale
    max_edge = max(max(v_x), max(v_y), max(v_z))
    min_edge = min(min(v_x), min(v_y), min(v_z))
    ax.scatter(min_edge, min_edge, min_edge)
    ax.scatter(max_edge, max_edge, max_edge)

    ax.scatter(0,0,0, c='white')

    ax.plot(v_x, v_y, v_z)

    plt.title(filename + ' velocity, Earth frame')
    plt.axis('equal')
    outfilename = 'img/%s_velocityE.png' % (filename)
    plt.savefig(outfilename)
#-----------------------------------------------------
  def plotComponentsE(self): 
    #--- plot components ----------------------------
    t = np.array([c.t_f for c in self.aConfigs[2:]])

    # acceleration data as an array
    a_x = np.array([c.a_f.x for c in self.aConfigs[2:]])
    a_y = np.array([c.a_f.y for c in self.aConfigs[2:]])
    a_z = np.array([c.a_f.z for c in self.aConfigs[2:]])
    a_norm = np.array([abs(c.a_f) for c in self.aConfigs[2:]])

    # rotation data as an array
    r_x = np.array([c.r_f.x for c in self.aConfigs[2:]])
    r_y = np.array([c.r_f.y for c in self.aConfigs[2:]])
    r_z = np.array([c.r_f.z for c in self.aConfigs[2:]])
    r_norm = np.array([abs(c.r_f) for c in self.aConfigs[2:]])

    #--- plot components ---------
    plt.figure('earth_frame_components')
    plt.subplot(2,1,1)
    plt.plot(t, a_x, label='X')
    plt.plot(t, a_y, label='Y')
    plt.plot(t, a_z, label='Z')
    plt.plot(t, a_norm, label='Norm')
    plt.legend()
    plt.title(filename + ' acceleration, Earth frame')

    plt.subplot(2,1,2)
    plt.plot(t, r_x, label='X')
    plt.plot(t, r_y, label='Y')
    plt.plot(t, r_z, label='Z')
    plt.plot(t, r_norm, label='Norm')
    plt.legend()
    plt.title(filename + ' rotation, Earth frame')

    outfilename = 'img/%s_componentsE.png' % (filename)
    plt.savefig(outfilename)
