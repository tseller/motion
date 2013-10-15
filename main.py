import csv
from isometry_H1 import *

c = Configs()
reader = csv.reader(open("data.csv", "rb"))
reader.next()
for row in reader:
  delta_t = float(row[0])
  acc = [float(i) for i in row[1:4]]
  acc.insert(0,0)
  rot = [float(i)/2 for i in row[4:7]]
  rot.insert(0,0)

  c.addConfig(delta_t, H(*acc), H(*rot))

c.plotConfigs()
