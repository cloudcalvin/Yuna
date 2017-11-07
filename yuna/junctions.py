from __future__ import print_function
from collections import defaultdict
from pprint import pprint
from utils import tools

import gdspy
import layers
import pyclipper


def transpose_cell(gdsii, Layers, refname, element):
    """ 
    The cells are centered in the middle of the gds
    file canvas. To include this cell into the main
    cell, we have to transpose it to the required position.

    Save tranposed coordinates in 'Layers' object.
    Maybe we should automate this later by making
    'result' a {} and not a [].
    """

    tools.green_print('Detecting ' + refname)
    cellpolygons = gdsii.extract(refname).get_polygons(True)

    layers = {}
    for key, polygons in cellpolygons.items():
        for layername, layerdata in Layers.items():
            if layerdata['gds'] == key[0]:
                save_transposed_coords(layers, polygons, layername, element)

    return layers


def save_transposed_coords(layers, polygons, layername, element):
    """ Transpose each layer in the Junction reference
    and save it by layername in a dict. """

    poly_list = []

    for poly in polygons:
        for coord in poly:
            coord[0] = coord[0] + element.origin[0]
            coord[1] = coord[1] + element.origin[1]

        poly_list.append(poly.tolist())

    layers[layername] = poly_list


def clipping(subj, clip, operation):
    """ Intersect the layers in the 'clip' object
    in the submodule. """

    layercross = []
    if subj and clip:
        if operation == 'intersection':
            layercross = tools.angusj(clip, subj, 'intersection')
        elif operation == 'difference':
            layercross = tools.angusj(clip, subj, 'difference')

    return layercross


Beweeg die na layers.py
def filter_base(baselayer, jjlayer):
    """ If the junction object has more than 
    one M0 polygon, then we have to find the 
    one with the JJ layer inside it. """

    subj = jjlayer
    clip = baselayer

    baselayer = None
    for poly in clip:
        if layers.does_layers_intersect([poly], subj):
            baselayer = poly

    return baselayer


def junction_inside_res(Layers, jj, res_layer):
    """ Filter the res inside the junction
    cell object with a JJ layer inside it. """

    name = layers.get_junction_layer(Layers)
    jj_layer = jj[name]

    if layers.does_layers_intersect([res_layer], jj_layer):
        return True
    else:
        return False


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
    
    def __init__(self, basedir, gdsii, Layers):
        self.basedir = basedir
        self.gdsii = gdsii
        self.Layers = Layers

        self.shunt_value = None
        self.area_value = None

        self.layers = {}
        self.edges = []
        self.base = []
        self.res = []

    def set_layers(self, layers):
        self.layers = layers

    def detect_jj(self, atom):
        """ The 'JJ' key means that we have to
        access the corresponding layer from
        the Junction Object List. """

        tools.magenta_print('Calculating junctions json:')

        for subatom in atom['Subatom']:
            tools.read_module(self.basedir, atom, subatom)

            base = subatom['Module']['base']['layer']
            res = subatom['Module']['res']['layer']

            self.base = self.base_with_jj_inside(base)
            self.res = self.res_connected_to_base(jj_base, res)

    def base_with_jj_inside(self, basename):
        """ Get the base layer (M0) polygon in the Junction
        objects that has a JJ layer inside them. """

        name = layers.get_junction_layer(self.Layers)

        baselayer = self.layers[basename]
        jjlayer = self.layers[name]

        return filter_base(baselayer, jjlayer)

    def res_connected_to_base(self, jj_base, res):
        """ Get the shunt resistance branch
        in the junction CellRefence. """

        name = layers.get_res_layer(self.Layers)
        reslayer = self.layers[name]

        all_reslayers = []
        for poly in reslayer:
            if not junction_inside_res(self.Layers, self.layers, poly):
                all_reslayers.append(poly)

        return clipping(all_reslayers, [jj_base], 'difference')        

    def calculate_shunt_value(self):
        pass

    def calculate_area_value(self):
        pass





