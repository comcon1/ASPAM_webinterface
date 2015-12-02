# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 21:40:18 2015

@author: comcon1
"""

from config import *
from servutils import Page, mkGetRequest
from experiment import Experiment

class ExperimentsBlock(Page):
    
    def __init__(self):
        super(ExperimentsBlock, self).__init__(os.path.join(DQTEMPLDIR,'index_experiment.xml'))

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
        self._tmpl.sub('state_string', ex.STATE_TO_STR[ex.state])
        self._tmpl.sub('datestart', ex.datestr)
        self._tmpl.sub('name', exp)
        self._tmpl.sub('comment', ex.comment)
        self._tmpl.sub('uri', '/expreview'+mkGetRequest(code=exp,fastpreview=True, regen_cache=True))
        self._tmpl.sub('STOP_LINK', '/action'+mkGetRequest(action='chstate_experiment', after_action='/index', code=exp, newstate=0))
        self._tmpl.sub('PAUSE_LINK', '/action'+mkGetRequest(action='chstate_experiment', after_action='/index', code=exp, newstate=1))
        self._tmpl.sub('START_LINK', '/action'+mkGetRequest(action='chstate_experiment', after_action='/index', code=exp, newstate=2))
        self._tmpl.sub('FCSV_LINK', '/expreview/csv'+mkGetRequest(code=exp,yunits=params.download.defcsvunits))
        return self._tmpl.string

class IndexPage(Page):

    def __init__(self, contrl):
        self._dqc = contrl
        super(IndexPage, self).__init__(os.path.join(DQTEMPLDIR,'index.xml'))

    def index(self):
        self._tmpl.reset()
        self._tmpl.sub('prog_name', DQSPRGNAME)
        self._tmpl.sub('prog_version', DQSVERSION)
        
        exprs = ExperimentsBlock()
        self._tmpl.sub( 'experiments_list', exprs.getList() )
        
        self._tmpl.sub( 'new_exp_ref', '/control/newexperiment' )
        
        return self._tmpl.string
        
    index.exposed = True
    
