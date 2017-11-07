from __future__ import print_function
from collections import defaultdict
from pprint import pprint
from utils import tools


import gdspy
import layers
import pyclipper


def clipping(subj, clip, operation):
    """ Intersect the layers in the 'clip' object
    in the submodule. """

    layercross = []
    if subj and clip:
        if operation == 'intersection':
            layercross = tools.angusj(clip, subj, 'intersection')
        elif operation == 'difference':
            layercross = tools.angusj(clip, subj, 'difference')

        if not layercross:
            print('Clipping is zero.')

    return layercross


class JunctionObjects:
    """ This class contains a list of all the
    junction objects inside the gds layout. """
    
    def __init__(self, basedir, gdsii, Layers):
        self.jjs = []
        self.jj_layers = {}
        self.basedir = basedir
        self.gdsii = gdsii
        self.Layers = Layers

    def filter_base(self, baselayer, jjlayer):
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

    def base_with_jj_inside(self, basename):
        """ Get the base layer (M0) polygon in the Junction
        objects that has a JJ layer inside them. """

        all_baselayers = []
        for jj in self.jjs:
            name = layers.get_junction_layer(self.Layers)
            baselayer = jj[basename]
            jjlayer = jj[name]

            jj_base = self.filter_base(baselayer, jjlayer)
            all_baselayers.append(jj_base)

        return all_baselayers

    def junction_inside_res(self, jj, res_layer):
        """ Filter the res inside the junction
        cell object with a JJ layer inside it. """

        name = layers.get_junction_layer(self.Layers)
        jj_layer = jj[name]

        print(res_layer)

        if layers.does_layers_intersect([res_layer], jj_layer):
            return True
        else:
            return False

    def junction_res(self, jj_base, res):
        """ Get the shunt resistance branch
        in the junction cell ref. """

        all_reslayers = []
        for jj in self.jjs:
            name = layers.get_res_layer(self.Layers)
            reslayer = jj[name]

            for poly in reslayer:
                if not self.junction_inside_res(jj, poly):
                    all_reslayers.append(poly)

        shunt = clipping(all_reslayers, jj_base, 'difference')        
        return shunt

    def calculate_jj(self, Elements, atom):
        """ The 'JJ' key means that we have to
        access the corresponding layer from
        the Junction Object List. """

        tools.magenta_print('Calculating junctions json:')
        self.fill_junction_list(Elements)

        for subatom in atom['Subatom']:
            tools.read_module(self.basedir, atom, subatom)

            base = subatom['Module']['base']['layer']
            res = subatom['Module']['res']['layer'] 

            jj_base = self.base_with_jj_inside(base)
            jj_res = self.junction_res(jj_base, res)

            subatom['Module']['base']['result'] = jj_base
            subatom['Module']['res']['result'] = jj_res

    def fill_junction_list(self, Elements):
        """ Loop over all elements, such as
        polygons, polgyonsets, cellrefences, etc
        and find the CellRefences. CellRefs
        which is a junction has to start with JJ. """

        for element in Elements:
            if isinstance(element, gdspy.CellReference):
                print('      CellReference: ', end='')
                print(element)

                refname = element.ref_cell.name
                if refname[:2] == 'JJ':
                    jj = Junction(self.Layers, element, refname)
                    jj.transpose_cell(self.gdsii)
                    self.jjs.append(jj.original_layers)


class Junction:
    """  """

    def __init__(self, Layers, element, name):
        """  """

        self.Layers = Layers
        self.element = element
        self.name = name
        self.original_layers = {}

    def save_transposed_coords(self, polygons, layername):
        """ Transpose each layer in the Junction reference
        and save it by layername in a dict. """

        poly_list = []
        for poly in polygons:
            for coord in poly:
                coord[0] = coord[0] + self.element.origin[0]
                coord[1] = coord[1] + self.element.origin[1]

            poly_list.append(poly.tolist())

        self.original_layers[layername] = poly_list

    def transpose_cell(self, gdsii):
        """ 
        The cells are centered in the middle of the gds
        file canvas. To include this cell into the main
        cell, we have to transpose it to the required position.

        Save tranposed coordinates in 'Layers' object.
        Maybe we should automate this later by making
        'result' a {} and not a [].
        """

        tools.green_print('Detecting ' + self.name)
        cellpolygons = gdsii.extract(self.name).get_polygons(True)

        for key, polygons in cellpolygons.items():
            for layername, layerdata in self.Layers.items():
                if layerdata['gds'] == key[0]:
                    self.save_transposed_coords(polygons, layername)









