# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8

"""
Load CSV file operations --- :mod: `libdaq.loader`
====================================================

  :class: Loader operates loading of a big csv-typed file.
  File should have fixed line size. Loader convert it into 
  integer-type array.

File partitioning scheme
------------------------

 ------------|<--buffer-size->|---------------
 **********************
         *************************
                              ****************
 ------->|---|<---intercept-->|---|<----------

Pices storage and regeneration
------------------------------

Files are stored in .npy format (numpy binaries). This format can be operated
easily. Files partN.npy are created into cache directory. When file is reopened
with larger size the last piece is regenerated and then :class:`Loader` forms
next pieces.

"""

import numpy as np
from matplotlib.mlab import movavg
import os,re
import os.path
import md5,sys
import pickle
from StringIO import StringIO
from core import CurrentCachable

from . import _workingDir

# load into memory (Kbytes)
__blocksize__ = 20000
__intercept__ = 3000

class LDRParams:
    def __init__(self, ncols=1):
        self.bfsz = -1
        self.bfin = -1
        dtlst = [('t', np.int32)]
        for i in range(ncols):
            dtlst.append(('v'+str(i), np.int16))
        self.dtp = np.dtype(dtlst)
        self.strs = -1
        self.zshift = -1
        self.lastfsz = -1
        self.portions = []
        pass

    def log(self):
        print '''
== Data-proxy directory initiated ==
Last processed file size: %10d
Buffer size: %d lines
Buffer intercept: %d lines
Characters in a string: %d
====================================
''' % (self.lastfsz, self.bfsz, self.bfin, self.strs)
    
    def addPortion(self, b,e,bt,et,f):
        self.portions.append({'f':f,'b':b,'e':e,'bt':bt,'et': et})
        print '[+] %11s: from line # %-10d (%10d lines) ' % \
            (os.path.basename(f), b, e - b)


