#!/usr/bin/env python
"""
Setup file for Ca-Python using distutils package.
Python2.6 or later should be used.
"""

import filecmp
import os
import sys
import platform
import shutil
import subprocess
import warnings

# Use setuptools to include build_sphinx, upload/sphinx commands
try:
    from setuptools import setup, Extension
except:
    from distutils.core import setup, Extension
    
import epicscorelibs.path
import epicscorelibs.config
import swig
os.environ["PATH"] += os.pathsep + swig.BIN_DIR

# python 2/3 compatible way to load module from file
def load_module(name, location):
    if sys.hexversion < 0x03050000:
        import imp
        module = imp.load_source(name, location)
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, location)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module

# check wether all paths exist
def paths_exist(paths):
    for path in paths:
        if not os.path.exists(path):
            return False
    return True

build_ca_ext=True
# define EPICS base path and host arch
EPICSBASE = epicscorelibs.path.base_path
HOSTARCH = epicscorelibs.config.get_config_var("EPICS_HOST_ARCH")
SHARED = epicscorelibs.config.get_config_var("EPICS_SHARED")


def create_exension():
    global EPICSBASE, HOSTARCH, SHARED
    umacros = []
    macros = []
    cflags = []
    lflags = []
    dlls = []
    extra_objects = []
    libraries = ["ca", "Com"]
    CMPL = 'gcc'
    UNAME = platform.system()
    ARCH = platform.architecture()[0]
    DEBUG = True if 'debug' in HOSTARCH else False
    # platform dependent libraries and macros
    if UNAME.lower() == "windows":
        UNAME = "WIN32"
        static = False
        if HOSTARCH in ['win32-x86', 'windows-x64', 'win32-x86-debug', 'windows-x64-debug']:
            if not SHARED:
                dlls = ['Com.dll', 'ca.dll']
                for dll in dlls:
                    dllpath = os.path.join(epicscorelibs.path.lib_path, dll)
                    if not os.path.exists(dllpath):
                        static = True
                        break
                    dll_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'CaChannel', dll)
                    if not os.path.exists(dll_filepath) or not filecmp.cmp(dllpath, dll_filepath):
                        shutil.copy(dllpath, dll_filepath)
            macros += [('_CRT_SECURE_NO_WARNINGS', 'None'), ('EPICS_CALL_DLL', ''), ('EPICS_BUILD_DLL', ''), ('USE_TYPED_RSET', '')]
            if DEBUG:
                cflags += ['/MDd', '/Od', '/RTCsu']
            cflags += ['/Od', '/RTCsu'] # use for release debugging
            cflags += ['/GR', '/Z7', '/Oy-']
            lflags += ['/DEBUG', '/LTCG:OFF']
            CMPL = 'msvc'
        if HOSTARCH in ['win32-x86-static', 'windows-x64-static'] or static:
            libraries += ['ws2_32', 'user32', 'advapi32']
            macros += [('_CRT_SECURE_NO_WARNINGS', 'None'), ('EPICS_DLL_NO', '')]
            umacros += ['_DLL']
            cflags += ['/EHsc', '/Z7']
            lflags += ['/LTCG', '/DEBUG']
            if DEBUG:
                libraries += ['msvcrtd']
                lflags += ['/NODEFAULTLIB:libcmtd.lib']
            else:
                libraries += ['msvcrt']
                lflags += ['/NODEFAULTLIB:libcmt.lib']
            CMPL = 'msvc'
        # GCC compiler
        if HOSTARCH in ['win32-x86-mingw', 'windows-x64-mingw']:
            macros += [('_MINGW', ''), ('EPICS_DLL_NO', '')]
            lflags += ['-static']
            CMPL = 'gcc'
        if HOSTARCH == 'windows-x64-mingw':
            macros += [('MS_WIN64', '')]
            CMPL = 'gcc'
    elif UNAME.lower() == "darwin":
        CMPL = 'clang'
        if not SHARED:
            extra_objects = [os.path.join(epicscorelibs.path.lib_path, 'lib%s.a' % lib) for lib in libraries]
            if paths_exist(extra_objects):
                libraries = []
            else:
                extra_objects = []
                SHARED= True
    elif UNAME.lower() == "linux":
        CMPL = 'gcc'
        if not SHARED:
            extra_objects = [os.path.join(epicscorelibs.path.lib_path, 'lib%s.a' % lib) for lib in libraries]
            if paths_exist(extra_objects):
                libraries = ['rt']
                if subprocess.call('nm %s | grep -q rl_' % os.path.join(epicscorelibs.path.lib_path, 'libCom.a'), shell=True) == 0:
                    libraries += ['readline']
            else:
                extra_objects = []
                SHARED = True
    else:
        print("Platform", UNAME, ARCH, " Not Supported")
        sys.exit(1)

    include_dirs = [epicscorelibs.path.include_path]

    ca_module = Extension('CaChannel._ca',
                          sources=['src/CaChannel/_ca.cpp'],
                          extra_compile_args=cflags,
                          include_dirs=include_dirs,
                          define_macros=macros,
                          undef_macros=umacros,
                          extra_link_args=lflags,
                          extra_objects=extra_objects,
                          libraries=libraries,
                          library_dirs=[epicscorelibs.path.lib_path])

    if UNAME == "Linux" and SHARED:
        ca_module.runtime_library_dirs = [epicscorelibs.path.lib_path]

    return [ca_module], dlls

_version = load_module('_version', 'src/CaChannel/_version.py')

if build_ca_ext:
    ext_module, package_data = create_exension()
    requirements = []
    if sys.hexversion < 0x03040000:
        requirements += ['enum34']
else:
    ext_module = []
    package_data = []
    requirements = ['caffi']
    

requirements += ["epicscorelibs", "swig"]    


setup(name="CaChannel",
      version=_version.__version__,
      author="Xiaoqiang Wang",
      author_email="xiaoqiang.wang@psi.ch",
      description="CaChannel Interface to EPICS",
      long_description=open('README.rst').read(),
      url="http://pypi.python.org/pypi/cachannel",
      license="BSD",
      platforms=["Windows", "Linux", "Mac OS X"],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Programming Language :: C',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: BSD License',
          'Topic :: Scientific/Engineering',
      ],
      packages=["CaChannel"],
      package_dir={"": "src", "CaChannel": "src/CaChannel"},
      py_modules=["ca", "epicsPV", "epicsMotor"],
      ext_modules=ext_module,
      package_data={'CaChannel': package_data},
      install_requires=requirements
      )
