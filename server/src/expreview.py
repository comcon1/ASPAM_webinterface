# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 21:43:59 2015

@author: comcon1
"""

from config import *
from servutils import *
from experiment import Experiment
import cherrypy
from cherrypy.lib import static
import shlex, subprocess, re

class ExperimentReview(Page):

    def __init__(self):
        super(ExperimentReview, self).__init__(os.path.join(DQTEMPLDIR,'expreview.xml')) 
    
    def index(self, code=None, ratlist=None, nrats=None, scale='5:3', yunits='meters',
              regen_cache=False, fromdate=None, tilldate=None):
        
        if code is None:
            return 'Specify code!'
        self._ex = Experiment(os.path.join(self._edir, code))
        
        if (ratlist is not None):
            self._selected_rats = dict.fromkeys(range(1, self._ex.nrats+1), False)
            for i in map(int, ratlist.split(',')):
                self._selected_rats[i] = True
        else:
            self._selected_rats = dict.fromkeys(range(1, self._ex.nrats+1), True)
        __ratlist = [k for k,v in self._selected_rats.iteritems() if v]
        
        command = os.path.join(os.path.dirname(__file__), 'image_loader.py')
        command += ' -x expreview_raw'
        command += ' -d '+ self._ex._dir
        command += ' -i '+ 'data00.xvg'
        if fromdate is not None:
            command += ' -f '+ fromdate
        if tilldate is not None:
            command += ' -t '+ tilldate
        if regen_cache:
            command += ' -u'
        command += ' -s '+ scale
        command += ' -r' + ','.join(map(str,__ratlist))
        command += ' -y ' + yunits
        print command

        pp = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        output,err = pp.communicate()
        for lin in output.split('\n'):
            m0 = re.match(r'^RESULT_BT\:\s*([0-9]+)\s*$', lin)
            if m0 is not None:
                result_bt = int(m0.group(1))
                continue
            m0 = re.match(r'^RESULT_ET\:\s*([0-9]+)\s*$', lin)
            if m0 is not None:
                result_et = int(m0.group(1))
                continue
            m0 = re.match(r'^IMAGE_PATH\:(.+)$', lin)
            if m0 is not None:
                raw_image = m0.group(1)
                continue

        command = os.path.join(os.path.dirname(__file__), 'image_loader.py')
        command += ' -x expreview_cumulative'
        command += ' -d '+ self._ex._dir
        command += ' -i '+ 'data00.xvg'
        if fromdate is not None:
            command += ' -f '+ fromdate
        if tilldate is not None:
            command += ' -t '+ tilldate
        if regen_cache:
            command += ' -u'
        command += ' -s '+ scale
        command += ' -r' + ','.join(map(str,__ratlist))
        command += ' -y ' + yunits
        print command

        pp = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        output,err = pp.communicate()
        for lin in output.split('\n'):
            m0 = re.match(r'^RESULT_BT\:\s*([0-9]+)\s*$', lin)
            if m0 is not None:
                result_bt = int(m0.group(1))
                continue
            m0 = re.match(r'^RESULT_ET\:\s*([0-9]+)\s*$', lin)
            if m0 is not None:
                result_et = int(m0.group(1))
                continue
            m0 = re.match(r'^IMAGE_PATH\:(.+)$', lin)
            if m0 is not None:
                cum_image = m0.group(1)
                continue
        
        _fromdate = dq.tu.lower_day(result_bt) if fromdate == None else int(fromdate)
        _tilldate = dq.tu.lower_day(result_et) if tilldate == None else int(tilldate)

        self._tmpl.reset();
        self._tmpl.sub('expcode', code)
        self._tmpl.sub('nrats', self._ex.nrats)        
        self._tmpl.sub('ratcheckbox', mkCheckBox(self._selected_rats, 'selectedrats'))
        self._tmpl.sub('unitscombo', mkComboBox({'meters':'meters','turns':'turns'}, yunits, 'yunits'))
        self._tmpl.sub('scalecombo', mkComboBox({'5:3':'50%','7.5:4.5':'75%','10:6':'100%'}, scale, 'scale'))
        self._tmpl.sub('fromdate', mkDateCombo(result_bt, result_et, _fromdate, 'fromdate', addspecial=['hour_ago']) )
        self._tmpl.sub('tilldate', mkDateCombo(result_bt, result_et, _tilldate, 'tilldate', addspecial=['now']) )
        self._tmpl.sub('nrats', self._ex.nrats);
        self._tmpl.sub('simplot', '/plotdata/'+raw_image )
        self._tmpl.sub('cumplot', '/plotdata/'+cum_image )
        self._tmpl.sub('regenchecked', '')
        
        self._tmpl.sub('download_simplot_png', '/expreview/download'+mkGetRequest(code=code, ratlist=','.join(map(str,__ratlist)), \
            scale=scale, yunits=yunits, fromdate=_fromdate, tilldate=_tilldate, imgtyp='raw', fmt='png') )
        
        return self._tmpl.string
    
    index.exposed = True
    
    def download(self, code=None, ratlist=None, scale='5:3', yunits='meters',
              fromdate=None, tilldate=None, imgtyp='raw', fmt='png'):
        
        if code is None:
            return 'Specify code!'
        if imgtyp not in ['raw', 'cumulative']:
            raise AttributeError('This image type (%s) is not implemented!', imgtyp)
            
        self._ex = Experiment(os.path.join(self._edir, code))       
        self._selected_rats = dict.fromkeys(range(1, self._ex.nrats+1), True)
        
        rca = dq.RotCurveAnalyzer(os.path.join(self._ex._dir,'data00.xvg'))
        ip0 = qi.RotImageParameters(rca.loader)    
        
        self._fromdate = int(fromdate)
        self._tilldate = int(tilldate)
        
        ip0.setDiapT(self._fromdate, self._tilldate+24*3600)
        ip0.setFigSize(tuple(map(float,scale.split(':'))))
        __ratlist = [k for k,v in self._selected_rats.iteritems() if v]

        ip0.setRatList(__ratlist)
        ip0.Yunits = yunits

        ip0.plotType = str(imgtyp)        
        ir0 = qi.RotImageDownload(rca, ip0, fmt)

        path = ir0.getImage(absolute=True)
        print path
        return static.serve_file(path, "application/x-download",
                                 "attachment", os.path.basename(path))

        
        return self._tmpl.string
    
    download.exposed = True
