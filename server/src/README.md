Here are the sources of the server-side scripts. Two of them are of a greate
importance:

* `config.py` --- main configuration script. You must specify path to your
server files and experiment folders in the head of its code.

* `run.py` --- the main program that starts WSGI server. Should be started at the
computer connected to the device.

* `image_loader.py` --- program generating images at the side of the server. 
WSGI process should have rights for executing it.

The rest files are used in formation of HTML pages, operating data aquisition
script etc.
