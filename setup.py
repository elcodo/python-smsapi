#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='python-smsapi',
    version='0.2',
    license='LICENSE.txt',
    description='Client library for SMSAPI.pl API.',
    long_description=open('README.txt').read(),
    author='ELCODO',
    author_email='info@elcodo.pl',
    url='https://github.com/elcodo/python-smsapi',
    py_modules=['smsapi', ],
    keywords=['api', 'smsapi.pl', 'sms'],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
