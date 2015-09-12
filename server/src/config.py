# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 21:42:09 2015

@author: comcon1
"""

import os.path
import sys

sys.path.append('../../')

DQSPRGNAME = 'Rat Wheel Analyzer'
DQSVERSION = '0.1'
DQSROOTDIR = os.path.join(os.path.dirname(__file__), \
    '../../testsuite/testserver/')

from iniparse.config import BasicConfig

n = BasicConfig()
f = open(os.path.join(DQSROOTDIR,'parameters.conf'))
n._readfp(f)
f.close()
params = n

import dqpackage

dqpackage.params = n

import dqpackage.libdaq as dq
import dqpackage.libDQimage as qi
