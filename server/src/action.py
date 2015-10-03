# -*- coding: utf-8 -*-

from config import *
from servutils import Page

class Action(Page):
    
    def __init__(self):
        self._actdict = {}
        super(IndexPage, self).__init__('../templates/redirect_page.xml')

    def registerActor(self, actor_function):
        if not (hasattr(actor_function, '__call__')):
            raise AttributeError('*actor_function* parameter should be of function or functor type!')
        self._actor = actor_function
    
    def index(self, action, after_action, **kwargs):
        self._tmpl.reset()
        self._tmpl.sub('action', action)
        self._tmpl.sub('redirect', after_action)        
        try:
            actfun = self._actdict[action]
        except Exception as e:
            print 'Invalid action was requested!'
            return errorPage(e)
        try:
            ret = actfun(kwargs)
        except Exception as e:
            print 'Error in action was found!'
            return errorPage(e)
        
        self._tmpl.sub('response', ret)
        return self._tmpl.string
