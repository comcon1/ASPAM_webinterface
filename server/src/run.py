#!/usr/bin/python

import cherrypy
import cherrypy.lib.auth_digest
import os.path
from config import *

from index import IndexPage
root = IndexPage()
from expreview import ExperimentReview
root.expreview = ExperimentReview()
from ratstat import RatStatistics
root.ratstat = RatStatistics()
from timestat import TimeStatistics
root.timestat = TimeStatistics()

print __file__


curconf = os.path.join(DQSROOTDIR, 'server.conf')
cherrypy.config.update(curconf)

get_ha1 = cherrypy.lib.auth_digest.get_ha1_file_htdigest(\
	os.path.join(DQSROOTDIR, 'htdigest') )

print get_ha1

if __name__ == '__main__':
    root_app = cherrypy.tree.mount(root, "/", curconf)
    root_app.config['/']['tools.auth_digest.get_ha1'] = get_ha1
    cherrypy.engine.start()
    cherrypy.engine.block() 
