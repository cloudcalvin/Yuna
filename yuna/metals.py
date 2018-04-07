import numpy as np
import pyclipper

from yuna import utils
from collections import namedtuple

from pygmsh.opencascade.surface_base import SurfaceBase
from pygmsh.opencascade.volume_base import VolumeBase
from pygmsh.built_in.volume import Volume

from .terminal import Terminal
from .utils import um


class Metal(object):
    """
    .v 0 -s 0.0 -l 137E-9
    """

    _ID = 0

    def __init__(self, poly, pen_depth=137e-9):
        self.id = '.v {} -s {} -l {}'.format(Metal._ID,
                                             0.0,
                                             pen_depth)
        Metal._ID += 1

        self.width = poly.data.width * um
        self.position = poly.data.position * um

        assert type(self.width) == float
        assert type(self.position) == float

        self.points = poly.get_points(self.position)

        if poly.holes:
            self.hole_points = poly.get_holes(self.position)
        else:
            self.hole_points = None

        self.surface = None
        self.volume = None

    def set_surface(self, geom):

        if self.hole_points is None:
            print('     .no holes detected')
            gp = geom.add_polygon(self.points, lcar=0.1, make_surface=True)
        else:
            print('     .holes detected')
            hole = geom.add_polygon(self.hole_points,
                                    lcar=0.1,
                                    make_surface=False)

            gp = geom.add_polygon(self.points,
                                  lcar=0.1,
                                  holes=[hole.line_loop],
                                  make_surface=True)

        self.surface = gp.surface

    def extrude(self, geom, surface=False):
        ex = geom.extrude(self.surface, [0, 0, self.width])

        if surface:
            geom.add_physical_surface(self.surface, self.id)

        self.volume = geom.add_physical_volume(ex[1], self.id)
