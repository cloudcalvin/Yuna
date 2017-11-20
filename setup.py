"""
    First version of Yuna
"""


from __future__ import print_function
from __future__ import absolute_import

import os
from setuptools import setup, find_packages
from termcolor import colored


version = '0.0.2'


setup(
    name="yuna",
    version=version,
    author="Ruben van Staden",
    author_email="rubenvanstaden@gmail.com",
    description="Processes the layers from a GDS file.",
    setup_requires=['setuptools-markdown'],
    long_description_markdown_filename='README.md',
    license="BSD",
    keywords="yuna",
    url="https://github.com/rubenvanstaden/yuna",
    packages=['yuna', 'tests'],
    package_dir={'yuna': 'yuna'},
    install_requires=['gdspy', 'pyclipper', 'setuptools', 'numpy', 'matplotlib', 'docopt', 'future', 'termcolor'],
    entry_points={
        'console_scripts': [
            'yuna = yuna:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
