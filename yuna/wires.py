from __future__ import print_function
from termcolor import colored
from utils import tools


import json


class Wire:
    """
    """

    def __init__(self, Layers, Subatom, vias):
        """  """
        self.Layers = Layers
        self.Subatom = Subatom
        self.vias = vias['Subatom']

    def union_polygons(self, Layers):
        """ Union the normal wiring polygons. """

        tools.green_print('Union Layer:')
        for key, layer in Layers.items():
            tools.union_wire(Layers, key, 'result')

    def find_via_diff(self, subatom):
        """ Connect vias and wires by finding 
        their difference and not letting the overlap. """

        subj = self.Layers[subatom]['result']

        all_vias_list = []
        for via in self.vias:
            for poly in via['result']:
                all_vias_list.append(poly)

        viadiff = []
        clip = all_vias_list
        if subj and clip:
            viadiff = tools.angusj(clip, subj, 'difference')
            if not viadiff:
                print('Clipping is zero.')

        return viadiff







