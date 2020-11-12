#!/usr/bin/env python

"""
setup.py file for SWIG lgpio
"""

from distutils.core import setup, Extension

lgpio_module = Extension('_lgpio', sources=['lgpio_wrap.c',], libraries=['lgpio',],)

setup (name = 'lgpio',
       version = '0.0.0.0',
       ext_modules = [lgpio_module],
       py_modules = ["lgpio"],
       )

