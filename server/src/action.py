# -*- coding: utf-8 -*-

from config import *
from servutils import Page

class Action(Page):
    
    def __init__(self):
        self._actdict = {}
        super(Action, self).__init__('../templates/redirect_page.xml')

    def registerActor(self, actor_alias, actor_function):
        if not (hasattr(actor_function, '__call__')):
            raise AttributeError('*actor_function* parameter should be of function or functor type!')
        self._actdict[actor_alias] = actor_function
    
    def index(self, action, after_action, **kwargs):
        self._tmpl.reset()
        self._tmpl.sub('action', action)
        self._tmpl.sub('redirect', after_action)        
        try:
            actfun = self._actdict[action]
        except Exception as e:
            print 'Invalid action was requested!'
            return self.errorPage(e)
        try:
            ret = actfun(**kwargs)
        except Exception as e:
            print 'Error in action was found!'
            return self.errorPage(e)
        
        self._tmpl.sub('response', ret)
        return self._tmpl.string
    
    index.exposed = True
    
    def __del__(self):
        if self._actdict.has_key('finish-00'):
            print 'Running finishing listener!'
            fun = self._actdict['finish-00']            
            fun()
