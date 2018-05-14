# Yuna

Yuna uses the *gdspy* package to read and manipulate the GDS layers.

## User 

Setup for the normal user.

### Dependencies

*Yuna* package descriptions:

`pyclipper` Python wrapper for Angusj Clipper library.
`termcolor` Package for color outputs in the terminal.
`gdspy` Python library for GDS file handeling.
`docopt` Library for user arguments in the terminal.

Make sure Python is installed on your system:

```
sudo dnf install python2-devel
sudo dnf install python3-devel
sudo dnf install gcc-c++
sudo dnf install tkinter
```

### Installing

You can install Yuna directly from the Python package manager *pip* using:

```
sudo pip install yuna
```

## Developers

Documentation for developers for maintaining and extending.

### Installation

To instead install Yuna from source, clone the git repository, *cd* into it, and run:

```
sudo pip install -r requirements.txt
sudo pip install .
```

We can also install the package in development mode with a symlink, so that
changes to the source files will be immediately available to other users of the
package on your system.

```
sudo pip install -e .
```

Remember to remove the build, dist and .egg directories before doing a new 
PyPi upload. To uploading package to PyPi using *twine*:

```
sudo python setup.py bdist_wheel
twine upload dist/*
```

Unit testing overview: http://docs.python-guide.org/en/latest/writing/tests/
