
import numpy as np
import sys

def getRoughUniDirShifts(ldr, startpos, direction, frm, diap:
        shifts = []
        rcls = ldr.getRecalcPartN()
        found = max(0,startpos - frm*2) # last processed time
        print 'Finding shifts from the point: ', found
        j = rcls[0] if len(rcls) else ldr.getPartID(t=found)
        print 'Starting from part No.', j
        
        while True:
            if j == ldr.getNumParts():
                break
            a = ldr.getPartNo(j)
            z = np.zeros(200, dtype=np.bool)
            ii = a['t'].searchsorted(found) + frm*2 if found else 1
            while a.shape[0] - ii > frm:
                foundr = 0
                # rough search
                print ('\nScanning file no. %d, line %10d' % (j,0) ),
                for i in range(ii, a.shape[0], frm/2):
                    sys.stdout.write('\b'*10)
                    sys.stdout.write('%10d' % a['t'][i])
                    ii = i
                    if (max(a['v'][i:i+frm]) - min(a['v'][i:i+frm])) > diap and \
                            not ( (a['v'][i] > a['v'][i+frm]) ^ direction):
                        foundr = i
                        break
                print '\n'
                if not foundr:
                    j += 1
                    break
                # precise search
                for i in range(foundr - 100, foundr + 100):
                    if (max(a['v'][i:i+frm]) - min(a['v'][i:i+frm])) > diap and \
                            not ( (a['v'][i] > a['v'][i+frm]) ^ direction):
                        z[i-foundr+100] = True
                found = 0
                for i in range(200):
                    if z[i:i+15].all():
                        found = a['t'][foundr - 100 + i]
                        break
                if found:
                    shifts.append(found)
                    print 'Found (%c) shift: %d' % ( '-' if direction else '+', found)
                ii += frm
        # may be need:
        del a; del z;
        return shifts

def preciseShiftsPositioning(ldr, shifts, frm):
        for j in range(len(shifts)):
            shift = shifts[j]
            a = ldr.getPartT(shift)
            i1 = a['t'].searchsorted(shift)
            i2 = i1 + 2*frm
            minsum = 1e10
            shift_precise = 0
            for i in range(i1,i2):
                med = ( a['v'][i1:i1+2].mean() + a['v'][i2:i2+2].mean() ) / 2
                if abs( (a['v'][i1:i2]-med).sum() ) < minsum:
                    shift_precise = ( a['t'][i1] + a['t'][i2] ) / 2
            shifts[j] = shift_precise
            print shift_precise
            del a;
        return shifts

