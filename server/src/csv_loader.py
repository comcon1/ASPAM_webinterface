#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 17:51:47 2015

Standalone script that loads CSV by parameters.
In future this script should be replaced with more fast procedures

@author: comcon1
"""

import os, sys, argparse
from config import *
from servutils import *
import profile,traceback

prs = argparse.ArgumentParser(description="")

# the major type! what CSV to create!
prs.add_argument('-d', dest="exdir", metavar='FILENAME', type=str, help='experiment directory', default='.')
prs.add_argument('-i', dest='datfil', metavar='FILENAME', type=str, help='experiment file',default='data00.xvg')
prs.add_argument('-f', dest="fromdate", metavar='N', type=int, help='from date', default=-1)
prs.add_argument('-t', dest="tilldate", metavar='N', type=int, help='till file', default=-1)
prs.add_argument('-r', dest="selected_rats", type=str, help='selected rats as list "1,2,3,.."', default='')
prs.add_argument('-y', dest="yunits", type=str, help='Units of the OY axis', default='meters')
prs.add_argument('-u', dest="regen_cache", action="store_true", help='force regenerate')

args = prs.parse_args()

futurefile = os.path.join(args.exdir, args.datfil)
print futurefile

def MUMU():
    try:
        rca = dq.RotCurveAnalyzer(futurefile)
        ip0 = qi.RotImageParameters(rca.loader)    
    except Exception as e:
        print '******** ERROR DURING LOADING AND ANALYSING!! *********'
        traceback.print_exc()
        sys.exit(1)
            
    print 'Data was recorded in diapazone: %d-%d' % (ip0.bt, ip0.et)
    _fromdate = dq.tu.lower_day(ip0.bt) if args.fromdate == -1 else int(args.fromdate)
    _tilldate = dq.tu.lower_day(ip0.et) if args.tilldate == -1 else int(args.tilldate)
    
    ip0.setDiapT(_fromdate, _tilldate+24*3600)
    print 'Requesting image for data in range %d-%d' % (_fromdate, _tilldate+24*3600)
    print 'Frame range: %d-%d:%d' % (ip0.startt, ip0.stopt, ip0._tstep)
    
    __ratlist = map(int,args.selected_rats.split(','))
    ip0.setRatList(__ratlist)
    ip0.Yunits = args.yunits
    if args.regen_cache:
        ip0.setRegen()
        
    try:
#TODO: may be other formats?
        ip0.plotType = 'raw'
        ir0 = qi.RotTableRequest(rca, ip0)
    except Exception as e:
        print '******** ERROR DURING CSV PREPARATION!! *********'
        traceback.print_exc()
        sys.exit(1)
    # print resulting information
    print 'CSV_PATH:' + ir0.getImage(absolute=True)
    
MUMU()

sys.exit(0)