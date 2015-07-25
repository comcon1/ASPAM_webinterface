#!/usr/bin/python

import sys
sys.path.append('../../package/')
import libdaq as lq
import numpy as np
from matplotlib.pyplot import *
from matplotlib.mlab import movavg



rca = lq.RawCurveAnalyzer('../patterns/test.curve')
fls = rca.detectRefills()
print fls
a = rca.getData(0, -1, 300)
b = rca.getPureData(0, -1, 300)
subplot(211)
plot(a['t'][:], a['v'][:], '-k', lw=2)
for fl in fls:
    ind = a['t'][:].searchsorted(fl[0])
    plot([ a['t'][ind], a['t'][ind] ], [0, 5000], '--r' if (fl[1]+1) else '--b')
subplot(212)
plot(b['t'][:], b['v'][:], '-k', lw=2)
show(block=False)

figure()
bb = rca.getPureData(0, -1, 1)
mb = movavg(bb['v'], 20)
mt = movavg(bb['t'], 20)

dt = np.gradient(mt)
yy = np.gradient(mb, dt)
plot(movavg(mt, 10)/3600., movavg(yy, 10))
twinx()
plot(mt/3600., mb)
show()
