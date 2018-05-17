import numpy as np
import networkx as nx
import itertools
import gdspy
import pyclipper

from yuna import utils

from yuna.utils import logging
from yuna.utils import datatype
from yuna.utils import nm

logger = logging.getLogger(__name__)


class PolyBase(gdspy.Polygon):
    """
    Holes can only be a list of points, since it is only a hole
    and has no other properties.
    """

    _ID = 0

    def __init__(self, key, points, pdk, holes=None):
        super(PolyBase, self).__init__(points, *key, verbose=False)

        self.holes = holes

        if key[1] == 1:
            self.id = 'v{}'.format(PolyBase._ID)
        elif key[1] == 3:
            self.id = 'j{}'.format(PolyBase._ID)
        elif key[1] == 7:
            self.id = 'n{}'.format(PolyBase._ID)
        else:
            self.id = 'i{}'.format(PolyBase._ID)

        process = {**pdk.layers['ix'],
                   **pdk.layers['res'],
                   **pdk.layers['ntron'],
                   **pdk.layers['jj'],
                   **pdk.layers['via']}

        self.properties = process[key[0]]

        PolyBase._ID += 1

    def get_holes(self, z):
        return [[float(p[0]*nm), float(p[1]*nm), z] for p in self.holes]

    def get_points(self, z):
        return [[float(p[0]*nm), float(p[1]*nm), z] for p in self.points]

    def get_variables(self):
        return (self.points, self.layer, self.datatype)
