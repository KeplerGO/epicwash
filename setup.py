#!/usr/bin/env python
from setuptools import setup

# Command-line tools
entry_points = {'console_scripts': [
    'epicwash = epicwash.epicwash:epicwash_main',
    'epicwash-prepare = epicwash.epicwash:epicwash_prepare_main'
]}

setup(name='epicwash',
      version='1.0.0',
      description="Prevents new K2 EPIC catalogs from "
                  "containing duplicate entries.",
      author='Geert Barentsen',
      author_email='hello@geert.io',
      packages=['epicwash'],
      install_requires=['csvkit'],
      entry_points=entry_points,
      )
