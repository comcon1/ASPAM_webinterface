# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8

"""
The base module for image preparation.
"""

import sys,os


if __name__ == '__main__':
    print 'This is a module.'
    sys.exit(1)

from .. import params

from ..libdaq import _workingDir
from ..libdaq.core import CurrentCachable 
from ..libdaq import RotCurveAnalyzer 
from ..libdaq.loader import Loader
from ..libdaq import timeutils as tmu

from matplotlib.mlab import frange
import matplotlib as mpl

mpl.rcParams['backend'] = 'agg'
mpl.interactive(False)
import matplotlib.pyplot as plt
import matplotlib.style as mpl_style
mpl_style.use(os.path.join(os.path.dirname(__file__),'./current.mplstyle'))

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
        self._cacheregen = False

        self._figsize = (7,7)
        del dat

    def setDiap(self, start=None, stop=None):
        '''Setting interval of plot. Start and Stop borders points the position
        from the beggining or the end of data array. Units - in timesteps.'''
        if start is None:
            self._start = 0
        else:
            if int(start) != start:
                raise AttributeError('start should be integer; not '+str(type(start)))
            self._start = ( start + self._steps ) % self._steps
        if stop is None:
            self._stop = self._steps
        else:
            if int(stop) != stop:
                raise AttributeError('start should be integer.'+str(type(stop)))
            self._stop = ( stop + self._steps ) % self._steps
    
    def setDiapT(self, start=None, stop=None):
        bp = None if start is None else (max(start,self.bt) - self.bt) / self.tstep
        ep = None if stop is None else (min(stop,self.et-1) - self.bt) / self.tstep
        if start < self.bt:
             bp = None
        if stop > self.et:
             ep = None
        self.setDiap(bp, ep)

    def __hash__(self):
        return hash((self._tstep,self._nrats,self._bt, self._et, self._start, \
            self._stop, self._figsize, self._ratlist))

    def setFigSize(self, fs):
        self._figsize = fs

    def setRatList(self, rl):
        assert(len(rl) > 0 and len(rl) <= self.nrats)
        self._ratlist = tuple(rl)
    
    def setRegen(self):
        self._cacheregen = True
        
    @property
    def cacheregen(self):
        return self._cacheregen

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
        


