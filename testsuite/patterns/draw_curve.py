#!/usr/bin/python


from core import CombinedCurve,CPInitiator,CPRefilling
from numpy import *
from matplotlib.pyplot import *
import random as rn
import pickle

rn.seed()

cc = CombinedCurve()

cc.pushCurve(CPInitiator(3200.))

f = open('refillings.bin', 'r')
refil_list = pickle.load(f)
f.close()
print 'Reffiling pattern lists was loaded.'
f = open('goods.bin', 'r')
good_list = pickle.load(f)
f.close()
print 'Good-drink pattern lists was loaded.'

for i in range(10):
    jr = rn.randint(0,len(refil_list)-1)
    jg = rn.randint(0,len(good_list)-1)
    cc.pushCurve(refil_list[jr])
    cc.pushCurve(good_list[jg])

print cc.data
print cc.top


plot(cc.data[:,0], cc.data[:,1])
savetxt('test.curve', cc.data, fmt='%10d')
show()
