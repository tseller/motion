#!/usr/bin/env python

import csv
import numpy as np
from isometry_H1 import *
import pandas as pd

#--- read in data ---------
# since G and A alternate, use the timestamp of G. average all subsequent A's
# until the next G, and advance the result to the leading G's timestamp.
 
data = []
prev_t = 0
cnt_A = 0
#o = {'delta_t': 0, 'acc': np.array([0.0,0.0,0.0]), 'rot': np.array([0.0,0.0,0.0])}
o = {'delta_t': 0, 'accX': 0, 'accY': 0, 'accZ': 0, 'rotX': 0, 'rotY': 0, 'rotZ': 0}

# WHY DO I NEED TO INITIALIZE ARRAYS TO [0.0, 0.0, 0.0] RATHER THAN [0,0,0]?
reader = csv.reader(open('stuff.tsv', "rb"), delimiter=' ')
for row in reader:
  if row[1] == 'G':
    delta_t = float(row[0]) - prev_t if prev_t != 0 else 0
    prev_t = float(row[0])

    #o['acc'] /= float(cnt_A)
    o['accX'] /= float(cnt_A)
    o['accY'] /= float(cnt_A)
    o['accZ'] /= float(cnt_A)
    cnt_A = 0

    data.append(o)

    #o = {'delta_t': delta_t, 'acc': np.array([0.0,0.0,0.0]), 'rot': np.array([float(i) for i in row[2:]])}
    o = {'delta_t': delta_t, 'accX': 0, 'accY': 0, 'accZ': 0, 'rotX': float(row[2]), 'rotY': float(row[3]), 'rotZ': float(row[4])}

  else:
    if prev_t == 0:
      prev_t = float(row[0])

    cnt_A += 1
    #o['acc'] += np.array([float(i) for i in row[2:]])
    o['accX'] += float(row[2])
    o['accY'] += float(row[3])
    o['accZ'] += float(row[4])

#--------------------------------
df = pd.DataFrame(data)

window_size = 15
df['gravX'] = pd.Series(pd.rolling_mean(df, window_size)['accX'], index=df.index)
df['gravY'] = pd.Series(pd.rolling_mean(df, window_size)['accY'], index=df.index)
df['gravZ'] = pd.Series(pd.rolling_mean(df, window_size)['accZ'], index=df.index)

c = Configs()
#for d in data[window_size-1:]:
for d in df.index[window_size-1:50]:
  acc = [0, df.accX.ix[d] - df.gravX.ix[d], df.accY.ix[d] - df.gravY.ix[d], df.accZ.ix[d] - df.gravZ.ix[d]]
  #acc = [0, d['accX'], d['accY'], d['accZ']]
  rot = [0, df.rotX.ix[d], df.rotY.ix[d], df.rotZ.ix[d]]
  #d['acc'] = np.insert(d['acc'], 0 ,0)
  #d['rot'] = np.insert(d['rot'], 0, 0)
  rot = [i/2.0 for i in rot] # quaternions need only _half_ the angle
  c.addConfig(df.delta_t.ix[d], H(*acc), H(*rot))

c.plotConfigs()
