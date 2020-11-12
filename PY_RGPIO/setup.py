#!/usr/bin/env python

from distutils.core import setup

setup(name='rgpio',
      version='0.0.0.0',
      author='joan',
      author_email='joan@abyz.me.uk',
      maintainer='joan',
      maintainer_email='joan@abyz.me.uk',
      url='http://abyz.me.uk/rpi/lg/python.html',
      description='Linux SBC GPIO module',
      long_description='Linux SBC Python module to access the lg daemon',
      download_url='http://abyz.me.uk/lg/lg.zip',
      license='unlicense.org',
      py_modules=['rgpio'],
      keywords=['linux', 'sbc', 'gpio',],
      classifiers=[
         "Programming Language :: Python :: 2",
         "Programming Language :: Python :: 3",
      ]
     )

