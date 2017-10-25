from __future__ import print_function
from termcolor import colored


import gdspy


class Params:
    """

    """

    def __init__(self):
        """ """

        self.jj_area = 0.0
        self.res_area = 0.0
        
    def calculate_area(self, Elements, Layers):
        if self.does_contain_junctions(Elements):
            self.junction_area(Elements)
            self.resistance_area(Layers)
        
    def does_contain_junctions(self, Elements):
        """ Check if the layout contains any Junctions. """
        
        hasjj = False
        for element in Elements:
            if isinstance(element, gdspy.CellReference):
                name = element.ref_cell.name
                if name[:2] == 'JJ':
                    hasjj = True
                    
        return hasjj
        
    def junction_area(self, Elements):
        print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
        print('Junction areas:')
        for element in Elements:
            if isinstance(element, gdspy.CellReference):
                name = element.ref_cell.name
                if name[:2] == 'JJ':
                    for key, value in element.area(True).items():
                        if key[0] == 6:
                            print('      ' + name + ' --> ' + str(value * 1e-12) + 'um')
                            self.jj_area = value * 1e-12
                            

    def resistance_area(self, Layers):
        """
            * We have to get the center of each resistance polygon.
            * Test if the center of each polygon is inside
              layer 9. If so, then remove that polygon. 
            * Finally, we should be left with just the 
              resistance branch polygon.
        """
        
        print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
        print('Parasitic resistance areas:')
        
        for key, value in Layers.items():
            if value['type'] == 'resistance':
                for poly in value['jj']:
                    poly_element = gdspy.Polygon(poly, 21)
                    value = poly_element.area(True).values()[0]
                    print('      ' + key + ' --> ' + str(value * 1e-12) + 'um')
                    self.res_area = value * 1e-12

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        