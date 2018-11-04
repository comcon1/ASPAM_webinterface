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

We use _numpy_, _matplotlib_, _pickle_.  
Also we use _textreader_ repository as a sumodule. It helps in fast opening 
large text files.

# Licensing

ASPAM\_webinterface is *not* the part of ASPAM project. 
It is released independently under BSD "3-clause" license.