class ImageRequest(CurrentCachable):

    def __init__(self, loader, req):
        self._ldr = loader
        self._drawData = None
        assert(type(self._ldr) == Loader)
        self._req = req
        assert(issubclass(type(self._req), ImageParameters))
        if (self._req.startt >= self._req.stopt):
            raise AttributeError('Invalid time boundaries for ImageRequest: %d, %d!' \
                   % (self._req.startt,self._req.stopt) )
        if not hasattr(self, '_ifn'):
            self._ifn = 'data.png'
        #TODO: may be other formats?
        if not hasattr(self, '_cachelist'):
            self._cachelist = [ 'data.png' ]
        #--end TODO
        super(ImageRequest, self).__init__() 

    def __str__(self):
        return "ImageRequest-"+hex(hash(self._req))[3:]

    def checkCacheData(self):
        if self._req.cacheregen:
            raise BaseException('RegenCache Flag was turned on!')
        for f in self._cachelist:
            fn = os.path.join(self._dir,f)
            print 'Cache file ',fn, os.stat(fn).st_size

    def _genticks(self, ta, precis='h'):
        '''Generating ticks and labels according to GMT time from unix time
        data, ta. One can set major and minor ticks via precis. '''
        if precis[0] == 'h':
            mods = [12,6,4,3,2,1]
            t = [0]*51
            # 4 ticks per inch is OK!
            while len(t) > 4*self._req.figsize[0] and len(mods):
                mm = mods.pop()
                gm_1hour = tmu.upper_hour(ta[0], mod=mm)
                t = map(int,list(frange(gm_1hour, ta[-1], 3600*mm)))
            if precis[1] == '0':
                zers = []
                for tt in t:
                    if time.localtime(tt).tm_hour == 0:
                        zers.append(t.index(tt))
                while len(zers):
                    t.pop(zers.pop())
            if len(t) > 4*self._req.figsize[0]:
                l = ['']*len(t)
            else:
                l = [ time.strftime('%H', time.localtime(int(ii))) for ii in t ]
        elif precis[0] == 'd':
            if precis[1] == 'c': # at the center of a day
                gm_1day = tmu.upper_day(ta[0]) 
                gm_1day = gm_1day - 12*3600 if gm_1day - 12*3600 > ta[0] else gm_1day + 12*3600
                fmt = '%d.%m'
            elif precis[1] == 'l':
                gm_1day = tmu.upper_day(ta[0])
                fmt = '%d'
            else:
                AttributeError('Precise code %s is incorrect' % precis)
            print 'Building day ticks from ts.%d to ts.%d' % (ta[0], ta[-1])
            print 'First tick: %d' % gm_1day
            skip_days = 1
            while (ta[-1]-gm_1day)/3600./24./skip_days > self._req.figsize[0]:
                skip_days += 1
                #TODO: and something more curious!
            print 'DAYS skipping: %d days at %d inches' %  (skip_days, self._req.figsize[0])
            t = map(int,list(frange(gm_1day, ta[-1],(3600*24*skip_days))))
            if len(t) > 0:
                if t[-1] > ta[-1]:
                    t.pop()
                l = [ time.strftime(fmt, time.localtime(int(ii))) for ii in t ]
                print t,l
            else:
                # at least one tick :-)
                t = [ (ta[0]+ta[1]) / 2. ]
                l = [ time.strftime(fmt, time.localtime(ta[0]) ) ]
        else:
            raise NotImplementedError('Precis type ``%s'' not implemented' \
                    % precis)
        return t,l

    @property
    def drawData(self):
        ''' All drawable array --- in simple format '''
        reqrl = list({0}|set(self._req.ratlist))
        reqrl.sort()
        if self._drawData is None:
            data = self._ldr.getPartT( self._req.startt  )
            
            print 'Data loaded: %d lines' % data.shape[0]
            #TODO: concatenate if draw through several parts
            starti = data['t'].searchsorted( self._req.startt )
            stopi = data['t'].searchsorted( self._req.stopt )
            print 'Timerange: %d - %d' % (self._req.startt, self._req.stopt)
            data = data[starti:stopi]
            print 'Data selected: %d lines' % data.shape[0]
            self._drawData = np.array(data.tolist(), dtype=np.float64)
            print 'Rats selected: ',  reqrl
            self._drawData = self._drawData[:, reqrl]
            self._drawData[:,1:] *= float(params.root.turnstometers) if self._req.Yunits == 'meters' else 1
        return self._drawData


    def _init_wo_cache(self):
        data = self.drawData
        if data.shape[0] < 10:
            raise AttributeError('Too small amount of data for analyse! Wait for more data!')
        print 'Image will be drawn for data of %dx%d' % data.shape
        mticks, mtlbls = self._genticks(data[:,0], 'h1',)
        jticks, jtlbls = self._genticks(data[:,0], 'dc')
        # drawing
        f = plt.figure(figsize=self._req.figsize)
        self._before_drawing(f)
        ax = plt.axes()
