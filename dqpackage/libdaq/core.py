# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8

"""

:class: Cachable provides interface for storing and communicating data
calculated earlier. This is a base class that should be nested by all
data processors which need hard calculations.

:class: CurrentCachable implements global configuration on an abstract class.
Now it is only _workingDir.

:class: ArtefactDetector is an abstract for artefact removal tool (overflows,
hairpins, non-natural noise, non-relevant shifts)

"""
import os,os.path,re,md5
from . import _workingDir

class Cachable(object):
    
    def __str__(self):
        raise NotImplementedError('__str__ method should be defined for dirname determination.')

    def __init__(self):
        '''Cachable constructor should run after subclass constructor. '''
        self._dir = self._suggestDirName()
        assert(type(self._dir) == str)
        assert(type(self._cachelist) == list)
        self.initCacheDir()

    def _suggestDirName(self):
        raise NotImplementedError('dirname solver not implemented')

    def checkCacheData(self):
        '''Performs cache data safety self-test and raises exceptions.'''
        raise NotImplementedError('check was not implemented')

    def initCacheDir(self):
        '''Initialize cache directory. Create if not exists. Requires
        :meth:`_init_wo_cache' and :meth:`_init_from_cache(self)` be
        implemented.'''
        if not os.path.isdir(self._dir):
            try:
                os.mkdir(self._dir)
                self._init_wo_cache()
                print 'Cache directory created: %s.' % (self._dir)
            except OSError as e:
                print "Can't create directory %s." % (self._dir)
                raise e
        else:
            print 'Directory %s for %s cache exists.' % (self._dir, str(self))
            try:
                self._init_with_cache()
                self.checkCacheData()
            except BaseException as e:
                print 'Cache reading failed with error:\n%s\n' % (e.message)
                print type(e)
                self.cleanCacheDir()
                self._init_wo_cache()

    def _init_wo_cache(self):
        '''Initiating class with empty cache. From the very beginning.'''
        raise NotImplementedError('no-cache init not implemented.')
    
    def _init_with_cache(self):
        '''Initiating class with existing cache.'''
        raise NotImplementedError('cache init not implemented')

    def cleanCacheDir(self):
        '''Remove all caching files. Use if cache directory is
        corrupted. '''
        for f in os.listdir(self._dir):
            for r in self._cachelist:
                if re.match(r, f) != None:
                    try:
                        fdl = os.path.join(self._dir, f)
                        print 'Deleting ',fdl 
                        #os.unlink(fdl)
                    except OSError:
                        pass
        print 'All cache data was removed for %s.' % (str(self))

class CurrentCachable(Cachable):

    def _suggestDirName(self):
        ''' Build directory name basing on *FULL* path of the file if
        self._apath is defined. Else reference to Loader should exists and
        we create subdirectory according to the class name. '''
        try:
            nm = os.path.join(_workingDir, md5.new(self._apath).hexdigest())
        except AttributeError:
            nm = os.path.join(self._ldr._dir, str(self))
        return nm


class ArtefactDetector(CurrentCachable):
    
    def __init__(self, ldr):
        self._ldr = ldr
        import loader
        assert(type(ldr) == loader.Loader)
        self._cachelist = [ '_'+str(self).lower() ]
        super(ArtefactDetector, self).__init__()
    
    def _init_wo_cache(self):
        pass

    def _init_with_cache(self):
        pass

    def determine(self):
        pass

'''
Below there are Class definitions that process some properties evaluation.

:class: Actor is ancestor class for some actions with raw data.

:class: PropertyEvaluator is Cachable-inherited class that calculates properties
with the help of chain of :class: Actor-type objects.
'''

# NOT USED YET!
class Actor(object):
    '''
    This class is functor-like interface to some typical manipulation with data
    such as pieces conjugation, artefact removal, timeline modification and
    etc. Instances of :class: Actor are executed from :class: PropertyEvaluator
    object and should be cached there (not here).
    '''

    def __init__(self, **data):
        self._data = data
        self._result = None

    def checkData(self):
        pass

    def processData(self):
        raise NotImplementedError('processData() should be defined for Action')

    def getResult(self):
        return self._result


# NOT USED YET!
class PropertyEvaluator(Actor, Cachable):

    def __init__(self):
        self._actorChain = []

    def registerActor(self, a):
        assert( issubclass(type(a), Actor) )
        self._actorChain.append( a )

    def processData(self):
        pass

