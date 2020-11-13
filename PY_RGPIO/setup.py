#!/usr/bin/env python

from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='rgpio',
      version='0.0.3.0',
      zip_safe=False,
      author='joan',
      author_email='joan@abyz.me.uk',
      maintainer='joan',
      maintainer_email='joan@abyz.me.uk',
      url='http://abyz.me.uk/lg/py_rgpio.html',
      description='Linux SBC GPIO module',
      long_description=long_description,
      long_description_content_type="text/markdown",
      download_url='http://abyz.me.uk/lg/lg.zip',
      license='unlicense.org',
      py_modules=['rgpio'],
      keywords=['linux', 'sbc', 'gpio',],
      classifiers=[
         "Programming Language :: Python :: 2",
         "Programming Language :: Python :: 3",
      ]
     )

