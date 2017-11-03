from __future__ import print_function
from termcolor import colored
from utils import tools

class Via:
    """
    """

    def __init__(self, config, subatom):
        """
        """

        self.Layers = config['Layers']
        self.Modules = subatom['Module']

    def get_polygon(self, poly):
        """  """

        polyclass = poly.keys()[0]
        polylayer = poly.values()[0]

        subjclip = None
        if polyclass == 'Layer':
            subjclip = self.Layers[polylayer]['result']
        elif polyclass == 'Module':
            subjclip = self.Modules[polylayer]['result']

        return subjclip

    def get_layercross(self, value):
        """ Intersect the layers in the 'clip' object
        in the submodule. """

#         tools.magenta_print('Connect layers with VIA')
        subj = self.get_polygon(value['wire_1'])
        clip = self.get_polygon(value['wire_2'])

        layercross = []
        if subj and clip:
            layercross = tools.angusj(clip, subj, 'intersection')
            if not layercross:
                print('Clipping is zero.')

        return layercross

    def get_viacross(self, value, subj):
        """  """

#         tools.magenta_print('Save Via Polygons:')
        clip = self.get_polygon(value['via_layer'])

        result_list = []
        viacross = []
        for poly in subj:
            result_list = tools.angusj([poly], clip, "intersection")
            if result_list:
                viacross.append(poly)

        return viacross

    def reverse_via(self, value, subj):
        """ This method is called when we have
        to save the via as the first layer below
        it. This is needed when the crossings 
        of the two wiring layers are not equally large.
        
        Note
        ----
        Note that wire_1 must be the largest polygon.
        """

        clip = self.get_polygon(value['wire_1'])

        result_list = []
        wireconnect = []
        for poly in clip:
            result_list = tools.angusj([poly], subj, 'intersection')
            if result_list:
                wireconnect.append(poly)

        return wireconnect

    def remove_viacross(self, value):
        """  """

#         tools.magenta_print('Remove polygon with VIA inside:')
        subj = self.get_polygon(value['wire_1'])
        clip = self.get_polygon(value['via_layer'])

        result_list = []
        viacross = []
        for poly in subj:
            result_list = tools.angusj([poly], clip, "intersection")
            if not result_list:
                viacross.append(poly)

        return viacross





