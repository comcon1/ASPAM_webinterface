# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 21:43:59 2015

@author: comcon1
"""

from config import *
from servutils import Page,Experiment, mkCheckBox
import libDQimage as qi
import libdaq as dq 

class ExperimentReview(Page):

    def __init__(self):
        super(ExperimentReview, self).__init__('../templates/expreview.xml')    
    
    def index(self, code=None, ratlist=None, nrats=None, zoom=None):
        self._tmpl.reset();
        
        if code == None:
            return 'Specify code!'
        self._tmpl.sub('expcode', code)
        ex = Experiment(os.path.join(self._edir, code))
        
        if (ratlist != None):
            self._selected_rats = dict.fromkeys(range(1, ex.nrats+1), False)
            for i in map(int, ratlist.split(',')):
                self._selected_rats[i] = True
        else:
            self._selected_rats = dict.fromkeys(range(1, ex.nrats+1), True)
        self._tmpl.sub('nrats', ex.nrats)
        
        self._tmpl.sub('ratcheckbox', mkCheckBox(self._selected_rats, 'selectedrats'))

        rca = dq.RotCurveAnalyzer(os.path.join(ex._dir,'data00.xvg'))
        
        ip0 = qi.RotImageParameters(rca.loader)
        ip0.setDiap(None, None)
        ip0.setFigSize((5,3))
        __ratlist = [k for k,v in self._selected_rats.iteritems() if v]

        ip0.setRatList(__ratlist)
        ip0.setPlotType('raw')
        ir0 = qi.RotImageRequest(rca, ip0)
        ip0.setPlotType('cumulative')
        ir1 = qi.RotImageRequest(rca, ip0)
        
        self._tmpl.sub('nrats', ex.nrats);
        self._tmpl.sub('simplot', '/plotdata/'+ir0.getImage(absolute=False) )
        self._tmpl.sub('cumplot', '/plotdata/'+ir1.getImage(absolute=False) )
        
        return self._tmpl.string
    
    index.exposed = True