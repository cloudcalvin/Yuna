# Yuna

Compiling Yuna from source is done as follow:

First clone the git repo:

```
git clone https://rubenvanstaden@bitbucket.org/coldflux/yuna.git
```

# Dependencies

Yuna package descriptions:

`pyclipper` Python wrapper for Angusj Clipper library.
`termcolor` Package for color outputs in the terminal.
`gdspy` Python library for GDS file handeling.

Make sure Python is installed on your system:

## Fedora

```
sudo dnf install python2-devel
sudo dnf install python3-devel
```

## CentOS

```
sudo yum install python-devel
```

## Ubuntu

```
sudo apt-get install python-dev
sudo apt-get install python3-dev
```

Install the necessary C++ compilers:

## Fedora

```
sudo dnf install gcc-c++
```

## CentOS

```
sudo yum install gcc-c++
```

## Ubuntu

```
sudo apt-get update
sudo apt-get install --reinstall build-essential
```

Install TKinter which is needed by Matplotlib:

```
sudo dnf install tkinter
```

Next install the dependencies for Yuna:

```
sudo pip install -r requirements.txt
```

Then install Yuna on your system:

```
sudo python setup.py install
```

# Installing Yuna from PyPy

In order to use *import yuna*, we have to install the package **locally**,
with:

```
pip3 install .
```

We can also install the package in development mode with a symlink, so that
changes to the source files will be immediately available to other users of the
package on your system.

```
pip3 install -e .
```

## Publishing to PyPI

The *setup.py* script is our main entry-point to register the package name op
PyPI and upload source distributions.

## Packaging

**Distutils** is still the standard tool for packaging in Python, but lacks
features.

**Setuptools** was developed to overcome *distutils'* limitations and is
included in the setup.py file using *import setuptools*.

# Debugging tools

Install iPython for debugging:

```
sudo dnf install ipython
```
