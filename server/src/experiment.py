# -*- coding: utf-8 -*-

from config import *
import libxml2 as lx
from servutils import Page

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
    
    def __init__(self, code, new=False, **kwargs):
        '''Constructor is initialized with a directory wich contains data and 
        settings file called 'daq.xml'. If *new* is true - new experiment with a
        standard parameters is created.'''
        self._dir = os.path.join(DQSROOTDIR, 'expdata', code)
        if new:
            self._daystart = kwargs['daystart'] if kwargs.has_key('daystart') \
                else params.default.experiment.daystart
            self._morning = kwargs['morning'] if kwargs.has_key('morning') \
                else params.default.experiment.morning
            self._evening = kwargs['evening'] if kwargs.has_key('evening') \
                else params.default.experiment.evening
            self._create()
        else:
            self._load()
    
    def _load(self):
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

    def _create(self):
        xx = lx.parseFile(os.path.join('..','templates','emptyExperiment.xml'))
        ch = xx.xpathEval('/experiment')[0]
        ch.setProp('nrats', str(self.nrats))
        ch.setProp('datestart', str(int(time.time())))
        ch = xx.xpathEval('/experiment/comment')[0]
        ch.setContent(self.comment)
        ch = xx.xpathEval('/experiment/rats/rat')[0]
        ch.setProp('datestart', str(int(time.time())))
        ch = xx.xpathEval('/experiment/rats')[0]
        for i in range(2,self.nrats+1):
            el = ch.newChild(None, rat, None)
            el.setProp('id', str(i))
            el.setProp('datestart', str(int(time.time())))
        
        ch = xx.xpathEval('/experiment/timesettings')[0]
        ch.setProp('daystart', self.daystart)
        ch.setProp('morning', self.morning)
        ch.setProp('evening', self.evening)
        # write to file at last        
        f = open(os.path.join(self._dir, 'daq.xml'), 'w')
        f.write(str(xx))
        f.close()
        
    
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

class NewExperimentPage(Page):
    
    def __init__(self):
        super(NewExperimentPage, self).__init__('../templates/one_experiment.xml')
    
    def index(self):
        self._tmpl.reset()
        self._tmpl.sub('code', 'enter code')
        self._tmpl.sub('comment', 'enter experiment name')
        self._tmpl.sub('daystart', params.default.experiment.daystart)
        self._tmpl.sub('morning', params.default.experiment.morning)
        self._tmpl.sub('evening', params.default.experiment.evening)
        self._tmpl.sub('nrats', '2')
        return self._tmpl.string
    
    index.exposed = True
        
        


def actor_create_experiment(code, nrats, comment, daystart=None, morning=None, evening=None):
    x = Experiment(code, new=True, nrats, daystart, comment, morning, evening)