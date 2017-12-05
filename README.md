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
`docopt` Library for user arguments in the terminal.

* Make sure Python is installed on your system:

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

* Install the necessary C++ compilers:

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

* Install TKinter which is needed by Matplotlib:

## Fedora

```
sudo dnf install tkinter
```

## Ubuntu

```
sudo apt-get install python-tk
```

* Next install the dependencies for Yuna:

```
sudo pip install -r requirements.txt
```

* Then install Yuna on your system:

```
sudo python setup.py install
```

# Installing Yuna from PIP

In order to use *import yuna*, we have to install the package **locally**,
with:

```
sudo pip install .
```

We can also install the package in development mode with a symlink, so that
changes to the source files will be immediately available to other users of the
package on your system.

```
sudo pip install -e .
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

# GIT Tips

To disregard small changes use:

```
git checkout .
```

# Mac OS

To get the Tkinter UI working in Mac, add the following file in `~/.matplotlib`:
https://stackoverflow.com/questions/21784641/installation-issue-with-matplotlib-python

# About setup.py

python setup.py install is used to install (typically third party) packages that you're not going to be developing/editing/debugging yourself.

For your own stuff, you want to get your package installed and then be able to frequently edit your code and not have to re-install your package—this is exactly what python setup.py develop does: installs the package (typically just a source folder) in a way that allows you to conveniently edit your code after its installed to the (virtual) environment and have the changes take effect immediately.

Note that it is highly recommended to use pip install . (install) and pip install -e . (developer install) to install packages, as invoking setup.py directly will do the wrong things for many dependencies like pulling prereleases and incompatible packages versions and make the package hard to uninstall with pip.
