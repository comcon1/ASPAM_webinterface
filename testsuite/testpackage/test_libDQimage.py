#!/usr/bin/python

import sys,os
sys.path.append('../../package/')
import libDQimage as qi
import libdaq as dq
import numpy as np
from matplotlib.pyplot import *
from matplotlib.mlab import movavg


rotfile = '../patterns/test.rotations'
day_start = '9:00'
day_stop  = '21:00'

ldr = dq.loader.Loader(rotfile)

ip0 = qi.ImageParameters(ldr)
ip0.setDiap(-48*60,-1)
ip0.setFigSize((14,7))

ir = qi.ImageRequest(ldr, ip0)
print 'Check it: ', ir.getImage()
os.system('display '+ir.getImage())

