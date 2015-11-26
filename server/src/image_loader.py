#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, argparse
from config import *
from servutils import *

'''
Standalone script that loads images by parameters.
In future this script should be replaced with more fast procedures.
'''

prs = argparse.ArgumentParser(description="")

# the major type! what image to create!
prs.add_argument('-x', dest='typ', metavar='T', type=str, help='type of the image') 

prs.add_argument('-d', dest="exdir", metavar='FILENAME', type=str, help='experiment directory', default='.')
prs.add_argument('-i', dest='datfil', metavar='FILENAME', type=str, help='experiment file',default='data00.xvg')

prs.add_argument('-f', dest="fromdate", metavar='N', type=int, help='from date', default=-1)
prs.add_argument('-t', dest="tilldate", metavar='N', type=int, help='till file', default=-1)
prs.add_argument('-r', dest="selected_rats", type=str, help='selected rats as list "1,2,3,.."', default='')
prs.add_argument('-s', dest="scale", type=str, help='scale of the plot', default='')
prs.add_argument('-y', dest="yunits", type=str, help='Units of the OY axis', default='meters')

prs.add_argument('-u', dest="regen_cache", action="store_true", help='force regenerate')
prs.add_argument('-p', dest="fastpreview", action="store_true", help='mode of fastest look')
#prs.add_argument('-l', dest="log", metavar='FILE', type=str, help='log file',default='logger.log')

args = prs.parse_args()

futurefile = os.path.join(args.exdir, args.datfil)
print futurefile

if args.typ in ['expreview_raw', 'expreview_cumulative']:
    try:
        rca = dq.RotCurveAnalyzer(futurefile)
        ip0 = qi.RotImageParameters(rca.loader)    
    except Exception as e:
        sys.exit(1)

    if args.fastpreview:
        # force reset dates
        args.fromdate = ip0.et - 3600
        args.tilldate = ip0.et
            
    print 'Data was recorded in diapazone: %d-%d' % (ip0.bt, ip0.et)
    _fromdate = dq.tu.lower_day(ip0.bt) if args.fromdate == -1 else int(args.fromdate)
    _tilldate = dq.tu.lower_day(ip0.et) if args.tilldate == -1 else int(args.tilldate)
    
    ip0.setDiapT(_fromdate, _tilldate+24*3600)
    print 'Requesting image for data in range %d-%d' % (_fromdate, _tilldate+24*3600)
    print 'Frame range: %d-%d:%d' % (ip0.startt, ip0.stopt, ip0._tstep)
    
    ip0.setFigSize(tuple(map(float,args.scale.split(':'))))
    __ratlist = map(int,args.selected_rats.split(','))
    ip0.setRatList(__ratlist)
    ip0.Yunits = args.yunits
    if args.regen_cache:
        ip0.setRegen()
    try:
        ip0.plotType = 'raw' if args.typ == 'expreview_raw' else 'cumulative'
        ir0 = qi.RotImageRequest(rca, ip0)
    except Exception as e:
        print '******** ERROR DURING REQUEST OF PICTURE PREPARATION!! *********'
        print str(e)
        sys.exit(1)

# print resulting information
print 'RESULT_BT:' + str(ip0.bt)
print 'RESULT_ET:' + str(ip0.et)
print 'IMAGE_PATH:' + ir0.getImage(absolute=False)
sys.exit(0)