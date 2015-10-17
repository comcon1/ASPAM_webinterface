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
    ''' Root abstract class for every HTML page. '''
     
    def __init__(self, fname):
        if fname == None:
            #TODO: implement DO_NOT_LOAD_PAGE_CLASS_ITSELF
            pass
        else:
            self._tmpl = XMLTemplate(fname)
            self._edir = os.path.join(DQSROOTDIR, 'expdata')
        
    def errorPage(self, e):
        self._tmpl = XMLTemplate('../templates/errorPage.xml')
        self._tmpl.sub('type', str(type(e)).split("'")[1])
        self._tmpl.sub('message', str(e) )
        
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        self._tmpl.sub('position', '%s:%d' % (fname, exc_tb.tb_lineno) )
        
        return self._tmpl.string
        

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