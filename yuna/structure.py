import gdsyuna
import yuna
import numpy as np

from yuna import tools


class DataField(gdsyuna.Cell):

    def __init__(self, name):
        self.name = name
        self.polygons = []
        self.labels = []

    # def get_polygons(self):
    #     polygons = {}
    #     for poly in self.polygons:
    #         key = (poly.layer, poly.datatype)
    #         if key in polygons:
    #             polygons[key].append(np.array(poly.points))
    #         else:
    #             polygons[key] = [np.array(poly.points)]
    #     return polygons

    def get_polygons(self):
        polygons = {}
        for poly in self.polygons:
            key = (poly.layer, poly.datatype)
            pp = tools.convert_node_to_3d([poly.points], 0)
            if key in polygons:
                polygons[key].append(pp)
            else:
                polygons[key] = [pp]
        return polygons

    def add(self, element):
        """
        Add a new element or list of elements to this cell.

        Parameters
        ----------
        element : object
            The element or list of elements to be inserted in this cell.

        Returns
        -------
        out : ``Cell``
            This cell.
        """

        print('--------' + str(type(element)))
        if isinstance(element, yuna.structure.Label):
            self.labels.append(element)
        else:
            self.polygons.append(element)

        return self

    def parse_gdspy(self, cell):

        for poly in self.polygons:
            polygon = gdsyuna.Polygon(*poly.get_variables())
            cell.add(polygon)

        for lbl in self.labels:
            label = gdsyuna.Label(*lbl.get_variables())
            cell.add(label)


class Polygon(gdsyuna.Polygon):
    _ID = 0

    def __init__(self, points, layer, datatype):
        super(Polygon, self).__init__(points, layer, datatype, verbose=False)

        self.id = 'p{}'.format(Polygon._ID)
        Polygon._ID += 1

    def get_variables(self):
        return (self.points, self.layer, self.datatype)


class Label(gdsyuna.Label):
    _ID = 0

    def __init__(self, ttype, metals, text, position, rotation, layer):
        super(Label, self).__init__(text, position, rotation=rotation, layer=layer)

        self.id = 'l{}'.format(Label._ID)
        self.type = ttype
        self.metals = metals

    def get_variables(self):
        return (self.text, self.position, self.rotation, self.layer)
