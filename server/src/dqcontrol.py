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
        expdir = os.path.join(DQSROOTDIR, self._expcode)
        assert(os.path.isdir(expdir))
        args = [lgr, '-d', '-p', os.path.join(expdir, 'logger.pid'), \
            '-o', os.path.join(expdir, 'data00.xvg'), '-l', \
            os.path.join(expdir, 'logger.log')]
        if True:
            args.append('-i')
            args.append('-f')
            args.append(os.path.join(DQSERVROOT,'dfi02.xvg'))
        # pointing DEVICE is optional!
        self._daemon = subprocess.Popen(args, \
            shell=False)
    
    def stop_logger(self):
        print 'Stopping logger for %s!' % (self._expcode)
        if (self._daemon == None):
            # nothing to do
            return
        self._daemon.terminate()
        self._daemon.wait()
        self._daemon = None
    
    def set_experiment(self, expcode):
        if self._daemon != None:
            raise AttributeError('Can not change experiment while logger is run!')
        if expcode != None:
            expdir = os.path.join(DQSROOTDIR, expcode)
            assert(os.path.isdir(expdir))
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
                os.kill(self._daemon.pid, 0) # it is a check-signal
            except OSError as e:
                print 'Some error occured: ' + str(e)
                print 'Restarting logger after 10 seconds'
                time.sleep(10)
                self.start_logger()
        
