from yuna import utils
from yuna import grid
from yuna import lvs

from shapely.geometry import Polygon

from .mask_base import MaskBase


class Via(MaskBase):

    def __init__(self, gds, poly):
        super(Via, self).__init__((gds, 1), poly)

        self.clip = False
        self.datatype = 1

    def add(self, mask):
        self.points = utils.angusj(self.points, mask.points, 'difference')
        self.clip = True
