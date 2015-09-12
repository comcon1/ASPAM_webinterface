# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8

'''
Determine overflow of the detector.
'''

import numpy as np
import sys, pickle
from matplotlib.mlab import *
from core import ArtefactDetector

class OverflowDetector (ArtefactDetector):

    def __str__(self):
        return "OverflowDetector"

    
