from __future__ import print_function
from termcolor import colored
from utils import tools


class Wire:
    """
    """

    def __init__(self, Layers, vias):
        """  """
        self.Layers = Layers
        self.vias = vias['Subatom']

    def union_wire_layers(self, subatom):
        print('Implement UNION wires.')
        layer = self.Layers[subatom]['result']

    def find_union_diff(self, subatom):
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







