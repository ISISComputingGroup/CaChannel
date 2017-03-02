#!/usr/bin/env python

import os
import platform
import socket
import sys
import time
import re
import runpy
import subprocess
import doctest
import unittest

class TestCa(unittest.TestCase):
    def setUp(self):
        try:
            UNAME=platform.uname()[0]
            ARCH=platform.architecture()[0]
        except:
            UNAME="Unknown"
            ARCH="Unknown"

        if UNAME.lower() == "windows":
            if ARCH=="64bit":
                HOSTARCH="windows-x64"
            else:
                HOSTARCH="win32-x86"
        elif UNAME.lower() == "darwin":
            HOSTARCH = 'darwin-x86'
        elif UNAME.lower() == "linux":
            if ARCH=="64bit":
                HOSTARCH="linux-x86_64"
            else:
                HOSTARCH="linux-x86"
        else:
            raise RuntimeError("Platform % is not supported"%UNAME)

        EPICS_BIN = os.path.join(os.environ['PREFIX'], 'epics', 'bin', HOSTARCH)
        EPICS_DBD = os.path.join(os.environ['PREFIX'], 'epics', 'dbd')

        environ = os.environ.copy()
        environ['PATH'] += os.pathsep + EPICS_BIN

        self.softIoc = subprocess.Popen(['softIoc', '-D', os.path.join(EPICS_DBD, 'softIoc.dbd'), '-d', 'tests/test.db'],
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                env = environ
        )
        time.sleep(2)

    def test_ca(self):
        try:
            if platform.system() != 'Linux':
                runpy.run_path('tests/ca_test.py', run_name='__main__')
        except SystemExit as e:
            ecode = e.code
        else:
            ecode = 0
        self.assertEqual(ecode, 0)

    def test_CaChannel(self):
        test = doctest.DocTestSuite('CaChannel.CaChannel')
        runner = unittest.TextTestRunner()
        runner.run(test)

    def tearDown(self):
        self.softIoc.stdin.write('exit\n')
        time.sleep(2)

if __name__ == '__main__':
    unittest.main()
