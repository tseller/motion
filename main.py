#!/usr/bin/env python

import csv, sys, re
import numpy as np
from isometry_H1 import *
import pandas as pd

import statsmodels.api as sm
lowess = sm.nonparametric.lowess

#--- read in data ---------
# since G and A alternate, use the timestamp of G. average all subsequent A's
# until the next G, and advance the result to the leading G's timestamp.

datafile = sys.argv[1] if len(sys.argv) > 1 else 'circle_run.tsv'

#---------------------------------------------
df = pd.io.parsers.read_csv(open(datafile, "rb"), delimiter=' ', names=['time','sensor','x','y','z'])
#df.index = df.pop('time')

subplot_num = 0
df_smooth = {'A': None, 'G': None}
for key, grp in df[10:500].groupby('sensor'):
  time_window_size = 2.0
  frac = time_window_size / (grp.time.max() - grp.time.min())

  # do the smoothing
  lowess_x = lowess(np.array(grp.x), np.array(grp.time), frac=frac)
  lowess_y = lowess(np.array(grp.y), np.array(grp.time), frac=frac)
  lowess_z = lowess(np.array(grp.z), np.array(grp.time), frac=frac)

  # create a dataframe based on the first smoothed series, and then make the 'time' column the index
  df_smooth[key] = pd.DataFrame(lowess_x, columns=['time', key+'_x'])
  df_smooth[key].index = df_smooth[key].pop('time')

  # add the other two smoothed series to the data frame
  df_smooth[key][key+'_y'] = pd.Series([i[1] for i in lowess_y], index=df_smooth[key].index)
  df_smooth[key][key+'_z'] = pd.Series([i[1] for i in lowess_z], index=df_smooth[key].index)

  subplot_num += 1
  plt.figure('moving frame')
  plt.subplot(2,1,subplot_num)
  plt.plot(df_smooth[key])
  plt.title(key)

outfilename = 'img/%s_componentsD.png' % (re.sub("\..*$", "", datafile))
plt.savefig(outfilename)

# merge the 'A' and 'G' smoothed data frames
df = pd.merge(df_smooth['A'], df_smooth['G'], left_index=True, right_index=True, how='outer')
print 'merged!'

# now that the 'A' and 'G' series are merged, there are plenty of gaps, so interpolate
df = df.apply(pd.Series.interpolate)

# calculate the time deltas in a new column
df['time'] = df.index
df['delta_t'] = (df['time']-df['time'].shift()).fillna(0)

# 
c = Configs()
df = df[2:] # THIS IS AD HOC GIVEN MY SAMPLE DATA
df.apply(lambda x: c.addConfig(x['time'], x['delta_t'], H(0.,x['A_x'],x['A_y'],x['A_z']), H(0.,x['G_x'],x['G_y'],x['G_z'])/2.0), axis=1)

c.plotPositionE()
c.plotAccelerationE()
c.plotRotationE()
c.plotComponentsE()
#-----------------------------------------------------
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

  outfilename = 'img/%s_acceleration_filter.png' % (re.sub("\..*$", "", datafile))
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

  outfilename = 'img/%s_rotation_filter.png' % (re.sub("\..*$", "", datafile))
  plt.savefig(outfilename)

#rolling_mean_filter()
