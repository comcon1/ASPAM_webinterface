#!/usr/bin/python
import os, sys, serial, time, argparse, glob, random, signal, ctypes
import os.path, termios
from datetime import datetime
dev_pat = "/dev/LOGGER*"

libc = ctypes.cdll.LoadLibrary("libc.so.6")
mask = '\x00' * 17 # 16 byte empty mask + null terminator 
libc.sigprocmask(2, mask, None)

timestamp = lambda: time.strftime("%Y-%m-%d_%H:%M:%S")

def connect(dev = None, ntry=-1):
  status_ok = 0
  while 1:
    try:
      if ntry > 0: ntry-=1
      if not dev: dev=dev_find()
      if dev:
        sr = serial.Serial(port=dev, timeout=2.0, baudrate=115200)
        status_ok = 1
        break
      else:
        print("Device not found")
        time.sleep(1)
      if ntry == 0: break
    except:
      dev = None
      print(sys.exc_info()[1])
#  while len(sr.read(1))>0: pass
  if status_ok:
    sr.write("\recho 0\r")
    time.sleep(1)
    sr.flushInput()
    return sr
  else:
    raise NameError, "Device not found"

 
def dev_find():
  d = glob.glob(dev_pat)
  if not len(d): return None # raise NameError, "Device not found"
  return d[-1] # Only one device is supported

class FakeSerial:
  def __init__(self, *args):
    pass

  def readline(self):
    return reduce(lambda a,b: a+b, map(lambda n: "%d "%n, map(lambda i: random.randint(0,4096), range(4))))

  def close(self):
    pass

  def write(self,s):
    pass

prs = argparse.ArgumentParser(description="")
prs.add_argument('-p', dest="lockf", metavar='FILENAME', type=str, help='lock file', default='logger.pid')
prs.add_argument('-t', dest='period', metavar='N', type=float, help='data collection period',default=1.0)
prs.add_argument('-o', dest="out", metavar='FILE', type=str, help='output file',default='logger.dat')
prs.add_argument('-f', dest="dev", metavar='/dev/ttyX', type=str, help='device file')
prs.add_argument('-d', dest="daemon",  action="store_true", help='daemonize')
prs.add_argument('-l', dest="log", metavar='FILE', type=str, help='log file',default='logger.log')
prs.add_argument('-i', dest="imitate", action="store_true", help='start imitational version')
args = prs.parse_args()

def bye(sig,fr):
  print("%s Logger stopped"%timestamp())
  os.unlink(args.lockf)
  sys.exit(0)


if args.daemon:
  if os.fork() > 0:
    sys.exit(0)
  os.setsid()
  if os.fork() > 0: sys.exit(0)
  os.umask(0)
  import resource		# Resource usage information.
  maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
  if (maxfd == resource.RLIM_INFINITY):
    maxfd = 1024
  for fd in range(0, maxfd):
    try:
      os.close(fd)
    except OSError:	# ERROR, fd wasn't open to begin with (ignored)
      pass

signal.signal(signal.SIGTERM,bye)

sys.stdin = open('/dev/null', 'r')
sys.stdout = open(args.log, 'a+',0)
sys.stderr = open(args.log, 'a+',0)


lck = open(args.lockf, 'w')
lck.write(str(os.getpid()))
lck.close()

is_continue = os.path.isfile(args.out)
period = int(args.period)

if is_continue:
	out = open(args.out, 'a+b')
	outsz = os.stat(args.out).st_size
	out.seek(outsz)
	out.seek(-1,1)
	if ( out.read(1) != '\n'):
	    print 'Incorrect file finalization!'
	    raise NotImplementedError('Refinalization was not realized!')
	# skip the last break
	out.seek(-1,1)
	# exclude the last string
	lastsymb = ''
	laststr = ''
	while lastsymb != '\n':
	  laststr = lastsymb + laststr
	  out.seek(-1,1)
	  lastsymb = out.read(1)
	  out.seek(-1,1)
	# exclude information about num of channels
	lastar = laststr.split()
	# skip the pre-last break
	out.seek(-1,1)
	# exclude the pre-last string
	lastsymb = ''
	laststr = ''
	while lastsymb != '\n':
	  laststr = lastsymb + laststr
	  out.seek(-1,1)
	  lastsymb = out.read(1)
	  out.seek(-1,1)
	# exclude information about num of channels
	prelastar = laststr.split()

	newnchan = len(lastar)-1
	print 'Number-of-channels (%d) was excluded from the dump!' % (newnchan)
		
	newperiod = int(lastar[0]) - int(prelastar[0])
	if (period == newperiod):
		pass
	else:
		period = newperiod
		print 'Force setting up the %d for the period!' % period

	out.close()
	
	out = open(args.out, 'a+')
	zers = ''.join(map(lambda v: "%5d" % v, [0]*newnchan)) + '\n'
	tnow = int(time.time())
	lasttime = int(lastar[0])
	nskipp = (tnow-lasttime)/period+3 # 3 periods - is time buffer!!
	t = 0
	for i in range(nskipp):
		t = lasttime+period*(i+1)
		out.write("%11d" %  t)
		out.write(zers)
		out.flush()
	time.sleep(-time.time()+t+period)
	out.close()
	
	
