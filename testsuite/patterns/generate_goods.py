#!/usr/bin/python
from numpy import *
from matplotlib.pyplot import *
import pickle

from core import CPGoods


a = loadtxt('../_rawdata/colsep10-15.dat')
genar = [ [   2100,  430000],
          [ 440000,  697500],
          [ 698000, 1378000],
          [1380000, 1800000] ]

goods_list = []
i = 0
for b in genar:
    _b = a[:,0].searchsorted(b[0])
    _e = a[:,0].searchsorted(b[1])
    xx = a[_b:_e,0]
    yy = a[_b:_e,1]
    xx -= xx[0]
    plot(xx, yy, label=str(i), lw=2)

    enter_point =  [ xx[0], yy[0:5].mean() ]
    finish_point = [ xx[-1], yy[-5:].mean() ]
    final_data = vstack((xx,yy)).T
    dtimes = 0 #TODO: now is zero
    
    obj = CPGoods(enter_point, finish_point,
            final_data, dtimes)
    goods_list.append(obj)
    i+=1

legend()
show()

f = open('goods.bin', 'w')
pickle.dump(goods_list, f, 2)
f.close()
print 'Good drinking pattern lists was serialized.'


