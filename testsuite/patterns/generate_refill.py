#!/usr/bin/python
from numpy import *
from matplotlib.pyplot import *
import pickle

from core import CPRefilling

a = loadtxt('../_rawdata/colsep10-15.dat')
brds = [ [394500, 396000],
         [627600, 627800],
         [1240000,1242000],
         [1620000,1623000] ]
shifts = [-409, +16, +160, -1065]
ends   = [540, 92, 630, 1900]
rbords = [139, 49, 345, 1602]
i = 0
refil_list = []
for b in brds:
    yy = a[b[0]:b[1],1]
    xx = a[b[0]:b[1],0]
    xx = xx - xx.mean() - shifts[i]
    _b = xx.searchsorted(-126)
    _e = xx.searchsorted(ends[i])
    xx = xx[_b:_e]
    yy = yy[_b:_e]
    # creating object
    enter_point =  [ xx[0], yy[0:5].mean() ]
    finish_point = [ xx[-1], yy[-5:].mean() ]
    final_data = vstack((xx,yy)).T
    dead_diap = [ 0, rbords[i] ]
    lowbase = yy[xx.searchsorted(dead_diap[0])+10 :\
            xx.searchsorted(dead_diap[1])-10].mean()
    obj = CPRefilling(enter_point, finish_point,
            final_data, dead_diap, lowbase) 
    refil_list.append(obj)
    plot(xx, yy, '-', label=str(i), lw=2)
    plot(xx, ones(len(yy))*lowbase, 'k--')
    plot(xx, ones(len(yy))*enter_point[1], 'k:')
    plot(xx, ones(len(yy))*finish_point[1], 'k-')
    i += 1

legend()
show()

f = open('refillings.bin', 'w')
pickle.dump(refil_list, f, 2)
f.close()
print 'Reffiling pattern lists was serialized.'

