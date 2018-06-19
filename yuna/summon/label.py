from yuna import utils
import yuna.labels as labels
from yuna.masternode import *

import gdspy


# class __Element__(object):

#     def __init__(self):
#         pass

#     def __add__(self, other):
#         pass


class CheckCell(object):
    """

    """

    def __init__(self, prefix, datatype):
        self.prefix = prefix
        self.datatype = datatype
        self.pins = {}

    # def __get__(self):
    #     pass

    # def __set__(self):
    #     pass

    def pin_position(self, geom, cell, stack):
        cell.flatten(single_datatype=1)

        # for element in cell.elements:
        #     if isinstance(element, gdspy.PolygonSet):
        #         if element.layers[0] == jjs[cell.name]['gds']:
        #             jj_poly = utils.angusj(element.polygons, element.polygons, 'union')

        #             if isinstance(jj_poly[0][0], list):
        #                 poly = gdspy.Polygon(jj_poly[0], element.layers[0], verbose=False)
        #             else:
        #                 poly = gdspy.Polygon(jj_poly, element.layers[0], verbose=False)

        element = cell
        name = cell.name

        bb = element.get_bounding_box()
        cx = ( (bb[0][0] + bb[1][0]) / 2.0 ) + 10.0
        cy = ( (bb[0][1] + bb[1][1]) / 2.0 )

        self.register_component(geom, cell, name, (cx, cy))

        # self.pins[name] = (cx, cy)

    def register_component(self, geom, cell, name, position):

        def _add_meta_class(cell, position, key, data, ltype):
            params = {}
            params['params'] = data

            MNode = type(ltype, (MasterNode,), params)

            pinlabel = MNode(text=key, position=position)

            cell.add(pinlabel.get_label())

        for key, data in geom.raw_pdk_data['Cells']['Vias'].items():
            if key != 'color' and key == name:
                _add_meta_class(cell, position, key, data, 'Via')

    def minimum_spacing(self):
        pass

    def maximum_spacing(self):
        pass

    def minimum_size(self):
        pass


# class MaskCell(gdspy.Cell):

#     def __init__(self, geom, cell, ltype=None, datatype=0):
#         print('--- flattening ' + cell.name)

#         self.geom = geom
#         self.cell = cell
#         self.type = ltype
#         self.datatype = datatype

#         self.elements = []

#     def add_labels(self):
#         # element = kwargs['element']
#         # name = kwargs['name']

#         self.cell.flatten(single_datatype=1)

#         bb = element.get_bounding_box()
#         cx = ( (bb[0][0] + bb[1][0]) / 2.0 ) + 10.0
#         cy = ( (bb[0][1] + bb[1][1]) / 2.0 )

#         lbl = gdspy.Label(name, (cx, cy), 0, layer=64)
#         cell.add(lbl)

#     def fields(self):
#         for subcell in cell.get_dependencies(True):
#             if subcell.name.split('_')[0] == 'via':
#                 labels.cell.vias(subcell, geom)


def cells(geom, cell):
    """
    Label each individual cell before flattening them
    to the top-level cell.

    Vias are primary components and are detected first.
    JJs and nTrons are defined as secondary components.

    Returns
    -------
    out : gdspy Cell
        The flattened version of original cell with labeled components
    """

    if len(cell.elements) == 0:
        utils.print_cellrefs(cell)

    for subcell in cell.get_dependencies(True):
        if subcell.name.split('_')[0] == 'via':
            labels.cell.vias(subcell, geom)

    for subcell in cell.get_dependencies(True):
        if subcell.name.split('_')[0] == 'ntron':
            labels.cell.ntrons(subcell, geom)

    for subcell in cell.get_dependencies(True):
        if subcell.name.split('_')[0] == 'jj':
            labels.cell.junctions(subcell, geom)


def devices(geom, cell_labels):
    """
    Place the labels to their corresponding positions
    after flattening the top-level cell. Update the
    datafield object to include all labels in the layout.
    """

    import yuna.masternodes as mn

    utils.green_print('Place labels in flattened layout')

    def _add_meta_class(self, lbl, key, layer, name):
        params = {}
        params['params'] = layer

        MNode = type(name, (MasterNode,), params)

        mm = MNode(text=key, position=lbl.position)

        geom.labels.append(mm)

    for lbl in cell_labels:
        comp = lbl.text.split('_')[0]

        if comp == 'via':
            print('Flatterning Via labels...')
            for key, layer in geom.raw_pdk_data['Cells']['Vias'].items():
                if key != 'color' and key == lbl.text:
                    _add_meta_class(geom, lbl, key, layer, 'Via')

        if comp == 'ntron':
            print('Flatterning Via labels...')
            for key, layer in geom.raw_pdk_data['Cells']['Ntrons'].items():
                if key != 'color' and key == lbl.text:
                    _add_meta_class(geom, lbl, key, layer, 'Ntron')

        # if comp == 'jj':
        #     params = self.raw_pdk_data['Cells']['Junctions']
        #     params['text'] = lbl.text
        #
        #     jj = mn.junction.Junction(lbl.position, params)
        #     self.labels.append(jj)
        #
        # if comp == 'shunt':
        #     params = self.raw_pdk_data['Cells']['Ntrons']
        #     params['text'] = lbl.text
        #
        #     shunt = mn.junction.Shunt(lbl.position, params)
        #     self.labels.append(shunt)
        #
        # if comp == 'ground':
        #     params = self.raw_pdk_data['Cells']['Ntrons']
        #     params['text'] = lbl.text
        #
        #     ground = mn.junction.Ground(lbl.position, params)
        #     self.labels.append(ground)