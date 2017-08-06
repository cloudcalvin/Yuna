# yuna

In order to use *import yuna*, we have to install the package **locally**,
with:

```
pip install .
```

We can also install the package in development mode with a symlink, so that
changes to the source files will be immediately available to other users of the
package on your system.

```
pip install -e .
```

## Puslishing to PyPI

The *setup.py* script is our main entrypoint to register the package name op
PyPI and upload source distrinutions.

## Packaging

**Distutils** is still the standard tool for packaging in Python, but lacks
features.

**Setuptools** was developed to overcome *distutils'* limitations and is
included in the setup.py file using *import setuptools*.

## Dependencies

To install graph-tool:

```
sudo apt-get build-dep python3-graph-tool
```

then download the source code, run the *autogen.sh* and then to configure for Python 3:

```
./configure PYTHON=python3
```
