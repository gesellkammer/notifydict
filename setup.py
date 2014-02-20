#!/usr/bin/env python

"""
notifydict: a dictionary which will fire a callback if its changed
"""

from setuptools import setup

classifiers = """
Development Status :: 3 - Alpha
Intended Audience :: Education
Intended Audience :: Developers
Intended Audience :: Information Technology
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Text Processing :: General
"""

setup(name='notifydict',
      version='0.0.2',
      description='a dictionary which will fire a callback if its changed', 
      long_description=__doc__,
      classifiers=filter(None, classifiers.split('\n')),
      author='Robert Handke',
      author_email='robert.handke@hushmail.com',
      py_modules=['notifydict']
      #install_requires=['pandas>=0.12.0', 'requests>=1.2.3'])
)


