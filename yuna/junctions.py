from __future__ import print_function
from __future__ import absolute_import

from collections import defaultdict
from pprint import pprint
from yuna.utils import tools

import gdspy
import yuna.layers as layers
import pyclipper


def filter_multiple_jj_polygons(clip, subj):
    """ If the junction object has more than
    one M0 polygon, then we have to find the
    one with the JJ layer inside it. """

    baselayer = None
    for poly in clip:
        if layers.does_layers_intersect([poly], subj):
            baselayer = poly

    return baselayer


def transpose_cell(gdsii, Layers, element):
    """
    The cells are centered in the middle of the gds
    file canvas. To include this cell into the main
    cell, we have to transpose it to the required position.

    Save tranposed coordinates in 'Layers' object.
    Maybe we should automate this later by making
    'result' a {} and not a [].
    """

    refname = element.ref_cell.name
    tools.green_print('Detecting ' + refname)
    cell = gdsii.extract(refname)
    cellpolygons = cell.get_polygons(True)

    layers = {}
    for key, polygons in cellpolygons.items():
        for layername, layerdata in Layers.items():
            if layerdata['gds'] == key[0]:
                layers[layername] = save_transposed_coords(polygons, element)

    return layers


def save_transposed_coords(polygons, element):
    """ Transpose each layer in the Junction reference
    and save it by layername in a dict. """

    poly_list = []
    for poly in polygons:
        for coord in poly:
            coord[0] = coord[0] + element.origin[0]
            coord[1] = coord[1] + element.origin[1]

        poly_list.append(poly.tolist())

    return poly_list


def clipping(subj, clip, operation):
    """ Intersect the layers in the 'clip' 
    object in the submodule. """

    layercross = []
    if subj and clip:
        if operation == 'intersection':
            layercross = tools.angusj(clip, subj, 'intersection')
        elif operation == 'difference':
            layercross = tools.angusj(clip, subj, 'difference')

    return layercross


def is_jj_cell(element):
    """  """

    jjbool = False
    
    if isinstance(element, gdspy.CellReference):
        print('      CellReference: ', end='')
        print(element)
        refname = element.ref_cell.name
        if refname[:2] == 'JJ':
            jjbool = True

    return jjbool


def fill_jj_list(config, basedir, jjs):
    """ Loop over all elements, such as
    polygons, polgyonsets, cellrefences, etc
    and find the CellRefences. CellRefs
    which is a junction has to start with JJ. """
    
    atom = config.Atom['jjs']

    jj_id = 0
    for element in config.Elements:
        if is_jj_cell(element):
            layers = transpose_cell(config.gdsii, config.Layers, element)

            jj = Junction(basedir, jj_id, config.Layers)
            jj.set_layers(layers)
            jj.detect_jj(atom)
            jjs.append(jj)
            jj_id += 1
            
            
def update_wire_object(wire, i, _id):
    """ V1 labeled edge is connected to Via 1.
    P1 is connected to Port 1. """
    
    label = 'J' + str(_id)
    wire.edgelabels.append(label)


class Junction:
    """
    This class contains a list of all the
    junction objects inside the gds layout.

    Variables
    ---------
    layers : list
        Original layers of the junction CellRefence.
    edges : list
        Edges of the wire polygons that connect
        to the 'base' of this junction.
    base : list
        The base polygon of the junction (M2, COU, etc)
        that connect the junction to the wires.
    res : list
        The shunt resistance polygon that is connected
        to the base polygon.
    *_value : double
        The shunt resistance and junction area
        value of this junction.

    Notes
    -----

    * Assume that each junction will only have one
      'base' and one 'res' layer, each.
    """

    def __init__(self, basedir, jj_id, Layers):
        self.basedir = basedir
        self.Layers = Layers

        self.shunt_value = None
        self.area_value = None

        self.id = jj_id
        self.layers = {}
        self.edges = []
        self.polygon = []
        self.res = []
        self.gds_base = 0
        self.gds_res = 0

    def set_layers(self, layers):
        self.layers = layers

    def set_gds(num):
        self.gds = num
        
    def connect_wires(self, wire):
        if wire.active and wire.polygon:
            wireoffset = tools.angusj_offset(wire.polygon, 'up')
            if layers.does_layers_intersect([self.polygon], wireoffset):
                self.connect_edges(wire)

    def connect_edges(self, wire):
        for i, polygon in enumerate(wire.polygon):
            for point in polygon:
                inside = pyclipper.PointInPolygon(point, self.polygon)

                if inside != 0:
                    self.edges.append(point)
                    update_wire_object(wire, i, self.id)

    def detect_jj(self, atom):
        """ The 'JJ' key means that we have to
        access the corresponding layer from
        the Junction Object List. """

        tools.magenta_print('Calculating junctions json:')

        for subatom in atom['Subatom']:
            tools.read_module(self.basedir, atom, subatom)

            basename = subatom['Module']['base']['layer']
            res = subatom['Module']['res']['layer']

            # TODO: Where do we use the GDS numbers?
            self.gds_base = subatom['Module']['base']['gds']
            self.gds_res = subatom['Module']['res']['gds']

            self.polygon = self.poly_with_jj_inside(basename)
            self.res = self.poly_connected_to_res(res)

    def poly_with_jj_inside(self, basename):
        """ Get the base layer (M0) polygon in the Junction
        objects that has a JJ layer inside them. """

        name = layers.get_junction_layer(self.Layers)

        baselayer = self.layers[basename]
        jjlayer = self.layers[name]

        return filter_multiple_jj_polygons(baselayer, jjlayer)

    def poly_connected_to_res(self, res):
        """ Get the shunt resistance branch
        in the junction CellRefence. """

        name = layers.get_res_layer(self.Layers)
        reslayer = self.layers[name]

        all_reslayers = []
        for poly in reslayer:
            if not layers.junction_inside_res(self.Layers, self.layers, poly):
                all_reslayers.append(poly)

        return clipping(all_reslayers, [self.polygon], 'difference')

    def calculate_shunt_value(self):
        pass

    def calculate_area_value(self):
        pass

    def plot_jj(self, cell):
        cell.add(gdspy.Polygon(self.polygon, self.gds_base))
        cell.add(gdspy.Polygon(self.res, self.gds_res))
