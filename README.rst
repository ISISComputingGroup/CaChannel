CaChannel - EPICS Channel Access in Python
==========================================

CaChannel is a Python interface to Channel Access. 
It was orginally developed by Geoff Savage usign `caPython extension <http://d0server1.fnal.gov/users/savage/www/caPython/caPython.html>`_

This CaChannel implementation uses PythonCA extension by `Noboru Yamamoto <http://www-acc.kek.jp/EPICS_Gr/products.html>`_.


Installation
------------
EPICS base 3.14.12.4 headers and static libraries are packed under ``epicsbase`` 
for OS X (Intel 32/64 bit), Linux (Intel 32/64 bit) and Windows (Intel 32/64 bit).

Use pip::

    $ [sudo] pip install cachannel

Or build from source, by which you need to have an appropriate compiler for your platform.
::

    $ hg clone https://bitbucket.org/xwang/cachannel
    $ python setup.py build
    $ [sudo] python setup.py install

Or build for Anaconda,
::
    
    $ hg clone http://bitbucket.org/xwang/cachannel
    $ cd conda
    $ conda build .

Documentation
-------------
Hosted at `Read the Docs <http://cachannel.readthedocs.org>`_