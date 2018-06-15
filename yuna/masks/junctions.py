from yuna import utils
from yuna import grid
from yuna import lvs

from shapely.geometry import Polygon
from yuna.lvs.poly_base import PolyBase
from .mask_base import MaskBase


class Junction(MaskBase):

    def __init__(self, gds, poly):
        super(Junction, self).__init__((gds, 3), poly, 20.0)

        self.datatype = 3
        self.polygons = []

    def add_polygon(self, geom):
        for pp in self.points:
            assert isinstance(pp[0], list)

            data = geom.raw_pdk_data['Layers']

            layers = [*data['ix'], *data['res'], *data['jj']]

            for params in layers:
                if params['layer'] == self.key[0]:
                    params['datatype'] = self.key[1]
                    polygon = PolyBase(pp, params)
                    self.polygons.append(polygon)
