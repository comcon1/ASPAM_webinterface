# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 21:40:18 2015

@author: comcon1
"""

from config import *
from servutils import Page, Experiment

class ExperimentsBlock(Page):
    
    def __init__(self):
        super(ExperimentsBlock, self).__init__('../templates/index_experiment.xml')

    def getList(self):
        assert(os.path.isdir(self._edir))
        exps = os.listdir(self._edir)
        ol = []
        for exp in exps:
            ol.append( self._one(exp) )
        return '\n'.join(ol)
        
    def _one(self, exp):
        ex = Experiment(os.path.join(self._edir, exp))
        # substituting
        self._tmpl.reset()
        self._tmpl.sub('nrats', ex.nrats)
        self._tmpl.sub('datestart', ex.datestr)
        self._tmpl.sub('name', exp)
        self._tmpl.sub('comment', ex.comment)
        self._tmpl.sub('uri', '/expreview?code='+exp)
        return self._tmpl.string

class IndexPage(Page):

    def __init__(self, contrl):
        self._dqc = contrl
        super(IndexPage, self).__init__('../templates/index.xml')

    def index(self):
        self._tmpl.sub('prog_name', DQSPRGNAME)
        self._tmpl.sub('prog_version', DQSVERSION)
        
        exprs = ExperimentsBlock()
        self._tmpl.sub( 'experiments_list', exprs.getList() )
        
        return self._tmpl.string
        
    index.exposed = True
    
