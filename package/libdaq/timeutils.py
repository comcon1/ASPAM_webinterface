'''Some usefull time hooks basing on a simple time module. '''

import time
import matplotlib.mlab as mlab

def upper_day(ut):
    uht = upper_hour(ut)
    gmt = time.gmtime(uht)
    if gmt.tm_hour == 0:
        return uht
    else:
        return uht + (24 - gmt.tm_hour)*3600

def upper_hour(ut):
    umt = upper_minute(ut)
    gmt = time.gmtime(umt)
    if gmt.tm_min == 0:
        return umt
    else:
        return umt + (60 - gmt.tm_min)*60

def upper_minute(ut):
    gmt = time.gmtime(ut)
    if gmt.tm_sec == 0:
        return ut
    else:
        return ut + (60 - gmt.tm_sec)

        
def form_periodic_intervals(starth, stoph, startut, stoput):
    '''From intervals from STARTH:00 to STOPH:00 over interval between two
    defined unix timestamps. Non-full intervals are not included.'''
    
    gmstart = time.gmtime(startut)
    if stoph > starth:
        _int = (stoph-starth)*3600
        # left border
        uhstart = upper_hour(startut)
        uhstart_hour = time.gmtime(uhstart).tm_hour
        if uhstart_hour <= starth:
            left_border = uhstart + (starth - uhstart_hour)*3600
        elif False:
            #TODO: criterion of inclusion of non-full interval
            pass
        else:
            left_border = upper_day(startut) + starth*3600
        # right border
        lba = mlab.frange(left_border, stoput, 86400)
        if ( lba[-1] > stoput ):
            lba = lba[:-1]
        if lba[-1] + _int > stoput:
            if False:
                #TODO: criterion of inclusion of non-full interval
                pass
            else:
                lba = lba[:-1]
        # final array generation
        retar = [ (i, i+_int) for i in list(lba) ]

    elif stoph < starth:
        # One should not be embarassed with code duplication because non-full
        # interval criteria are not included yet.
        _int = (24-stoph+starth)*3600
        # -- left border --
        uhstart = upper_hour(startut)
        uhstart_hour = time.gmtime(uhstart).tm_hour
        if uhstart_hour <= starth:
            if uhstart_hour < stoph:
                if False:
                    #TODO: criterion of inclusion of non-full interval
                    pass
                else:
                    left_border = uhstart + (starth - uhstart_hour)*3600
            else:
                left_border = uhstart + (starth - uhstart_hour)*3600
        elif False:
            #TODO: criterion of inclusion of non-full interval
            pass
        else:
            left_border = upper_day(startut) + starth*3600
        # right border
        lba = mlab.frange(left_border, stoput, 86400)
        if ( lba[-1] > stoput ):
            lba = lba[:-1]
        if lba[-1] + _int > stoput:
            if False:
                #TODO: criterion of inclusion of non-full interval
                pass
            else:
                lba = lba[:-1]
        # final array generation
        retar = [ (i, i+_int) for i in list(lba) ]
    else:
        raise AttributeError('Empty time interval.')

    return retar


    
