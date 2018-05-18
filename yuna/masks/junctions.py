from yuna import utils
from yuna import grid
from yuna import lvs

from shapely.geometry import Polygon
from .mask_base import MaskBase


class Junction(MaskBase):

    def __init__(self, gds, poly):
        super(Junction, self).__init__((gds, 3), poly, 20.0)

        self.datatype = 3

        # process = {**pdk.layers['ix'],
        #            **pdk.layers['res'],
        #            **pdk.layers['ntron'],
        #            **pdk.layers['jj'],
        #            **pdk.layers['via']}
        #
        # self.properties = process[gds]