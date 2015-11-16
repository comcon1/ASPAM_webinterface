# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 21:43:59 2015

@author: comcon1
"""

from config import *
from servutils import *
import cherrypy
from experiment import Experiment
from cherrypy.lib import static

class TimeStatistics(Page):
    
    def __init__(self):
        super(TimeStatistics, self).__init__('../templates/timestat.xml') 

    def index(self, code=None, ratlist=None, nrats=None, scale='5:3', yunits='meters',
              regen_cache=False, fromdate=None, tilldate=None, dayflag=3):
                  
        if code is None:
            return 'Specify code!'
        self._ex = Experiment(os.path.join(self._edir, code))
        
        if (ratlist is not None):
            self._selected_rats = dict.fromkeys(range(1, self._ex.nrats+1), False)
            for i in map(int, ratlist.split(',')):
                self._selected_rats[i] = True
        else:
            self._selected_rats = dict.fromkeys(range(1, self._ex.nrats+1), True)
        
        rca = dq.RotCurveAnalyzer(os.path.join(self._ex._dir,'data00.xvg'))
        ip0 = qi.RotImageParameters(rca.loader)    
        
        self._fromdate = dq.tu.lower_day(ip0.bt) if fromdate is None else int(fromdate)
        self._tilldate = dq.tu.lower_day(ip0.et) if tilldate is None else int(tilldate)
        
        ip0.setDiapT(self._fromdate, self._tilldate+24*3600)
        ip0.setFigSize(tuple(map(float,scale.split(':'))))
        __ratlist = [k for k,v in self._selected_rats.iteritems() if v]

        ip0.setRatList(__ratlist)
        ip0.Yunits = yunits
        if regen_cache:
            ip0.setRegen()

        ip0.plotType = 'timecumulate'
        ir0 = qi.RotImageRequest(rca, ip0)

        self._tmpl.reset();
        self._tmpl.sub('expcode', code)
        self._tmpl.sub('nrats', self._ex.nrats)        
        self._tmpl.sub('ratcheckbox', mkCheckBox(self._selected_rats, 'selectedrats'))
        self._tmpl.sub('unitscombo', mkComboBox({'meters':'meters','turns':'turns'}, yunits, 'yunits'))
        self._tmpl.sub('scalecombo', mkComboBox({'5:3':'50%','7.5:4.5':'75%','10:6':'100%'}, scale, 'scale'))
        self._tmpl.sub('fromdate', mkDateCombo(ip0.bt, ip0.et, self._fromdate, 'fromdate') )
        self._tmpl.sub('tilldate', mkDateCombo(ip0.bt, ip0.et, self._tilldate, 'tilldate') )
        self._tmpl.sub('nrats', self._ex.nrats);
        self._tmpl.sub('plot', '/plotdata/'+ir0.getImage(absolute=False) )
        self._tmpl.sub('regenchecked', '')
        
        self._tmpl.sub('download_png', '/ratstat/download'+mkGetRequest(code=code, ratlist=','.join(map(str,__ratlist)), \
            scale=scale, yunits=yunits, fromdate=self._fromdate, tilldate=self._tilldate, imgtyp='raw', fmt='png') )
        
        return self._tmpl.string
    
    index.exposed = True