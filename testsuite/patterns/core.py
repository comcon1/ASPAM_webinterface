'''
 Classes for curve construction.
'''

import numpy as np
import matplotlib.pyplot as pp
from matplotlib.mlab import *

class Params:
    pass

global _p
_p = Params()
_p.minADC  = 0
_p.maxADC  = 4005
_p.stepADC = 1. # DEPRECATED!

class CombinedCurve(object):

    def __init__(self):
        self._data = np.zeros((0,2))
        self._top = None

    def pushCurve(self, curve):
        if self._top == None:
            # first time!
            self._data = np.array(curve.data)
            self._top = np.array(curve.top)
        else:
            ndata = np.array(curve.data)
            ndata[:,0] += -curve.bot[0] + self._top[0]
            ndata[:,1] += -curve.bot[1] + self._top[1]
            self._data = np.vstack((self._data,ndata))
            self._top += np.array(curve.top) - np.array(curve.bot)
        self._electricCut()

    def _electricCut(self):
        self._data[self._data[:,1] > _p.maxADC,1] = _p.maxADC
        self._data[self._data[:,1] < _p.minADC,1] = _p.minADC


    @property
    def data(self):
        return self._data

    @property
    def top(self):
        return self._top


class _CurvePartBase(object):

    def __init__(self, enter_v, leave_v, data):
        self._entV = enter_v
        self._leaV = leave_v
        self._data = data

    @property
    def data(self):
        return self._data

    @property
    def top(self):
        return self._leaV

    @property
    def bot(self):
        return self._entV


class CPInitiator(_CurvePartBase):

    def __init__(self, v, t=0, timestep=1):
        _CurvePartBase.__init__(self, 
                np.array([t,v]), 
                np.array([t+timestep,v]), 
                np.array([[t,v],[t+timestep,v]]))


class CPRefilling(_CurvePartBase):

    def __init__(self, enter_v, leave_v, data, \
            lowbase, dead):
        ''' 
            enter_v, leave_v, data - see base constructor
            lowbase - value of measurer with zero weight 
            dead - time diapasone of measurer with zero weight
        '''
        _CurvePartBase.__init__(self, enter_v, leave_v, data)

        self._lowbase = lowbase
        self._dead = dead

class CPGoods(_CurvePartBase):

    def __init__(self, enter_v, leave_v, data, \
            drinktimes):
        '''
            enter_v, leave_v, data - see base constructor
            drinktimes - iterations of drinking 
        '''
        _CurvePartBase.__init__(self, enter_v, leave_v, data)

        self._drinks = drinktimes


