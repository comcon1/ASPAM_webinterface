#!/usr/bin/python

import cherrypy
import cherrypy.lib.auth_digest
import os.path
from config import *
from functools import partial

from dqcontrol import DQController

dqc = DQController()

from index import IndexPage
root = IndexPage(dqc)
from expreview import ExperimentReview
root.expreview = ExperimentReview()
from ratstat import RatStatistics
root.ratstat = RatStatistics()
from timestat import TimeStatistics
root.timestat = TimeStatistics()

# controller pages
import experiment, servutils
root.control = servutils.Page(None) # do not load it!
root.control.newexperiment = experiment.NewExperimentPage()

# forming factory of server-side interfaces
import action
actfactory = action.Action()
actfactory.registerActor('create_experiment', experiment.actor_create_experiment)
actfactory.registerActor('chstate_experiment', partial(experiment.actor_changestate_experiment, dqc))


# binding registered actors
root.action = actfactory

print __file__


curconf = os.path.join(DQSROOTDIR, 'server.conf')
cherrypy.config.update(curconf)

get_ha1 = cherrypy.lib.auth_digest.get_ha1_file_htdigest(\
	os.path.join(DQSROOTDIR, 'htdigest') )

print get_ha1

if __name__ == '__main__':
    root_app = cherrypy.tree.mount(root, "/", curconf)
    root_app.config['/']['tools.auth_digest.get_ha1'] = get_ha1
    cherrypy.engine.subscribe( 'stop', partial(experiment.actor_finish_active_experiment, dqc) )
    cherrypy.engine.start()
    cherrypy.engine.block() 
