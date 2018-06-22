import numpy as np
import itertools

from yuna import utils

from yuna.utils import logging
# from yuna.utils import datatype
from yuna.utils import nm

from yuna.pdk.properties import PolygonProperties


logger = logging.getLogger(__name__)


class PolyBase(PolygonProperties):
    """
    Holes can only be a list of points, since it is only a hole
    and has no other properties.
    """

    _ID = 0

    def __init__(self, points, params, id0=None):
        super(PolyBase, self).__init__(points, **params)

        # TODO: Implement the hole detection.
        self.holes = None

        if id0 is None:
            self.id = 'polybase_{}'.format(PolyBase._ID)
            PolyBase._ID += 1
        else:
            self.id = id0

    # def __str__(self):
    #     prop = '(gds-{}, datatype-{}, name-{}, width-{}, metals-{})'.format(
    #         self.layer, self.datatype, self.name, self.width, self.metals)

    #     return 'Layer Properties {}'.format(prop)

    def __properties__(self):
        return ['name', 'rank', 'stack', 'width', 'color']

    def get_holes(self, z):
        if self.holes is not None:
            return [[float(p[0]*nm), float(p[1]*nm), z] for p in self.holes]
        return None

    # def __getattr__(self, name):
    #     if name == 'points':
    #         print('ewfbewuifbewjewfbejwfwefjbefkjwebfjkwebfjkwebfkwjefbwefjkbwefkb')
    #         # return [[float(p[0]*nm), float(p[1]*nm), z] for p in self.points]
    #     else:
    #         raise AttributeError("No such attribute: " + name)

    def get_points(self, z):
        return [[float(p[0]*nm), float(p[1]*nm), z] for p in self.points]

    def get_variables(self):
        return (self.points, self.layer, self.datatype)

    # def get_var1(self):
    # #     key = (self.layer, self.datatype)
    #     return (self.points, self.layer, self.datatype, self.kwargs)
