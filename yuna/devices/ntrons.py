from yuna import utils
from yuna import grid
from yuna import lvs

from shapely.geometry import Polygon
from .mask_base import MaskBase


class Ntron(MaskBase):

    def __init__(self, gds, poly):
        super(Ntron, self).__init__((gds, 7), poly)

        self.datatype = 7

        # process = {**pdk.layers['ix'],
        #            **pdk.layers['res'],
        #            **pdk.layers['ntron'],
        #            **pdk.layers['jj'],
        #            **pdk.layers['via']}
        #
        # self.properties = process[gds]
