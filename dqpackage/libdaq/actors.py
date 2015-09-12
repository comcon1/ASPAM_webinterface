# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8

from core import Actor
import numpy as np


# NOT USED YET!
class ActorApplyToEvery(Actor):

    def checkData(self):
        assert(type(self._data.dli) == list) # list of data
        assert(type(self._data.ali) == list) # list of actors
        assert(len(self._data.dli) == len(self._data.ali))
        for i in self._data.ali:
            assert( issubclass(i, Actor) )

    def processData(self):
        self._result = [None]*len(self._data.dli)
        for i in range(self._data.ali):
            a = self._data.ali[i]( data=self._data.dli[i] )
            a.processData()
            self._result[i] = a.getResult()

# NOT USED YET!
class ActorNPConcatenate(Actor):

    def checkData(self):
        assert(type(self._data.dli) == list) # list of data
        for i in range(self._data.dli):
            assert(type(self._data.dli[i]) == np.ndarray)

    def processData(self):
        self._result = np.concatenate(self._data.dli)

'''
Пока не понятно, как сворачивать код - пишем в лоб. Потом - рефакторинг.
'''

class EvaluateTotalDrinking(Cachable):
    '''
    Remove hairpin artefacts.
    Remove overflow from evaluation.
    Remove drinker refills.
    Building total drinking curve.
    Get drinking change for requesting data.
    '''
    pass

class EvaluateTotalDrinktimes(Cachable):
    '''
    Construct array with separate drink actions.
    '''
    pass
