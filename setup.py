#!/usr/bin/python3.6

# from __future__ import print_function
# from __future__ import absolute_import

from pprint import pprint
from setuptools import setup, find_packages

from yuna import __version__


setup(
    name="yuna",
    version=__version__,
    author="Ruben van Staden",
    author_email="rubenvanstaden@gmail.com",
    description="Processes the layers from a GDS file.",
    long_description_markdown_filename='README.md',
    license="MIT",
    keywords="yuna",
    url="https://github.com/rubenvanstaden/yuna",
    packages=['yuna', 
              'yuna.lvs', 
              'yuna.labels', 
              'yuna.pdk', 
              'yuna.technology', 
              'yuna.masks', 
              'yuna.masternodes'],
    package_dir={'yuna': 'yuna'},
    install_requires=[
        'gdspy',
        'shapely',
        'pygmsh',
        'pyclipper',
        'setuptools',
        'numpy',
        'matplotlib',
        'docopt',
        'future',
        'pytest'
    ],
    entry_points={
        'console_scripts': [
            'yuna = yuna:grand_summon'
        ]
    }
)
