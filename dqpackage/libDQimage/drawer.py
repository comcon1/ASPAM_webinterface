# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8

"""
The base module for image preparation.
"""

import sys,os


if __name__ == '__main__':
    print 'This is a module.'
    sys.exit(1)

sys.path.append('../../package')

from libdaq import _workingDir
from libdaq.core import CurrentCachable 
from libdaq import RotCurveAnalyzer 
from libdaq.loader import Loader
import libdaq.timeutils as tmu
from matplotlib.mlab import frange
import numpy as np
import time

class ImageParameters(object):
    '''ImageParameters describe the query to image server. Only common geometry
    of the raw data is loaded into :class: ImageParameters instance. This class
    could be hashed and the same image request will be redirected to the cache.'''

    def __init__(self, loader):
        dat = loader.getPartNo(0)
        self._tstep = dat['t'][1]-dat['t'][0]
        self._nrats = len(dat.dtype)-1
        self._ratlist = tuple(range(self._nrats))
        self._bt, self._et = loader.getPartNo(0,flag=1)[0],\
            loader.getPartNo(loader.getNumParts()-1, flag=1)[1]
        self._steps = int( (self._et - self._bt) / self._tstep )

        self._start = None
        self._stop = None

        self._figsize = (7,7)
        del dat

    def setDiap(self, start=None, stop=None):
        '''Setting interval of plot. Start and Stop borders points the position
        from the beggining or the end of data array. Units - in timesteps.'''
        if start == None:
            self._start = 0
        else:
            if type(start) != int:
                raise AttributeError('start should be integer.')
            self._start = ( start + self._steps ) % self._steps
        if stop == None:
            self._stop = self._steps
        else:
            if type(stop) != int:
                raise AttributeError('start should be integer.')
            self._stop = ( stop + self._steps ) % self._steps

    def __hash__(self):
        return hash((self._tstep,self._nrats,self._bt, self._et, self._start, \
            self._stop, self._figsize, self._ratlist))

    def setFigSize(self, fs):
        self._figsize = fs

    def setRatList(self, rl):
        assert(len(rl) > 0 and len(rl) <= self.nrats)
        self._ratlist = tuple(rl)

    @property
    def figsize(self):
        return self._figsize

    @property
    def bt(self):
        return self._bt

    @property
    def et(self):
        return self._et

    @property
    def startt(self):
        return self._bt + self._start*self._tstep

    @property
    def stopt(self):
        return self._bt + self._stop*self._tstep

    @property
    def tstep(self):
        return self._tstep

    @property
    def nrats(self):
        return self._nrats

    @property 
    def ratlist(self):
        return self._ratlist

plt = None

class ImageRequest(CurrentCachable):

    def __init__(self, loader, req):
        self._ldr = loader
        self._drawData = None
        assert(type(self._ldr) == Loader)
        self._req = req
        assert(issubclass(type(self._req), ImageParameters))
        self._ifn = 'data.png'
        #TODO: may be other formats?
        self._cachelist = [ 'data.png' ]
        #--end TODO
        super(ImageRequest, self).__init__() 

    def __str__(self):
        return "ImageRequest-"+hex(hash(self._req))[3:]

    def checkCacheData(self):
        for f in self._cachelist:
            fn = os.path.join(self._dir,f)
            print 'Cache file ',fn, os.stat(fn).st_size

    def _genticks(self, ta, precis='h'):
        '''Generating ticks and labels according to GMT time from unix time
        data, ta. One can set major and minor ticks via precis. '''
        if precis[0] == 'h':
            mods = [12,6,4,3,2,1]
            t = [0]*51
            while len(t) > 50 and len(mods):
                mm = mods.pop()
                gm_1hour = tmu.upper_hour(ta[0], mod=mm)
                t = map(int,list(frange(gm_1hour, ta[-1], 3600*mm)))

            print ta[0], ta[-1]
            if precis[1] == '0':
                zers = []
                for tt in t:
                    if time.gmtime(tt).tm_hour == 0:
                        zers.append(t.index(tt))
                while len(zers):
                    t.pop(zers.pop())
            l = [ time.strftime('%H', time.gmtime(int(ii))) for ii in t ]
        elif precis[0] == 'd':
            gm_1day = tmu.upper_day(ta[0])
            t = map(int,list(frange(gm_1day, ta[-1],(3600*24))))
            if t[-1] > ta[-1]:
                t.pop()
            l = [ time.strftime('%d', time.gmtime(int(ii))) for ii in t ]
            print t,l
        else:
            raise NotImplementedError('Precis type ``%s'' not implemented' \
                    % precis)
        return t,l

    @property
    def drawData(self):
        ''' All drawable array --- in simple format '''
        if self._drawData == None:
            data = self._ldr.getPartT( self._req.startt  )
            #TODO: concatenate if draw through several parts
            starti = data['t'].searchsorted( self._req.startt )
            stopi = data['t'].searchsorted( self._req.stopt )
            data = data[starti:stopi]
            self._drawData = np.array(data.tolist(), dtype=np.int64)
            print 'Rats selected: ',  list(set(self._req.ratlist) | {0})
            self._drawData = self._drawData[:, list(set(self._req.ratlist) | {0})]
        return self._drawData


    def _init_wo_cache(self):
        import matplotlib.pyplot as plt
        data = self.drawData
        mticks, mtlbls = self._genticks(data[:,0], 'h0',)
        jticks, jtlbls = self._genticks(data[:,0], 'd')
        # drawing
        f = plt.figure(figsize=self._req.figsize)
        ax = plt.axes()
