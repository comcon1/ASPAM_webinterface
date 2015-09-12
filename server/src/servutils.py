# -*- coding: utf-8 -*-

import os
from config import *
import numpy as np
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
    '''
    Experiment *class* parses data XML and check its correctness.

    
    ==Properties==

    $datestr$ and $datestart$ - is start of the experiment in string and timestamp formats.

    $nrats$ - number of total channels.

    $comment$ - *string* comment.
    
    Timesettings of summation: $daystart$ is a time of day. $morning$ - time 
    of lightday. $evening$ - start of nightday. Either day or night may consists
    of two pieces.'''
    
    def __init__(self, dirpath):
        '''Constructor is initialized with a directory wich contains data and 
        settings file called 'daq.xml'. '''
        self._dir = dirpath
        xx = lx.parseFile(os.path.join(self._dir, 'daq.xml'))
        ch = xx.xpathEval('/experiment')[0]
        self._nrats = int(ch.hasProp('nrats').content)
        self._datestart = int(ch.hasProp('datestart').content)
        ch = xx.xpathEval('/experiment/comment')[0]
        self._comment = ch.content
        # *************
        ch = xx.xpathEval('/experiment/timesettings')[0]
        self._daystart = str(ch.hasProp('daystart').content)
        self._morning = str(ch.hasProp('morning').content)
        self._evening = str(ch.hasProp('evening').content)
        assert( self.daystart)
    
    @property 
    def datestr(self):
        return time.strftime('%d.%m.%y %H:%M', \
            time.localtime(self._datestart) )
    @property 
    def daystart(self):
        return self._daystart
    
    @property 
    def nrats(self):
        return self._nrats
        
    @property 
    def comment(self):
        return self._comment
    
    @property 
    def morning(self):
        return self._morning
    
    @property 
    def evening(self):
        return self._evening

def mkCheckBox(dic, name, id=None, cls=None):
    #TODO: implement class *cls*
    assert(type(dic) == dict)
    checks = []
    i = 0
    for key in dic.keys():  
        s = '<input type="checkbox" id="%s" value="%s" %s/> '\
           % (name+'_'+str(key), str(key), 'checked' if dic[key] else '')
        checks.append(s)
        if dic[key]:
            color = params.curves['r%d'%i].color
            i += 1
        else:
            color = '#dddddd'
        s = '<label for="%s" style="color: %s;">Rat №%s</label>' % \
            (name+'_'+str(key), color, str(key))
        checks.append(s)
    return '\n'.join(checks)

def mkComboBox(dic, selected, name, id=None, cls=None, sort_flag=False):
        #TODO: implement class *cls*
    assert(type(dic) == dict)
    l = []
    l.append('<select size="1" name="%s">' % name)
    kar = np.sort(dic.keys()) if sort_flag else dic.keys()
    for key in kar:  
        s = '<option value="%s" %s>%s</option> ' % (str(key),\
          'selected' if str(key) == str(selected) else '', dic[key])
        l.append(s)
    l.append('</select>')
    return '\n'.join(l)
    
def mkDateCombo(startt, stopt, curt, name, id=None, cls=None):
    zz = np.arange(dq.tu.lower_day(startt), dq.tu.lower_day(stopt)+1, step=24*3600)
    dates = map(lambda x: time.strftime('%d.%m',time.localtime(x)), zz)
    dic = dict(zip(zz,dates))
    return mkComboBox(dic, curt, name, id, cls, sort_flag=True)

def mkGetRequest(**kwargs):
    #TODO: make character safety
    s = []
    for k,v in kwargs.iteritems():
        _s = str(k)+'='+str(v)
        _s = _s.replace(' ', '%20')
        s.append(_s)
    return '?'+'&'.join(s)