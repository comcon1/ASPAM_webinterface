# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8

'''
Determine intervals of drinker refill according the following simple algorythm.
The principle schmeme of data is:
                       ,(+) shift
    vvvvvvvv.          .vvvvvvvvvvvv
            |          |
            |vvvvvvvvvv|
  (-) shift'

All (-) and (+) shifts are collected into the timeline as following:
    -+-+-+-+-+-+--+-+-++-+-+--+
                 ^     ^     ^
                       repeatings are removed and signs are coupled:
    [-+][-+][-+][-+][-+][-+][-+][-+][-+][-+][-+][-+]

'''

import numpy as np
import sys, pickle
from matplotlib.mlab import *
from core import CurrentCachable

class RefillDetector (CurrentCachable):
    
    def __str__(self):
        return 'RefillDetector'

    def __init__(self, ldr):
        ''' '''
        self._ldr = ldr
        self._cachelist = [ '_rflshifts' ]
        super(RefillDetector, self).__init__()

    def _init_wo_cache(self):
        self._nshifts = []
        self._pshifts = []
        self._lastpos = 0

    def _init_with_cache(self):
        f = open(os.path.join(self._dir, '_rflshifts'), 'rb')
        self._nshifts, self._pshifts, self._lastpos = pickle.load(f)
        f.close()
        # remove shifts that will be recalculated 
        rcls = self._ldr.getRecalcPartN()
        for i in rcls:
           b,e = self._ldr.getPartNo(i, flag=1)
           self._nshifts = filter(lambda x: (x < b) and (x > e), self._nshifts)
           self._pshifts = filter(lambda x: (x < b) and (x > e), self._pshifts)
        print 'Following shifts were loaded from cache:'
        print 'Negatives: ', ' '.join(map(str,self._nshifts))
        print 'Positives: ', ' '.join(map(str,self._pshifts))

    def checkCacheData(self):
        #TODO: think what to check here?
        pass


    def _getUnidirShifts(self, direction, frm, diap):
        import utils
        return utils.getRoughUniDirShifts(self._ldr, self._lastpos, \
                direction, frm, 500)
   
    def _preciseShifts(self, shifts, frm):
        import utils
        return utils.preciseShiftsPositioning(self._ldr, shifts, frm)
       

    def detect_shifts(self):
        frm = 20
        self._lastpos = self._ldr.getPartNo(-1,1)[1]
        # rough search of negative shift
        # these procedure takes a long time and restarts from cache
        shifts_a = self._getUnidirShifts(True, frm)
        shifts_b = self._getUnidirShifts(False, frm)
        # make shifts precise
        shifts_a = self._preciseShifts(shifts_a, frm)
        shifts_b = self._preciseShifts(shifts_b, frm)
        self._nshifts.extend(shifts_a)
        self._pshifts.extend(shifts_b)
        # saving shifts
        alls = (self._nshifts, self._pshifts, self._lastpos)
        f = open(os.path.join(self._dir, '_rflshifts'), 'w')
        pickle.dump(alls, f, 2)
        f.close()
        return shifts_a, shifts_b

    def determine(self):
        if self._nshifts == None:
            raise AssertionError('Shifts have not been determined yet!')
        ssa = np.ones((len(self._nshifts)+len(self._pshifts), 2), \
                dtype=np.int32)
        ssa[0:len(self._nshifts),0] = self._nshifts
        ssa[0:len(self._nshifts),1] = -1 # negative
        ssa[len(self._nshifts):,0] = self._pshifts
        ssa = ssa[ssa[:,0].argsort(),:]
        # aggregator of non-processable shifts
        irregular_shifts = []
        i = 0
        wait = -1 # first shift should be negative
        while i < ssa.shape[0]:
            if ssa[i,1] != wait:
                irregular_shifts.append( ssa[i,:] )
                ssa = ssa[list(set(range(ssa.shape[0])) - {i}), :]
            else:
                wait *= -1
                i += 1
            
        return ssa
        