out = open(args.out, 'a+')

if args.imitate:
    # imitational behavior of the DAEMON
    pass
    # uses device string as filename
    import os.path
    if not os.path.isfile(args.dev):
        sys.stderr.write('Cannot open file %s for imitation!' % (args.dev))
        sys.exit(1)
    
    imitf = open(args.dev, 'r')
    file_line = '# oo'
    while file_line[0] == '#':
        file_line = imitf.readline()
    oridata = imitf.tell() - len(file_line) # the position BEFORE first data string
    imitf.seek(oridata)
    nchan = len(file_line.strip().split())
    tstart=time.time()

    print("%s Logger started"%timestamp())
    if not is_continue: 
        out.write("# LOGGER started @ %s\n#\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
    
    while True:
        
        file_line = imitf.readline().strip()
        vals_dif = map(int,file_line.split()[1:])
        
        out.write("%11d" % time.time() )
        out.write(''.join(map(lambda v: "%5d" % v, vals_dif)) + "\n")
        out.flush()
        
        tnow = time.time()
        icycle = int((tnow - tstart) / period)
        tnext = tstart + (icycle + 1) * period
        time.sleep(tnext - tnow)
        if imitf.tell() == os.fstat(imitf.fileno()).st_size:
            print 'Logger reads imitation file from the very beggining!'
            imitf.seek(oridata)
else:
    # normal execution of the DAEMON
    # dev = args.dev if args.dev else dev_find()
    sr = connect(args.dev, ntry=1)
    # while len(sr.read(1))>0: pass
    # sr = FakeSerial()
    
    nchan = 0
    tstart=time.time()
    print("%s Logger started"%timestamp())
    if not is_continue: 
        out.write("# LOGGER started @ %s\n#\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
    while True:
      tBeforeComReq = time.time()
      try:
        sr.flushInput()
        sr.write("cnt\r")
        s = sr.readline()
        sr.write("adc 0\r")
        sadc = sr.readline()
      except (serial.serialutil.SerialException, termios.error) as err:
        print("%s Error communicating to device: %s" % (timestamp(),str(err)))
        sr.close()
        time.sleep(1)
        # sys.stdout.flush()
        sr = connect() #serial.Serial(port=dev_find(), timeout=0.5)
        # while len(sr.read(1))>0: pass
        print("%s Reconnected to device" % timestamp())
      finally:
        tAfterComReq = time.time()
    
      try:
        vals = map(int, s.split())
        if nchan > 0 and len(vals) != nchan:
          raise NameError
      except:
        print("%s Corrupted reply string '%s'" % (timestamp(),s))
        continue
      
      if nchan == 0:
        nchan = len(vals)
        vals_prev = vals
        print("%s Number of channels: %d" % (timestamp(), nchan))
        #TODO: determine number of channels from the file!
        if not is_continue:
            out.write("# Number of channels: %d\n" % nchan)
            out.write('# timestamp '+''.join(map(lambda i: " channel-%d" % i, range(nchan))) + "\n#\n")
    
      vals_dif = []
      for i in xrange(nchan):
        # it occurs when hard reconnect
        if vals[i] < vals_prev[i]:
            vals_dif.append(0)
        else:
            vals_dif.append(vals[i] - vals_prev[i])
    
      vals_prev = vals
    
      tnow = time.time()

      out.write("%11d" % tnow)
      out.write(''.join(map(lambda v: "%5d" % v, vals_dif)) + "\n")
      out.flush()
      print "%-27s ==> %-6s | %-8.3f" % ( str(datetime.now()), sadc.strip(), \
              (int((tAfterComReq-tBeforeComReq)*1000)) )
    
      icycle = int((tnow - tstart) / period)
      tnext = tstart + (icycle + 1) * period
      time.sleep(tnext - tnow)
