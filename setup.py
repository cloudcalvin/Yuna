"""
    First version of Yuna
"""


import os
from setuptools import setup, find_packages


# preserve format, this is read from __init__.py
version = '0.0.1'


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
    install_requires=['gdspy', 'pyclipper'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
