# ***************************************************************
# libDAQ library for numerical analysis of raw rat-drinking data
# ***************************************************************

'''
libDAQ - [u.c.]
'''

__all__ = ['libdaq']
_workingDir = '/home/comcon1/.libdaq/'

import core
import os.path, md5



# exports

from libdaq import RawCurveAnalyzer
from loader import Loader
from core import CurrentCachable
import timeutils as tu
