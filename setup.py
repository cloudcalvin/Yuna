"""
    First version of Yuna
"""


from __future__ import print_function
import os
from setuptools import setup, find_packages
from termcolor import colored


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
    # entry_points={
        # 'console_scripts': [
            # 'yuna = yuna.__main__:main'
        # ]
    # },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