#        f.add_axes(ax)
        pls = [] # plot lines
        for i in range(data.shape[1]-1):
            try: 
                color_i = params.curves['r%d'%i].color
                pp = plt.plot(data[:,0], data[:,i+1], '-', lw=2, ms=2, color=color_i)
            except:
                pp = plt.plot(data[:,0], data[:,i+1], '-', lw=2, ms=2)
            pls.append(pp[0])
        ax.set_xticks(mticks, minor=True)
        ax.set_xticklabels(mtlbls, minor=True, fontsize=8)
        ax.set_xticks(jticks, minor=False)
        ax.set_xticklabels(jtlbls, minor=False, fontsize=12)
        ax.tick_params(pad=20, axis='x', which='major')
        ax.set_ylabel('Length, meters' if self._req.Yunits == 'meters' else 'Turns')
        ax.set_xlabel('Date (d.m) and time (h)')
        # saving
        ax.set_xlim(data[0,0], data[-1,0])
        self._after_drawing(f,pls)
        self._saveData(f)
    
    def _before_drawing(self, fig):
        pass
    
    def _after_drawing(self, fig, pls):
        pass

    def _saveData(self, fig):
        print 'Generating figure..'
        fn = self.getImage()
        fig.savefig(fn,format='png',dpi=92) 
        # is it really need?
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
    
    ''' daynightFlag - 000 perbit flag. 1st - day, 2nd - daylight, 3rd - night '''
    
    _typlst = ['raw', 'cumulative', 'partsum', 'daynight', 'timecumulate']
    _pt = 'raw' # default value
    _Yunits = 'meters'
    _dnflag = 7
    _tintervals = (0,9*60,21*60)
    
    def __hash__(self):
        return super(RotImageParameters, self).__hash__() ^ \
                hash((self.plotType,self.Yunits,self.daynightFlag,\
                self.tintervals))

    @property 
    def plotType(self):
        return self._pt
    
    @plotType.setter
    def plotType(self, typ):
        assert(type(typ) == str)
        assert(typ in self._typlst)
        self._pt = typ    

    @property
    def Yunits(self):
        return self._Yunits
    
    @Yunits.setter
    def Yunits(self, units):
        if units in ['meters', 'turns']:
            self._Yunits = units
        else:
            raise AttributeError('Bad units value!')
        
    @property
    def daynightFlag(self):
        return self._dnflag
    
    @daynightFlag.setter
    def daynightFlag(self, f):
        assert(f in [1,2,3,4,5,6,7])
        self._dnflag = f
    
    @property
    def tintervals(self):
        return self._tintervals
    
    @tintervals.setter
    def tintervals(self, dln):
        assert(len(dln) == 3)
        assert(dln[0] < 24*60 and dln[0] > 0)
        assert(dln[1] < 24*60 and dln[1] > 0)
        assert(dln[2] < 24*60 and dln[2] > 0)
        self._tintervals = tuple(dln)

