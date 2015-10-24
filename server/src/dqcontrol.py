# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 16:22:17 2015

@author: comcon1
"""

from config import *
from threading import Thread
import os, os.path
import subprocess, signal, time

class DQController(Thread):
    ''' DQController is a singleton Thread implemented class that control the
    execution of the logger script. '''
    
    def __init__(self):
        self._daemon = None
        self._expcode = None
        Thread.__init__(self)
    
    def start_logger(self):
        assert(self._expcode != None)
        lgr = os.path.join(DQSERVROOT, 'logger.py')
        expdir = os.path.join(DQEXPDATADIR, self._expcode)
        assert(os.path.isdir(expdir))
        args = [lgr, '-d', '-p', os.path.join(expdir, 'logger.pid'), \
            '-o', os.path.join(expdir, 'data00.xvg'), '-l', \
            os.path.join(expdir, 'logger.log')]
        # guess an imitate mode
        imitateMode = None
        try:
            if (int(params.daq.workingModeImitate) == 1):
                imitateMode = True
        except:
            print 'Logger working mode is node defined in params [daq.workingModeImitate] variable.'            
            imitateMode = True
        # guess device file
        deviceFile = None
        try:
            deviceFile = os.path.join(DQSERVROOT, params.daq.deviceFile)
        except:
            print 'Logger device-file is not defined in params [daq.deviceFile] variable.'
            if imitateMode:
                print 'File `dfi02.xvg` will be used by default!'
                deviceFile = os.path.join(DQSERVROOT,'dfi02.xvg')
            else:
                print 'Device file will be guess by logger script!'
                deviceFile = None
        if imitateMode:
            print 'Imitate mode is activated!'
            args.append('-i')
        # device file could be set for imitate mode (text) or for working mode (device)
        if deviceFile != None:
            args.append('-f')
            args.append(deviceFile)
        # run the process
        subprocess.Popen(args, shell=False)
        while True:
            try:
                f = open(os.path.join(expdir, 'logger.pid'))
                self._daemon =  int(f.readline().strip())
                f.close()
            except IOError:
                time.sleep(0.5)
                continue
            break

    def _isrunning(self):
        if not os.path.isfile("/proc/%s/cmdline"%self._daemon): 
            print '<a>'
            return False
        f=open("/proc/%s/cmdline"%self._daemon,'r')
        cmd = f.readline().split('\x00')
        f.close()
        if len(cmd)<2:
            print '<b>'
            return False
        if not (cmd[0].split('/')[-1]=='python' and cmd[1].split('/')[-1]=='logger.py'):
            print '<c>'
            return False
        return True
    
    def stop_logger(self):
        if (self._daemon == None):
            # nothing to do
            return
        pidfile = os.path.join(DQEXPDATADIR, self._expcode, 'logger.pid')
        print 'Stopping logger for %s: %d!' % (self._expcode, self._daemon)
        if self._isrunning():
            os.kill(self._daemon, signal.SIGTERM )
            counter = 0
            while True:
                try:
                    os.kill(self._daemon, 0)
                except OSError:
                    print '[Killing..]'
                    time.sleep(1)
                    counter += 1
                    continue
                if counter == 5:
                    os.kill(self._daemon, signal.SIGKILL )
                    print '[We need to send SIGKILL]'
                    os.unlink(pidfile)
                    break
                break
        else:
            print 'Logger died incorrectly!'
            if os.path.isfile(pidfile):
                os.unlink(pidfile)            

        self._daemon = None
        print 'Logger was stoped!'
    
    def set_experiment(self, expcode):
        if self._daemon != None:
            raise AttributeError('Can not change experiment while logger is run!')
        if expcode != None:
            expdir = os.path.join(DQEXPDATADIR, expcode)
            if not os.path.isdir(expdir):
                raise OSError, 'directory '+expdir+' not found.'
        self._expcode = expcode
        
    
    def get_experiment(self):
        return self._expcode
    
    def is_started(self):
        return self._daemon != None
    
    def run(self):
        print 'Starting logger for %s!' % (self._expcode)
        while True:
            time.sleep(2)
            if self._daemon == None:
                continue
            try:
                os.kill(self._daemon, 0) # it is a check-signal
            except OSError as e:
                print 'Some error occured: ' + str(e)
                print 'Restarting logger after 10 seconds'
                time.sleep(10)
                self.start_logger()
        