class Loader(CurrentCachable):
    '''
    Loader can work with both multi-partionated and single-piece data file.
    The interface is absolutely the same.
    '''

    def __str__(self):
        return "Loader"

    def __init__(self, fname):
        '''
        Instance should be initialized with filename (:string: fname).
        '''
        self._cachelist = [\
                '_ldrparams', \
                'part[0-9]+.npy' ]
        self._apath = os.path.abspath(fname)
        s = os.stat(self._apath)
        super(Loader, self).__init__()
        
        self.partionate()

    def getDir(self):
        return self._dir

    def getNumParts(self):
        return len(self._p.portions)

    def getPartID(self, t=None):
        if t is not None:
            cc = 0
            i = None
            for prt in self._p.portions:
                if prt['bt'] <= t and prt['et'] >= t:
                    i = cc 
                    break
                cc += 1
            if i is None:
                raise AttributeError('Such time not found in all pieces.')
            return i
        else:
            raise NotImplementedError('getPartID with None')


    def getPartNo(self, i, flag=0):
        ''' *flag* : 0 - only array, 1 - borders.'''
        prt = self._p.portions[i]
        if flag == 0:
            X = np.load(prt['f'])
            return X
        elif flag == 1:
            return prt['bt'], prt['et']
        else:
            raise AttributeError('Flag should be 0 or 1.')


    def getPartT(self, t, flag=0):
        ''' Finds part where ``t'' is in a good evironment. 
        TODO: let t be a range. '''
        if issubclass(type(t), int):
            maxd = -1
            curpart = None
            for prt in self._p.portions:
                if prt['bt'] > t or prt['et'] < t:
                    continue
                if min(t-prt['bt'], prt['et']-t) > maxd:
                    curpart = prt
            X = np.load(curpart['f'])
            return X
        elif type(t) == tuple:
            raise NotImplementedError('Tuple request is not implemented yet')
        else:
            raise AttributeError('Wrong type of t: '+str(type(t)))


    def getRecalcPartN(self):
        '''Return indicies of parts which were generated de novo.'''
        return self._recalcParts

    def partionate(self):
        ''' 
Partionating file wrapper. File may change from previous run and 
during this run.
        '''
        fsz = os.stat(self._apath).st_size
        shift = ( (fsz-self._p.zshift) / self._p.strs) * self._p.strs - \
          self._p.lastfsz + self._p.zshift
        if shift == 0:
            print 'Cache is up to date.'
            self._recalcParts = []
        elif self._p.lastfsz == -1:
            print 'Partionating from the very beginning.'
            self._partionateAll()
        elif shift < 0:
            print 'File size is smaller.'
            self.cleanCacheDir()
            self._partionateAll()
        elif shift > 0:
            print 'File was appended. Partionating from the last piece.'
            self._continuePartionate()

    def checkCacheData(self):
        f = open(self._apath)
        cc = 0
        for prt in self._p.portions:
            X = np.load(prt['f'], mmap_mode='r')
            f.seek(self._p.zshift+prt['b']*self._p.strs)
            if int(f.readline().split()[0]) != X['t'][0]:
                raise IOError('Portion #%d failed self-test.' % cc)
            f.seek(self._p.zshift+(prt['e']-1)*self._p.strs, 0)
            if int(f.readline().split()[0]) != X['t'][-1]:
                raise IOError('Portion #%d failed self-test.' % cc)
            print '[v] %11s: from line # %-10d (%10d lines) ' % \
                    (os.path.basename(prt['f']), prt['b'], prt['e'] - prt['b'])
            cc += 1
        del X
        f.close()

    def _partionateAll(self):
        f = open(self._apath)
        # skipt commented header
        if self._p.zshift == -1:
            l = '#'
            zeroshift=0
            while l[0] == '#':
                zeroshift = f.tell()
                l = f.readline()
            f.seek(zeroshift)
            N = len(l.strip().split())
            print N-1
            self._p = LDRParams(N-1)
            self._p.strs = len(l)
            self._p.zshift = zeroshift
            self._p.bfsz = (__blocksize__ * 1024) / self._p.strs
            self._p.bfin = (__intercept__ * 1024) / self._p.strs
        print '''
File ``%s'' is opened.
Raw data begins from byte #%d. ''' % \
        ( self._apath, self._p.zshift )
            
        p0 = StringIO(f.read((self._p.bfsz+self._p.bfin)*self._p.strs))
        a0 = np.loadtxt(p0, dtype=self._p.dtp)
        np.save(os.path.join(self._dir, 'part0.npy'), a0)
        # is file longer than first buffer/
        if (a0.shape[0] == self._p.bfsz+self._p.bfin):
            # for a long file
            self._p.addPortion(0, self._p.bfsz+self._p.bfin, a0['t'][0], \
                    a0['t'][-1], os.path.join(self._dir, 'part0.npy'))
            del a0; del p0
            cc = 0
            while os.stat(self._apath).st_size - self._p.zshift - f.tell() >\
                    self._p.bfsz*self._p.strs:
                cc += 1
                f.seek(-self._p.bfin*self._p.strs, 1)
                curbline = (f.tell()-self._p.zshift) / self._p.strs
                p0 = StringIO(f.read((self._p.bfsz+2*self._p.bfin)*self._p.strs))
                a0 = np.loadtxt(p0, dtype=self._p.dtp)
                fnm = os.path.join(self._dir, 'part%d.npy' % (cc))
                self._p.addPortion(curbline, curbline + a0.shape[0], a0['t'][0], \
                    a0['t'][-1],fnm)
                np.save(fnm, a0)
                del a0; del p0
            cc += 1
            f.seek(-self._p.bfin*self._p.strs, 1)
            fnm = os.path.join(self._dir, 'part%d.npy' % (cc))
            curbline = (f.tell()-self._p.zshift) / self._p.strs
            # protect from reading non-full line. Reading integer count of lines.
            p0 = StringIO(f.read( ( ( os.stat(self._apath).st_size - self._p.zshift - f.tell() ) /
                self._p.strs ) * self._p.strs ))
            a0 = np.loadtxt(p0, dtype=self._p.dtp)
            # update information about last processed byte
            self._p.lastfsz = ( curbline + a0.shape[0])*self._p.strs 
            self._p.addPortion(curbline, curbline + a0.shape[0], a0['t'][0], \
                    a0['t'][-1],fnm)
            np.save(fnm, a0)
            del a0; del p0
        else:
            # for a short file. Adding the ONLY portion :)
            self._p.addPortion(0, a0.shape[0], a0['t'][0], \
                    a0['t'][-1], os.path.join(self._dir, 'part0.npy'))
            self._p.lastfsz = self._p.zshift + a0.shape[0]*self._p.strs
            del a0; del p0;

        f = open(os.path.join(self._dir, '_ldrparams'), 'w')
        pickle.dump(self._p, f, 2)
        f.close()
        
        self._recalcParts = range( 0, len(self._p.portions) )
    
    def _continuePartionate(self):
        print 'cprt0'
        f = open(self._apath)
        f.seek(self._p.zshift + (self._p.portions[-1]['b']+self._p.bfin) * self._p.strs )
        self._p.portions.pop()
        cc = len(self._p.portions) - 1
        ncp = cc + 1 # non-calculated parts
        while os.stat(self._apath).st_size - self._p.zshift - f.tell() > self._p.bfsz*self._p.strs:
            cc += 1
            f.seek(-self._p.bfin*self._p.strs, 1)
            curbline = (f.tell()-self._p.zshift) / self._p.strs
            p0 = StringIO(f.read((self._p.bfsz+2*self._p.bfin)*self._p.strs))
            print 'loading..',
            sys.stdout.flush()
            a0 = np.loadtxt(p0, dtype=self._p.dtp)
            print 'OK'
            print a0.shape
            fnm = os.path.join(self._dir, 'part%d.npy' % (cc))
            self._p.addPortion(curbline, curbline + a0.shape[0], a0['t'][0], \
                a0['t'][-1],fnm)
            np.save(fnm, a0)
            del a0; del p0
        cc += 1
        f.seek(-self._p.bfin*self._p.strs, 1)
        fnm = os.path.join(self._dir, 'part%d.npy' % (cc))
        curbline = (f.tell()-self._p.zshift) / self._p.strs
        # protect from reading non-full line. Reading integer count of lines.
        print 'loading strio..',
        sys.stdout.flush()
        p0 = StringIO(f.read( ( ( os.stat(self._apath).st_size - self._p.zshift - f.tell() ) /
            self._p.strs ) * self._p.strs ))
        print 'OK'
        a0 = np.loadtxt(p0, dtype=self._p.dtp)
        # update information about last processed byte
        self._p.lastfsz = ( curbline + a0.shape[0])*self._p.strs 
        self._p.addPortion(curbline, curbline + a0.shape[0], a0['t'][0], \
                a0['t'][-1],fnm)
        print 'saving..',
        sys.stdout.flush()
        np.save(fnm, a0)
        print 'OK'
        del a0; del p0
        
        f = open(os.path.join(self._dir, '_ldrparams'), 'w')
        pickle.dump(self._p, f, 2)
        f.close()

        self._recalcParts = range( ncp, len(self._p.portions) )
        print 'cprt1'

    def _init_wo_cache(self):
        self._p = LDRParams()
        self._recalcParts = []

    def _init_with_cache(self):
        try:
            f = open(os.path.join(self._dir, '_ldrparams'),'rb')
            self._p = pickle.load(f)
            self._p.log()
            f.close()
        except IOError as e:
            print 'Error opening parameter file.'
            raise e
        for prt in self._p.portions:
            fnm = os.path.basename(prt['f'])
            if not os.path.isfile(prt['f']):
                print 'One of files missing: %s.' % \
                    os.path.basename(prt['f'])
                raise IOError('File '+prt['f']+' missing!')


