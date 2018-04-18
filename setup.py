from __future__ import print_function
from __future__ import absolute_import

from termcolor import colored
from pprint import pprint
from setuptools import setup, find_packages

from yuna import __version__

# setup_requires = []
# if 'build_sphinx' in sys.argv:
#     setup_requires.extend(['sphinx', 'sphinx_rtd_theme'])

setup(
    name="yuna",
    version=__version__,
    author="Ruben van Staden",
    author_email="rubenvanstaden@gmail.com",
    description="Processes the layers from a GDS file.",
    # setup_requires=setup_requires,
    long_description_markdown_filename='README.md',
    license="BSD",
    keywords="yuna",
    url="https://github.com/rubenvanstaden/yuna",
    packages=['yuna'],
    package_dir={'yuna': 'yuna'},
    install_requires=[
        'gdspy',
        'pyclipper',
        'setuptools',
        'numpy',
        'matplotlib',
        'docopt',
        'future',
        'termcolor'
    ],
    entry_points={
        'console_scripts': [
            'yuna = yuna:grand_summon'
        ]
    }
)
