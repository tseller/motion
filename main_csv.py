import csv, sys
import numpy as np
from isometry_H1 import *
import pandas as pd
'''
#--- detect gravity ---------
gravity = np.array([0,0,0])
cnt = 0

reader = csv.reader(open(sys.argv[1], "rb"))
reader.next()
for row in reader:
  gravity += np.array([float(i) for i in row[1:4]])
  cnt += 1

gravity /= float(cnt)
'''
#--- read the data ---------------------------
aData = []

#reader = csv.reader(open(sys.argv[1], "rb"))
reader = csv.reader(open('data.csv', "rb"))
reader.next()
for row in reader:
  # data is presumed to be in the format: deltaT, accX, accY, accZ, rotX, rotY, rotZ
  delta_t = float(row[0])

  acc = [float(i) for i in row[1:4]]
  acc.insert(0,0)

  # divide the angular velocity by 2
  # since we'll turn this into a quaternion.
  rot = [float(i)/2 for i in row[4:7]]
  rot.insert(0,0)

  aData.append({'delta_t': delta_t, 'acc': acc, 'rot': rot})


c = Configs()
for d in aData:
  c.addConfig(d['delta_t'], H(*d['acc']), H(*d['rot']))

c.plotConfigs()

#--- preprocess the data ----------------------------
window_size = 10
df = pd.io.parsers.read_csv('data.csv')
#df = pd.DataFrame(aData)
signal = pd.rolling_mean(df, window_size)[window_size-1:]
noise = signal - df[window_size-1:]
#--- convert the preprocessed data into configurations ------------------
