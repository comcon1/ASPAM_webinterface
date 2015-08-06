#!/usr/bin/python

import cherrypy
import os.path
from config import *

from index import IndexPage
root = IndexPage()
from expreview import ExperimentReview
root.expreview = ExperimentReview()

print __file__

curconf = os.path.join(DQSROOTDIR, 'server.conf')

if __name__ == '__main__':
    cherrypy.quickstart(root, config=curconf)
