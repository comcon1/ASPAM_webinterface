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
from libdaq.loader import Loader
import libdaq.timeutils as tmu
import matplotlib.pyplot as plt
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
            self._stop, self._figsize))

    def setFigSize(self, fs):
        self._figsize = fs

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



class ImageRequest(CurrentCachable):

    def __init__(self, loader, req):
        self._ldr = loader
        assert(type(self._ldr) == Loader)
        self._req = req
        assert(type(self._req) == ImageParameters)
        self._ifn = 'data.png'
        #TODO: may be other formats?
        self._cachelist = [ 'data.png' ]
        #--end TODO
        super(ImageRequest, self).__init__() 

    def __str__(self):
        return "ImageRequest-"+str(hash(self._req))

    def checkCacheData(self):
        for f in self._cachelist:
            fn = os.path.join(self._dir,f)
            print 'Cache file ',fn, os.stat(fn).st_size

    def _genticks(self, ta, precis='h'):
        '''Generating ticks and labels according to GMT time from unix time
        data, ta. One can set major and minor ticks via precis. '''
        if precis[0] == 'h':
            gm_1hour = tmu.upper_hour(ta[0])
            print gm_1hour
            t = map(int,list(frange(gm_1hour, ta[-1], 3600)))
            if precis[1] == '0':
                zers = []
                for tt in t:
                    print tt
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

    def _init_wo_cache(self):
        data = self._ldr.getPartT( self._req.startt  )
        #TODO: concatenate if draw through several parts
        starti = data['t'].searchsorted( self._req.startt )
        stopi = data['t'].searchsorted( self._req.stopt )
        data = data[starti:stopi]
        mticks, mtlbls = self._genticks(data['t'], 'h0',)
        jticks, jtlbls = self._genticks(data['t'], 'd')
        # drawing
        f = plt.figure(figsize=self._req.figsize)
        ax = plt.axes()
#        f.add_axes(ax)
        for i in range(self._req.nrats):
            plt.plot(data['t'], data['v'+str(i)],\
                    'o', lw=2, ms=2)
        ax.set_xticks(mticks, minor=True)
        ax.set_xticklabels(mtlbls, minor=True, fontsize=8)
        ax.set_xticks(jticks, minor=False)
        ax.set_xticklabels(jtlbls, minor=False, fontsize=12)
        # saving
        ax.set_xlim(data['t'][0], data['t'][-1])
        print 'Generating figure'
        fn = self.getImage()
        f.savefig(fn,format='png',dpi=92) 

    def _init_with_cache(self):
        pass

    def getImage(self):
        return os.path.join(self._dir, self._ifn)
