# -*- coding: utf-8 -*-

import os
from config import *
import time
import libxml2 as lx

class XMLTemplate(object):
    
    def __init__(self, fname):
        assert(os.path.isfile(fname))
        self._fname = fname
        self._load()
    
    def _load(self):
        f = open(self._fname, 'r')
        self._str = f.read()
        self._ori = self._str
        f.close()
    
    def sub(self, key, value):
        self._str = self._str.replace('##'+key+'##', str(value) )
        
    def reset(self):
        self._str = self._ori
        
    @property
    def string(self):
        return self._str
        
    def allKeys(self):
        raise NotImplementedError('allKeys not implemented!')

class Page(object):
    
    def __init__(self, fname):
        self._tmpl = XMLTemplate(fname)
        self._edir = os.path.join(DQSROOTDIR, 'expdata')

class Experiment(object):
    
    def __init__(self, dirpath):
        self._dir = dirpath
        xx = lx.parseFile(os.path.join(self._dir, 'daq.xml'))
        ch = xx.xpathEval('/experiment')[0]
        self._nrats = int(ch.hasProp('nrats').content)
        self._datestart = int(ch.hasProp('datestart').content)
        ch = xx.xpathEval('/experiment/comment')[0]
        self._comment = ch.content
    
    @property
    def datestr(self):
        return time.strftime('%d.%m.%y %H:%M', \
            time.localtime(self._datestart) )
    
    @property
    def nrats(self):
        return self._nrats
        
    @property
    def comment(self):
        return self._comment

def mkCheckBox(dic, name, id=None, cls=None):
    #TODO: implement class *cls*
    assert(type(dic) == dict)
    checks = []
    for key in dic.keys():  
        s = '<input type="checkbox" name="%s[]" id="%s" value="%s" %s/> '\
           % (name, name+'_'+str(key), str(key), 'checked' if dic[key] else '')
        checks.append(s)
        s = '<label for="%s">%s</label>' % (name+'_'+str(key), str(key))
        checks.append(s)
    return '\n'.join(checks)