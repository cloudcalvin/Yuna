import itertools
import json
import gdspy

from yuna import utils

import collections as cl


"""
Hacker: 1h3d*n
For: Volundr
Docs: Algorithm 1
Date: 31 April 2017

Description: Using Angusj Clippers library to do
             polygon manipulations.

1) The union is done on each polygon of the wiring layer.
2) The difference and intersection is done with the
union result and the moat layer.
3) Note, you might have to multiple each coordinate with
1000 to convert small floats 0.25 to integers, 250.
"""


class ProcessDesignKit(object):

    def __init__(self):
        self.layers = None
        self.cells = None

    def __add__(self):
        pass


class CellProperties(list):
    """

    """

    def __init__(self):
        pass

    def __getitem__(self, name):
        print('\nRetrieve CellProperties:')
        for i in self:
            if i.name == name:
                print('  {}'.format(i))

    def __setitem__(self, key, value):
        print('Updating CellProperties', (key, value))
        self.append(value)

    def __contains__(self, atom):
        if issubclass(atom, AtomBase):
            pass


class LayerProperties(list):
    """

    """

    def __init__(self):
        pass

    def __getitem__(self, gds):
        print('\nRetrieve LayerProperties:')
        for i in self:
            if i.gds == gds:
                print('  {}'.format(i))

    def __setitem__(self, key, value):
        print('Updating LayerProperties', (key, value))
        self.append(value)

    def __contains__(self, atom):
        if issubclass(atom, LayerBase):
            pass
