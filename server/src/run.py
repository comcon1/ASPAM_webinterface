#!/usr/bin/python

import cherrypy

class IndexPage:
    def index(self):
        return '''
        Hellow, guy!
        '''
    index.exposed = True


root = IndexPage()

print __file__

import os.path
curconf = os.path.join(os.path.dirname(__file__), \
                '../../testsuite/testserver/server.conf')

if __name__ == '__main__':
    cherrypy.quickstart(root, config=curconf)
