# -*- coding: utf-8 -*-
"""
Configuration file for ASPAM_webinterface
@author: comcon1
"""

import os.path
import sys
if __name__ == "__main__":
    sys.exit(1)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#  USER DEFINED AREA. PLEASE REDEFINE AT LEAST
#   *DQSROOTDIR* VARIABLE.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ROOT folder of server configuration
# now it points to the test server folder
DQSROOTDIR = os.path.join(os.path.dirname(__file__), \
    '../../testsuite/testserver/')
# Folder containing experiment data
DQEXPDATADIR = os.path.join(DQSROOTDIR, 'expdata')
# Path to LOG file
DQGENLOG = os.path.join(DQEXPDATADIR, 'dqgen.log')

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#  PLEASE DO NOT MODIFY THE PARAMETERS BELOW
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

DQTEMPLDIR = os.path.join(os.path.dirname(__file__),'../templates')
DQSERVROOT = os.path.join(os.path.dirname(__file__), '..', 'daq')
DQSPRGNAME = 'Rat Wheel Analyzer'
DQSVERSION = '0.1'

sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))
from iniparse.config import BasicConfig

n = BasicConfig()

try:
    f = open(os.path.join(DQSROOTDIR,'parameters.conf'))
    n._readfp(f)
    f.close()
except IOError as e:
    print 'Can not read PARAMETERS file!'
    print e
    sys.exit(1)

params = n

import dqpackage

dqpackage.params = n

import dqpackage.libdaq as dq
import dqpackage.libDQimage as qi