class RotImageRequest(ImageRequest):
    
    def __init__(self, rca, req):
        assert(type(rca) == RotCurveAnalyzer)
        self._rca = rca
        try:
            self.day_color = params.daynight.day.bar.facecolor
        except:
            self.day_color = '#ff0000'        
        try:
            self.light_color = params.daynight.light.bar.facecolor
        except:
            self.light_color = '#00ff00'
        try:
            self.night_color = params.daynight.night.bar.facecolor
        except:
            self.night_color = '#0000ff'
        super(RotImageRequest, self).__init__(rca.loader, req)

    @property
    def drawData(self):
        ''' All drawable array --- in simple format '''
        reqrl = list({0}|set(self._req.ratlist))
        reqrl.sort()
        if self._drawData is not None:
            return self._drawData
        if self._req.plotType == 'raw':
            data = np.array(self._rca.rawdata, dtype=np.float64)
            starti = data[:,0].searchsorted( self._req.startt )
            stopi = data[:,0].searchsorted( self._req.stopt )
            data = data[starti:stopi,reqrl]
            data[:,1:] *= float(params.root.turnstometers) if self._req.Yunits == 'meters' else 1.0
            self._drawData = np.copy(data)
        elif self._req.plotType == 'cumulative':
            data = np.array(self._rca.cumdata, dtype=np.float64)
            starti = data[:,0].searchsorted( self._req.startt )
            stopi = data[:,0].searchsorted( self._req.stopt )
            data = data[starti:stopi,reqrl]
            data[:,1:] *= float(params.root.turnstometers) if self._req.Yunits == 'meters' else 1.0
            self._drawData = np.copy(data)
        elif self._req.plotType == 'partsum':
            raise NotImplementedError('Unimplemented plotType'\
                    +self._req.plotType)
        elif self._req.plotType == 'daynight':
            day,light,night = self._rca.getDayNightData(self._req.tintervals[0], \
                self._req.tintervals[1], self._req.tintervals[2], self._req.startt, \
                self._req.stopt)
            day = day[:,reqrl]
            light = light[:,reqrl]
            night = night[:,reqrl]
            # time, DAY mean, std, LIGHT mean, std, NIGHT mean std
            #TODO: make correct 1-tailed quantile
            dd = np.zeros((day.shape[0],7))
            dd[:,0] = day[:,0]
            dd[:,1] = np.mean(day[:,1:], axis=1)
            dd[:,2] = np.std(day[:,1:], axis=1) 
            dd[:,3] = np.mean(light[:,1:], axis=1)
            dd[:,4] = np.std(light[:,1:], axis=1) 
            dd[:,5] = np.mean(night[:,1:], axis=1)
            dd[:,6] = np.std(night[:,1:], axis=1)
            dd[:,1:] *= float(params.root.turnstometers) if self._req.Yunits == 'meters' else 1
            self._drawData = dd
        elif self._req.plotType == 'timecumulate':
            day,light,night = self._rca.getDayNightData(self._req.tintervals[0], \
                self._req.tintervals[1], self._req.tintervals[2], self._req.startt, \
                self._req.stopt)
            day = day[:,reqrl]
            light = light[:,reqrl]
            night = night[:,reqrl]
            # time, DAY mean, std, LIGHT mean, std, NIGHT mean std
            #TODO: make correct 1-tailed quantile
            dd = np.zeros((len(self._req.ratlist),4))
            dd[:,0] = list(set(self._req.ratlist))
            dd[:,1] = np.sum(day[:,1:], axis=0)
            dd[:,2] = np.sum(light[:,1:], axis=0)
            dd[:,3] = np.sum(night[:,1:], axis=0)

            dd[:,1:] *= float(params.root.turnstometers) if self._req.Yunits == 'meters' else 1
            self._drawData = dd        
        else:
            raise AttributeError('Unknown plotType '+self._req.plotType)
        # finally..
        return self._drawData
        
    def _init_wo_cache(self):
        if self._req.plotType in ['cumulative','raw']:
            super(RotImageRequest, self)._init_wo_cache()
            return
        elif self._req.plotType == 'daynight':
            self._drawDN()
            return
        elif self._req.plotType == 'timecumulate':
            self._drawTC()
            return
    
    def _drawDN(self):
        data = self.drawData
        # drawing
        f = plt.figure(figsize=self._req.figsize)
        self._before_drawing(f)
        ax = plt.axes()
        pls = [] # bar patches
        bitcount = 1 if self._req.daynightFlag in [1,2,4] else \
                    2 if self._req.daynightFlag in [3,5,6] else \
                     3
        ndays = data.shape[0]        
        xs = np.linspace(0, (bitcount+1)*(ndays-1), ndays)
        print xs
        print data
        zshift = 0.2 # between box and left/right side of the panel
        shift = zshift
        boxWidth = 1.0
            
        if self._req.daynightFlag & 1: # DAY
            pp = plt.bar(xs + shift, data[:,1], yerr=data[:,2], \
                width=boxWidth, color=self.day_color)
            pls.append(pp[0])
            shift += 1
        if self._req.daynightFlag & 2: # LIGHT
            pp = plt.bar(xs + shift, data[:,3], yerr=data[:,4], \
                width=boxWidth, color=self.light_color)
            pls.append(pp[0])
            shift += 1
        if self._req.daynightFlag & 4: # NIGHT
            pp = plt.bar(xs + shift, data[:,5], yerr=data[:,6], \
                width=boxWidth, color=self.night_color)
            pls.append(pp[0])
        
        ax.set_xlim(0,xs[-1]+shift+boxWidth+zshift)
        ax.set_xticks(xs + (shift+zshift)/2. + boxWidth/2.)
        fmt = '%d.%m'
        jtbl = [ time.strftime(fmt, time.localtime(int(ii))) for ii in data[:,0] ]
        ax.set_xticklabels(jtbl)
        # saving
        self._after_drawing(f,pls)
        self._saveData(f)
    
    def _drawTC(self):
        data = self.drawData
        # drawing
        f = plt.figure(figsize=self._req.figsize)
        self._before_drawing(f)
        ax = plt.axes()
        pls = [] # bar patches
        bitcount = 1 if self._req.daynightFlag in [1,2,4] else \
                    2 if self._req.daynightFlag in [3,5,6] else \
                     3
        nrats = data.shape[0]
        xs = np.linspace(0, (bitcount+1)*(nrats-1), nrats)
        print xs
        print data
        zshift = 0.2 # between box and left/right side of the panel
        shift = zshift
        boxWidth = 1.0
        
        if self._req.daynightFlag & 1: # DAY
            pp = plt.bar(xs + shift, data[:,1], \
                width=boxWidth, color=self.day_color)
            pls.append(pp[0])
            shift += 1
        if self._req.daynightFlag & 2: # LIGHT
            pp = plt.bar(xs + shift, data[:,2], \
                width=boxWidth, color=self.light_color)
            pls.append(pp[0])
            shift += 1
        if self._req.daynightFlag & 4: # NIGHT
            pp = plt.bar(xs + shift, data[:,3], \
                width=boxWidth, color=self.night_color)
            pls.append(pp[0])
        
        ax.set_xlim(0,xs[-1]+shift+boxWidth+zshift)
        ax.set_xticks(xs + (shift+zshift)/2. + boxWidth/2.)
        fmt = '%d'
        jtbl = [ fmt % (ii) for ii in data[:,0] ]
        ax.set_xticklabels(jtbl)
        # saving
        self._after_drawing(f,pls)
        self._saveData(f)

