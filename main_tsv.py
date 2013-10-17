#!/usr/bin/env python

import csv, sys
import numpy as np
from isometry_H1 import *
import pandas as pd

import statsmodels.api as sm
lowess = sm.nonparametric.lowess

#--- read in data ---------
# since G and A alternate, use the timestamp of G. average all subsequent A's
# until the next G, and advance the result to the leading G's timestamp.
 
data = []
prev_t = 0
cnt_A = 0
o = {'delta_t': 0., 'acc': np.zeros(3), 'rot': np.zeros(3)}

reader = csv.reader(open('stuff.tsv', "rb"), delimiter=' ')
for row in reader:
  if row[1] == 'G':
    delta_t = float(row[0]) - prev_t if prev_t != 0 else 0
    prev_t = float(row[0])

    o['acc'] /= float(cnt_A)
    cnt_A = 0

    data.append(o)

    o = {'delta_t': delta_t, 'acc': np.zeros(3), 'rot': np.array([float(i) for i in row[2:]])}

  else:
    if prev_t == 0:
      prev_t = float(row[0])

    cnt_A += 1
    o['acc'] += np.array([float(i) for i in row[2:]])

#--------------------------------
def lowess_filter():
  df = pd.io.parsers.read_csv(open('stuff.tsv', "rb"), delimiter=' ', names=['time','sensor','x','y','z'])

  for key, grp in df.groupby('sensor'):
    t = np.array([i for i in grp.time])
    x = np.array([i for i in grp.x])
    y = np.array([i for i in grp.y])
    z = np.array([i for i in grp.z])

    time_window_size = 2.0
    frac = time_window_size / (grp.time.max() - grp.time.min())
    x0 = lowess(x, t, frac=frac)
    y0 = lowess(y, t, frac=frac)
    z0 = lowess(z, t, frac=frac)

    #--- plot ---------
    plt.figure(key)
    plt.subplot(2,1,1)
    plt.plot(t, x)
    plt.plot(t, y)
    plt.plot(t, z)

    plt.subplot(2,1,2)
    plt.plot([i[0] for i in x0], [i[1] for i in x0]) 
    plt.plot([i[0] for i in y0], [i[1] for i in y0]) 
    plt.plot([i[0] for i in z0], [i[1] for i in z0]) 

    outfilename = 'img/%s_lowess_%s.png' % (re.sub("\..*$", "", sys.argv[0]), key)
    plt.savefig(outfilename)

def rolling_mean_filter():
  data2 = [np.append(np.append([d['delta_t']], d['acc']), d['rot']) for d in data]

  df = pd.DataFrame(data2, columns=['delta_t', 'accX', 'accY', 'accZ', 'rotX', 'rotY', 'rotZ'])

  window_size = 15
  signal = pd.rolling_mean(df, window_size)[window_size-1:]
  noise = signal - df[window_size-1:]

  #--- plot acceleration signal and noise --------
  df_acc = df[['accX', 'accY', 'accZ']]
  signal_acc = signal[['accX', 'accY', 'accZ']]
  noise_acc = noise[['accX', 'accY', 'accZ']]

  fig, axes = plt.subplots(nrows=3, ncols=1)
  fig.set_figheight(15)
  fig.set_figwidth(5)
  df_acc.plot(ax=axes[0]); axes[0].set_title('Original Time Series')
  signal_acc.plot(ax=axes[1]); axes[1].set_title('Underlying Signal')
  noise_acc.plot(ax=axes[2]); axes[2].set_title('Noise')
  #fig.tight_layout()

  outfilename = 'img/%s_acceleration_filter.png' % (re.sub("\..*$", "", sys.argv[0]))
  plt.savefig(outfilename)

  #--- plot rotation signal and noise --------
  df_rot = df[['rotX', 'rotY', 'rotZ']]
  signal_rot = signal[['rotX', 'rotY', 'rotZ']]
  noise_rot = noise[['rotX', 'rotY', 'rotZ']]

  fig, axes = plt.subplots(nrows=3, ncols=1)
  fig.set_figheight(15)
  fig.set_figwidth(5)
  df_rot.plot(ax=axes[0]); axes[0].set_title('Original Time Series')
  signal_rot.plot(ax=axes[1]); axes[1].set_title('Underlying Signal')
  noise_rot.plot(ax=axes[2]); axes[2].set_title('Noise')
  #fig.tight_layout()

  outfilename = 'img/%s_rotation_filter.png' % (re.sub("\..*$", "", sys.argv[0]))
  plt.savefig(outfilename)

lowess_filter()
rolling_mean_filter()
'''
window_size = 15
df['gravX'] = pd.Series(pd.rolling_mean(df, window_size)['accX'], index=df.index)
df['gravY'] = pd.Series(pd.rolling_mean(df, window_size)['accY'], index=df.index)
df['gravZ'] = pd.Series(pd.rolling_mean(df, window_size)['accZ'], index=df.index)
'''
#-----------------------------------
c = Configs()
for d in data[0:20]:
  acc = np.insert(d['acc'], 0 ,0)
  rot = np.insert(d['rot'], 0, 0)
  rot = [i/2.0 for i in rot] # quaternions need only _half_ the angle
  c.addConfig(d['delta_t'], H(*acc), H(*rot))

c.plotConfigs()
