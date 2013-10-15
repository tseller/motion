import math

class Quaternion(object):
  def __init__(self, w=0, x=0, y=0, z=0):
    self.w = w
    self.x = x
    self.y = y
    self.z = z

  def real(self):
    return self.w

  def imag(self):
    return Quaternion(0, self.x, self.y, self.z)

  def norm2(self):
    return self.w**2 + self.x**2 + self.y**2 + self.z**2

  def __abs__(self):
    return math.sqrt(self.norm2())

  def __invert__(self):
    #Conjugate of Quaternion.
    return Quaternion(self.w, -self.x, -self.y, -self.z)

  def __radd__(self,c):
    return Quaternion(c + self.w, self.x, self.y, self.z)

  def __rmul__(self,c):
    return Quaternion(c * self.w, c * self.x, c * self.y, c * self.z)

  def __rdiv__(self,c):
    return (float(c)/self.norm2()) * ~self

  def __neg__(self):
    return -1*self

  def __add__(self, q):
    return Quaternion(
      self.w + q.w,
      self.x + q.x,
      self.y + q.y,
      self.z + q.z,
    )

  def __sub__(self, q):
    return self + (-q)

  def __mul__(self, q):
    return Quaternion(
      self.w*q.w - self.x*q.x - self.y*q.y - self.z*q.z,
      self.w*q.x + self.x*q.w + self.y*q.z - self.z*q.y,
      self.w*q.y - self.x*q.z + self.y*q.w + self.z*q.x,
      self.w*q.z + self.x*q.y - self.y*q.x + self.z*q.w,
    ) if hasattr(q, 'w') else q * self

  def __div__(self, q):
    return self * (1.0 / q) 

  def normalize(self):
    return self / float(abs(self))

  def exp(self):
    imag = self.imag()
    theta = abs(imag)
    unit = imag / theta if theta != 0 else imag

    return math.exp(self.real()) * (Quaternion(math.cos(theta), 0, 0, 0) + math.sin(theta) * unit)

  def imag_as_array(self):
    return [self.x, self.y, self.z]

  def as_tuple(self):
    return (self.w, self.x, self.y, self.z)

  def __str__(self):
    i = '+ %s' % (self.x) if self.x >= 0 else '- %s' % (-self.x)
    j = '+ %s' % (self.y) if self.y >= 0 else '- %s' % (-self.y)
    k = '+ %s' % (self.z) if self.z >= 0 else '- %s' % (-self.z)
    return '(%s %si %sj %sk)' % (self.w, i, j, k)

