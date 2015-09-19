#!/usr/bin/python
import os, sys, serial, time, argparse, glob, random, signal, ctypes
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
        sr = serial.Serial(port=dev, timeout=0.5, baudrate=115200)
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
    sr.write("\n")
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
args = prs.parse_args()

def bye(sig,fr):
  print("%s Logger stopped"%timestamp())
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
out = open(args.out, 'w')
#dev = args.dev if args.dev else dev_find()
sr = connect(args.dev, ntry=1)
#while len(sr.read(1))>0: pass
#sr = FakeSerial()



nchan = 0
tstart=time.time()
print("%s Logger started"%timestamp())
out.write("# LOGGER started @ %s\n#\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
while True:
  try:
    sr.flushInput()
    sr.write("cnt\n")
    s = sr.readline()
  except (serial.serialutil.SerialException, serial.termios.error) as err:
    print("%s Error communicating to device: %s"%(timestamp(),str(err)))
    sr.close()
    time.sleep(1)
#      sys.stdout.flush()
    sr = connect() #serial.Serial(port=dev_find(), timeout=0.5)
#    while len(sr.read(1))>0: pass
    print("%s Reconnected to device"%timestamp())

  try:
    vals = map(int, s.split())
    if nchan > 0 and len(vals) != nchan:
      raise NameError
  except:
    print("%s Corrupted reply string '%s'"%(timestamp(),s))
    continue

  if nchan == 0:
    nchan = len(vals)
    vals_prev = vals
    print("%s Number of channels: %d" % (timestamp(), nchan))
    out.write("# Number of channels: %d\n" % nchan)
    out.write(reduce(lambda a, b: a + b, map(lambda i: " channel-%d" % i, range(nchan)), "# time(sec)") + "\n#\n")

  vals_dif = []
  for i in xrange(nchan):
    vals_dif.append(vals[i] - vals_prev[i])

  vals_prev = vals

  out.write("%.0f" % (time.time() - tstart))
  out.write(reduce(lambda a, b: a + b, map(lambda v: " %d" % v, vals_dif)) + "\n")
  out.flush()

  tnow = time.time()
  icycle = int((tnow - tstart) / args.period)
  tnext = tstart + (icycle + 1) * args.period
  time.sleep(tnext - tnow)
