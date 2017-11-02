from __future__ import print_function
from termcolor import colored
from utils import tools

class Via:
    """
    """

    def __init__(self, config):
        """
        """

        self.config = config

    def get_angusj_polygon(self, poly):
        """  """

        Layers = self.config['Layers']

        polyclass = poly.keys()[0]
        polylayer = poly.values()[0]

        subjclip = None
        if polyclass == 'Layer':
            subjclip = Layers[polylayer]['result']
        elif polyclass == 'Module':
            print('Implement Module support.')

        return subjclip

    def get_layercross(self, value):
        """ Intersect the layers in the 'clip' object
        in the submodule. """

        tools.magenta_print('Connect layers with VIA')
        subj = self.get_angusj_polygon(value['wire_1'])
        clip = self.get_angusj_polygon(value['wire_2'])

        layercross = []
        if subj and clip:
            layercross = tools.angusj(clip, subj, 'intersection')
            if not layercross:
                print('Clipping is zero.')

        return layercross

    def get_viacross(self, value, subj):
        """  """

        tools.magenta_print('Save Via Polygons:')
        clip = self.get_angusj_polygon(value['via_layer'])

        result_list = []
        viacross = []
        for poly in subj:
            result_list = tools.angusj([poly], clip, "intersection")
            if result_list:
                viacross.append(poly)

        return viacross





