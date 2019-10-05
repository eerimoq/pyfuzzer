#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages
import re


def find_version():
    return re.search(r"^__version__ = '(.*)'$",
                     open('pyfuzzer/version.py', 'r').read(),
                     re.MULTILINE).group(1)


setup(name='pyfuzzer',
      version=find_version(),
      description='Fuzz test Python modules with libFuzzer.',
      long_description=open('README.rst', 'r').read(),
      author='Erik Moqvist',
      author_email='erik.moqvist@gmail.com',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
      ],
      keywords=['fuzz', 'fuzzying', 'test'],
      url='https://github.com/eerimoq/pyfuzzer',
      packages=find_packages(exclude=['tests']),
      test_suite="tests",
      include_package_data=True,
      entry_points = {
          'console_scripts': ['pyfuzzer=pyfuzzer.__init__:main']
      })
