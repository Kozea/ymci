#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ymci - Your Modern Continous Integration server
# Copyright © 2014 Florian Mounier, Kozea

import os
import re

from setuptools import setup
ROOT = os.path.dirname(__file__)

with open(os.path.join(ROOT, 'ymci', '__init__.py'), encoding='utf-8') as fd:
    __version__ = re.search("__version__ = '([^']+)'", fd.read()).group(1)

setup(
    name="ymci",
    version=__version__,
    description="Your Modern Continous Integration server",
    author="Florian Mounier, Kozea",
    author_email="florian.mounier@kozea.fr",
    platforms="Linux",
    scripts=['ymci.py'],
    packages=['ymci'],
    provides=['ymci'],
    install_requires=['tornado', 'tornado_systemd', 'pyyaml', 'wtforms',
                      'sqlalchemy', 'psycopg2', 'wtforms_alchemy', 'pygal',
                      'pbkdf2', 'pygments', 'simplepam'],
    tests_require=["pytest"],
    package_data={'ymci': ['static/*', 'templates/*']},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Build Tools"])
