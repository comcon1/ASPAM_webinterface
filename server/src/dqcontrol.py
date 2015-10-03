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
    
    def __init__(self):
        self._daemon = None
        self._expcode = None
        Thread.__init__(self)
    
    def start_logger(self):
        lgr = os.path.join(DQSERVROOT, 'logger.py')
        expdir = os.path.join(DQSROOTDIR, self._expcode)
        assert(os.path.isdir(expdir))
        args = [lgr, '-d', '-p', os.path.join(expdir, 'logger.pid'), \
            '-o', os.path.join(expdir, 'data00.xvg')]
        # pointing DEVICE is optional!
        self._daemon = subprocess.Popen(args, \
            shell=False)
    
    def stop_logger(self):
        if (self._daemon == None):
            # nothing to do
            return
        self._daemon.terminate()
        self._daemon.wait()
    
    def change_experiment(self,expcode):
        if (expcode == self._expcode):
            return
        self._stop_logger()
        self._expcode = expcode
    
    def get_current_experiment(self):
        return self._expcode if self._expcode != None else 'NOT_SELECTED'
    
    def run(self):
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
        
