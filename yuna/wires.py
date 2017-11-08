from __future__ import print_function
from termcolor import colored
from utils import tools


import gdspy


def union_polygons(Layers):
    """ Union the normal wiring polygons. """

    tools.green_print('Union Layer:')
    for key, layer in Layers.items():
        tools.union_wire(Layers, key, 'result')


class Wire:
    """
    """

    def __init__(self):
        """  """

        self.gds = 0
        self.name = ''
        self.layer = []
        self.active = False

    def set_name(self, name):
        self.name = name

    def set_gds(self, num):
        self.gds = num
            
    def set_layer(self, layer):
        self.layer = layer

    def set_active(self, active):
        self.active = active

    def update_with_via_diff(self, vias):
        """ Connect vias and wires by finding
        their difference and not letting the overlap. """

        subj = self.layer

        clip = []
        for via in vias:
            clip.append(via.base)

        if subj and clip:
            self.layer = tools.angusj(clip, subj, 'difference')

    def update_with_jj_diff(self, jjs):
        """ Find the difference between the wiring
        polygons and the junction base polygons. """

        subj = self.layer

        clip = []
        for jj in jjs:
            clip.append(jj.base)

        if subj and clip:
            self.layer = tools.angusj(clip, subj, 'difference')

    def plot_wire(self, cell):
        if self.active:
            for poly in self.layer:
                cell.add(gdspy.Polygon(poly, self.gds))

















