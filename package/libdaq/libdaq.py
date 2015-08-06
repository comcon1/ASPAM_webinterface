#!/usr/bin/python

import numpy as np 
from matplotlib.mlab import *
from loader import Loader
from refils import RefillDetector
import timeutils as tmu
import os


class RawCurveAnalyzer(object):

    def __init__(self, fname):
        print 'Raw Curve Analyzer starts.'
        self._fname = fname
        try:
            s = os.stat(self._fname)
        except OSError:
            print 'No such file!'
            return
        print 'Analyzing file: %s (%.1f Kb)' % (self._fname, s.st_size/1024.)
        self._ldr = Loader(self._fname)
        self._rfl = None

    def getData(self, start, stop, skip=1):
        '''Use -1 for start for the beginning and -1 for stop at the very end.
        One can extract skipped data.'''
        p0 = 0 if start == -1 else self._ldr.getPartID(t=start)
        p1 = self._ldr.getNumParts() if stop == -1 else \
            self._ldr.getPartID(t=stop)
        p = np.array([], dtype=self._ldr._p.dtp)
        for j in range(p0, self._ldr.getNumParts()):
            print 'u'
            p0 = self._ldr.getPartNo(j)
            print p.shape, p0.shape
            ind = 0 if not p.shape[0] else \
                    p0['t'][:].searchsorted(p['t'][-1])
            p = np.concatenate( (p, p0[ind::skip] ))
            del p0
        return p

    def getPureData(self, start, stop, skip):
        p = self.getData(start, stop, skip)
        rfl = list(self.detectRefills()[:,0])
        while len(rfl):
            b = rfl.pop()
            a = rfl.pop()
            ia = p['t'].searchsorted(a-20)
            ib = p['t'].searchsorted(b+20)
            p['v'][:ia] -= (p['v'][ia-25:ia-20].mean() - p['v'][ib+20:ib+25].mean())
            print ia,ib
            p = p[list(set(range(p.shape[0]))-set(range(ia,ib)))]
        return p

    @property
    def loader(self):
        return self._ldr

class DrinkCurveAnalyzer(RawCurveAnalyzer):
    
    def detectRefills(self):
        if self._rfl != None:
            return self._rfl
        rfd = RefillDetector(self._ldr)
        sa, sb = rfd.detect_shifts()
        fls = rfd.determine()
        self._rfl = fls
        return fls

class RotCurveAnalyzer(RawCurveAnalyzer):
    '''Class for analyzing data of rat wheel rotations. '''
        
    _cumdata = None
    _rawdata = None
    
    @property
    def rawdata(self):
        if self._rawdata == None:
            rawdata = self.getData(-1,-1)
            print rawdata
            self._rawdata = np.array(rawdata.tolist(), dtype=np.int32)
        return self._rawdata
    
    @property
    def cumdata(self):
        '''Return numerical integral of data'''
        if (self._cumdata == None):
            self._cumdata = np.copy(self.rawdata)
            self._cumdata[:,1:] = np.cumsum(self.rawdata[:,1:], axis=0)
        return self._cumdata 

    def genPartialSums(self, period='h'):
        '''Generate array of sums over hours and days. '''
        pass

    def extractTimePeriod(self, starth, stoph, start, stop):
        '''Generate array of sums over specific period. Period can be
        overnight. ``start'' and ``stop'' have the same meaning as in getData()
        method.'''
        data = self.getData(start, stop)
        ints = tmu.form_periodic_intervals(starth, stoph)
        inds = [ (data['t'].searchsorted(i), data['t'].searchsorted(j)) \
                for i,j in ints ]
        res = zeros(len(inds), dtype=data.dtype)
        res['t'] = [ i for i,j in ints ]
        for field in data.dtype.names[1:]:
            res[field] = [ data[field][i:j].sum() for i,j in inds ]
        return res


    def getData(self, start, stop):
        '''Use -1 for start for the beginning and -1 for stop at the very
        end.'''
        # avoid skipping when analyzing rotations
        return super(RotCurveAnalyzer, self).getData(start, stop, 1)


