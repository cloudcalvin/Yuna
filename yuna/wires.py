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
            if json.loads(layer['union']):
                tools.union_wire(Layers, key, 'result')

#     def union_wire_layers(self, subatom):
#         print('Implement UNION wires.')
#         layer = self.Layers[subatom]['result']

#     def find_wire_diff(self, subatom):
#         """ Do not let layering wires overlap,
#         by getting their polygon difference. """
# 
#         subj_id = self.Layers[subatom]['id']
#         subj = self.Layers[subatom]['result']
# 
#         all_wires_list = []
#         for sub in self.Subatom:
#             layer_id = self.Layers[sub]['id']
#             layer = self.Layers[sub]['result']
#             if layer_id != subj_id:
#                 for poly in layer:
#                     all_wires_list.append(poly)
# 
#         wirediff = []
#         clip = all_wires_list
#         if subj and clip:
# #             wirediff = tools.angusj(clip, subj, 'union')
#             wirediff = tools.angusj(clip, subj, 'difference')
#             if not wirediff:
#                 print('Clipping is zero.')
# 
#         return wirediff
 
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







