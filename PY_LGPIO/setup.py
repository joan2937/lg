#!/usr/bin/env python

"""
setup.py file for SWIG lgpio
"""

import os
from pathlib import Path
from textwrap import dedent

from setuptools import setup, Extension
from setuptools.command.build_py import build_py as _build_py

class build_py(_build_py):
    # The package's module lgpio.py is produced by SWIG, hence build_ext must
    # run prior to the build_py command
    def run(self):
        self.run_command('build_ext')
        return super().run()

if int(os.environ.get('PYPI', '0')):
    # If building for PyPI, build a statically linked module that incorporates
    # the liblgpio library
    Path('MANIFEST.in').write_text(dedent("""\
        include lgpio_extra.py
        include src/lg*.h
        include src/rgpiod.h
        """))
    lgpio_module = Extension(
        '_lgpio',
        sources=[str(p) for p in Path('src').glob('lg*.c')] +
                ['lgpio.i', 'src/rgpiod.c'],
        libraries=['rt', 'dl'],
        include_dirs=['src'],
        extra_compile_args=['-O3', '-pthread'],
    )
else:
    # Otherwise, build a dynamically linked module
    Path('MANIFEST.in').write_text(dedent("""\
        include lgpio_extra.py
        include src/lgpio.h
        """))
    lgpio_module = Extension(
        '_lgpio',
        sources=['lgpio.i'],
        libraries=['lgpio'],
        include_dirs=['src'],
    )

setup (name = 'lgpio',
       version = '0.2.2.0',
       zip_safe=False,
       author='joan',
       author_email='joan@abyz.me.uk',
       maintainer='joan',
       maintainer_email='joan@abyz.me.uk',
       url='http://abyz.me.uk/lg/py_lgpio.html',
       description='Linux SBC GPIO module',
       long_description=Path('README.md').read_text(),
       long_description_content_type="text/markdown",
       download_url='http://abyz.me.uk/lg/lg.zip',
       license='unlicense.org',
       keywords=['linux', 'sbc', 'gpio',],
       classifiers=[
         "Programming Language :: Python :: 3",
       ],
       ext_modules=[lgpio_module],
       py_modules=["lgpio"],
       cmdclass={'build_py': build_py},
       )