'''
    Overriding RotImageRequest behaviour for simply generating CSV instead of an image. 
#TODO: absolutely need to be transferred to another file!
'''
class RotTableRequest(RotImageRequest):
    
    def __init__(self, *args, **kwargs):
        # override file format
        self._ifn = 'data.csv'
        self._cachelist = [ 'data.csv' ]
        # run inherited constructor
        super(RotTableRequest, self).__init__(*args, **kwargs)
    
    def _init_wo_cache(self):
        data = self.drawData
        fmt = params.download.csvdtfmt

        fname = self.getImage()
        print fname
        f = open(fname, 'w')
        if self._req.Yunits == 'turns':
            fmnums = ',%d'*(data.shape[1]-1)
        elif self._req.Yunits == 'meters':
            fmnums = ',%.3f'*(data.shape[1]-1)
        for i in range(data.shape[0]):
            f.write(time.strftime(fmt, time.localtime(data[i,0])) + \
                (fmnums % tuple(data[i,1:])) + '\n')
        f.close()



class RotImageDownload(RotImageRequest):
    
    def __str__(self):
        return 'downloads'
    
    def __init__(self, rca, req, tpd):
        ''' *string* tpd: type of download. May be 'csv', 'png', 'pdf' '''
        assert (tpd in ['csv', 'png', 'pdf'])
        self._tpd = tpd
        super(RotImageDownload, self).__init__(rca, req)
        
    def checkCacheData(self):
        self._ifn = hex(hash(self._req))[3:] + '.'+self._tpd
        self._cachelist = []
        raise BaseException('Generating downloading data. Caching is turned off.')
        
    def _before_drawing(self, fig):
        # including legend to the right
        fig.set_figheight( max (fig.get_figheight(), 0.25*len(self._req.ratlist)+0.8) )
        fig.set_figwidth(fig.get_figwidth() + float(params.download.legendwidth) )
        fig.subplots_adjust( right = (fig.get_figwidth() - float(params.download.legendwidth))/fig.get_figwidth() )
    
    def _init_wo_cache(self):
        if self._tpd == 'csv':
            return
        else:
            super(RotImageDownload, self)._init_wo_cache()
        
    def _after_drawing(self, fig, lines):
        #TODO: nice axes margin
        if self._req.plotType == 'raw':
            plt.title('Raw data from detectors2', figure=fig)
        elif self._req.plotType == 'cumulative':
            plt.title('Cumulative data', figure=fig, linespacing=2.5)
        plt.figlegend( lines, map(lambda x: 'Rat #%d' % x, self._req.ratlist) , 'center right')

    def _saveData(self, fig):
        print 'Generating figure..'
        if self._tpd == 'csv':
            pass
        elif self._tpd == 'png':
            fn = self.getImage(absolute=True)
            fig.savefig(fn,format='png') 
        elif self._tpd == 'pdf':
            pass
    
    
    
    
