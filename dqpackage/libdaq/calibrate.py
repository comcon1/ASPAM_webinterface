# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8

'''
@TODO@
'''

from core import Cachable

class Calibration(Cachable):

    def __str__(self):
        return 'Calibration'

    def _init_with_cache(self):
        pass

    def _init_wo_cache(self):
        pass