#        f.add_axes(ax)
        for i in range(data.shape[1]-1):
            plt.plot(data[:,0], data[:,i+1], '-', lw=2, ms=2)
        ax.set_xticks(mticks, minor=True)
        ax.set_xticklabels(mtlbls, minor=True, fontsize=8)
        ax.set_xticks(jticks, minor=False)
        ax.set_xticklabels(jtlbls, minor=False, fontsize=12)
        # saving
        ax.set_xlim(data[0,0], data[-1,0])
        self._saveData(f)

    def _saveData(self, fig):
        print 'Generating figure..'
        fn = self.getImage()
        fig.savefig(fn,format='png',dpi=92) 
        print 'Saving raw figure data..'
        np.savetxt(os.path.join(self._dir, 'raw.xvg'), self.drawData, fmt='%8d')

    def _init_with_cache(self):
        #TODO: making cache check
        pass

    def getImage(self, absolute=True):
        if absolute:
            return os.path.join(self._dir, self._ifn)
        else:
            return os.path.join(self._dir, self._ifn).replace(_workingDir, '')
            

# *****************************************
# CONCRETIZATION FOR WHEEL_TYPE EXPERIMENTS
# *****************************************

class RotImageParameters(ImageParameters):

    _typlst = ['raw', 'cumulative', 'partsum', 'daynight']
    _pt = 'raw' # default value

    
    def setPlotType(self, typ):
        assert(type(typ) == str)
        assert(typ in self._typlst)
        self._pt = typ

    def __hash__(self):
        return super(RotImageParameters, self).__hash__() ^ \
                hash(self.plotType)

    @property 
    def plotType(self):
        return self._pt

class RotImageRequest(ImageRequest):
    
    def __init__(self, rca, req):
        assert(type(rca), RotCurveAnalyzer)
        self._rca = rca
        super(RotImageRequest, self).__init__(rca.loader, req)

    @property
    def drawData(self):
        ''' All drawable array --- in simple format '''
        if self._drawData != None:
            return self._drawData
        if self._req.plotType == 'raw':
            return super(RotImageRequest, self).drawData
        elif self._req.plotType == 'cumulative':
            data = self._rca.cumdata
            starti = data[:,0].searchsorted( self._req.startt )
            stopi = data[:,0].searchsorted( self._req.stopt )
            data = data[starti:stopi,list(set(self._req.ratlist)|{0})]
            self._drawData = np.copy(data)
        elif self._req.plotType == 'partsum':
            raise NotImplementedError('Unimplemented plotType'\
                    +self._req.plotType)
        elif self._req.plotType == 'daynight':
            raise NotImplementedError('Unimplemented plotType'\
                    +self._req.plotType)
        else:
            raise AttributeError('Unknown plotType '+self._req.plotType)
        # finally..
        return self._drawData
