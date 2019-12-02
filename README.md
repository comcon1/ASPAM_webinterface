# Webinterface for ASPAM project

The project contains Web interface submodule for ASPAM
(https://github.com/comcon1/ASPAM) or related applications.

This repository contains four main logical parts:

*  *libdaq* - **LIB**rary for **D**ata **AQ**uisition

This library is used by Web-interface to separate day and night run.

* *libDQimage* - **LIB**rary for **D**ata a**Q**uision **IMAGE** drawing

* *server* - Server containing Web-interface for work with ASPAM.

* *testsuite* - testing libraries including *artificial rat*. 

# Dependencies

**Attention!** ASPAM project works with Python2.

We use _numpy_, _matplotlib_, _pickle_.  
Also we use _textreader_ repository as a sumodule. It helps in fast opening 
large text files.

# Installing

To run server with testing configuration, please create `testsuite/testserver/parameters.conf` on the base of `testsuite/testserver/parameters.conf.example`, and do the same thing for `testsuite/testserver/server.conf`. To run server with normal configuration, copy the folder `testsuite/testserver` somewhere and point this path defining DQSROOTDIR in `server/src/config.py` file.

# Licensing

ASPAM\_webinterface is *not* the part of ASPAM project. 
It is released independently under BSD "3-clause" license.

