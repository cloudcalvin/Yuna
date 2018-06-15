from yuna import utils
from yuna import grid
from yuna import lvs

from shapely.geometry import Polygon
from .mask_base import MaskBase


class Ntron(MaskBase):
    """
    Represents the polygons of a specific gds layer that
    belongs to cells of the class via.

    Parameters
    ----------
    gds : integer
        Gds number of the layer.
    poly : array-like[N][2]
        List of polygons that contains the vertex coordinates.

    Arguments
    ---------
    datatype : integer
        The integer number that represents a via polygon.
    polygons : list
        List of the PolyBase objects that represents the
        polygons of the layers linked with their properties.
    """

    def __init__(self, gds, poly):
        self.datatype = 7
        self.smoothness = 100.0
        key = (gds, self.datatype)
        super(Ntron, self).__init__(key, poly, self.smoothness)

        self.polygons = []

    def add_polygon(self, geom):
        """
        Link the polygon coordinates and the given properties.
        Then save them into a list of PolyBase objects.
        """

        from yuna.lvs.poly_base import PolyBase

        for pp in self.points:
            assert isinstance(pp[0], list)

            data = geom.raw_pdk_data['Layers']

            layers = [*data['ix']]

            for params in layers:
                if params['layer'] == self.key[0]:
                    params['datatype'] = self.key[1]
                    polygon = PolyBase(pp, params)
                    self.polygons.append(polygon)
