from __future__ import print_function # lace this in setup.
from termcolor import colored

import json
import gdspy
import yuna.utils.tools as tools


"""
    Hacker: 1h3d*n
    For: Volundr
    Docs: Algorithm 1
    Date: 31 April 2017

    Description: Using Angusj Clippers library to do
                 polygon manipulations.

    1) The union is done on each polygon of the wiring layer.
    2) The difference and intersection is done with the
    union result and the moat layer.
    3) Note, you might have to multiple each coordinate with
    1000 to convert small floats 0.25 to integers, 250.

    --> union = or
    --> difference = not
    --> intersection = and
"""


gdsii = gdspy.GdsLibrary()


def is_layer_active(Layers, atom):
    all_layers = True
    for layer in atom['check']:
        if Layers[layer]['active'] == 'False':
            all_layers = False
    return all_layers


def make_active(Layers, layer):
    """
        This function changes the 'active' state of
        the layer in the 'Layers' object in the
        config.json file.
    """

    if layer in Layers:
        Layers[layer]['active'] = True


def transpose_cell(Layers, cellpolygons, origin, name):
    """
        The cells are centered in the middle of the gds 
        file canvas. To include this cell into the main 
        cell, we have to transpose it to the required position.
    """
    
    for key, polygons in cellpolygons.items():
        for layer, lay_data in Layers.items():
            if lay_data['gds'] == key[0]:
                for poly in polygons:
                    for coord in poly:
                        coord[0] = coord[0] + origin[0]
                        coord[1] = coord[1] + origin[1]

                    # Save tranposed coordinates in 'Layers' object.
                    # Maybe we should automate this later by making
                    # 'result' a {} and not a [].
                    # print(type(polygons))
                    if (layer == 'JJ'):
                        lay_data['result'].append(poly.tolist())
                    elif (layer == 'JP') or (layer == 'JC'):
                        lay_data['result'].append(poly.tolist())
                    else:
                        lay_data['jj'].append(poly)


def polygon_result(Layers, element):
    """ Add the polygon to the 'result' key in the 'Layers' object """

    for layer, lay_data in Layers.items():
        if lay_data['gds'] == element.layer:
            Layers[layer]['result'].append(element.points.tolist())


def polygon_jj(Layers, element):
    """ Add the polygon to the 'jj' key in the 'Layers' object. """

    # print ('\n' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    # print('Add junction: ')
    name = element.ref_cell.name
    if name[:2] == 'JJ':
        Layers['JJ']['name'].append(name)
        cellpolygons = gdsii.extract(name).get_polygons(True)
        transpose_cell(Layers, cellpolygons, element.origin, name)
        # print('    Name: ' + name)


def union_polygons(Layers):
    # Change this by making layers active.
    Layers['RES']['active'] = True
    
    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('Union Layer:')
    for layer, lay_data in Layers.items():
        if json.loads(lay_data['union']):
            tools.union_wire(Layers, layer, 'result')

        # if (layer == 'JJ') or (layer == 'JP') or (layer == 'JC'):
        #     tools.union_wire(Layers, layer, 'result')
        # elif (layer != 'RES'):
        #     tools.union_wire(Layers, layer, 'result')
        #     # Make sure we can actually do this.
        #     # tools.union_wire(Layers, layer, 'jj')


def does_contain_junctions(Elements):
    """ Check if the layout contains any Junctions. """
    
    hasjj = False
    
    for element in Elements:
        if isinstance(element, gdspy.CellReference):
            name = element.ref_cell.name
            if name[:2] == 'JJ':
                hasjj = True

    return hasjj


def junction_area(Elements):
    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('Junction areas:')
    for element in Elements:
        if isinstance(element, gdspy.CellReference):
            name = element.ref_cell.name
            if name[:2] == 'JJ':
                for key, value in element.area(True).items():
                    if key[0] == 6:
                        print('      ' + name + ' --> ' + str(value * 1e-12) + 'um')


def resistance_area(Layers):
    """
        * We have to get the center of each resistance polygon.
        * Test if the center of each polygon is inside
          layer 9. If so, then remove that polygon. 
        * Finally, we should be left with just the 
          resistance branch polygon.
    """
    
    # NB: We have to save the JJ name with the corresponding area value.
    
    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('Parasitic resistance areas:')
    for poly in Layers['RES']['jj']:
        poly_element = gdspy.Polygon(poly, 21)
        value = poly_element.area(True).values()[0]
        print('      RES' + ' --> ' + str(value * 1e-12) + 'um')


def add_elements(Layers, Elements):
    """ 
        Add the elements read from GDSPY to the 
        corresponding Layers in the JSON object.
    """
    
    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('Elements:')
    for element in Elements:
        if isinstance(element, gdspy.Polygon):
            print('      Polygons: ', end='')
            print(element)
            polygon_result(Layers, element)
        elif isinstance(element, gdspy.CellReference):
            print('      CellReference: ', end='')
            print(element)
            polygon_jj(Layers, element)


class Process:
    """
        Variables
        ---------
            origin : dict
                This dict contains all the original layers as read in
                from the import GDS file, before manipulation.
            uPoly : dict
                Union of polygon layers, like m1 that has been union, m1 and m2
                that has been intersected, etc.
            iPoly : dict
                Intersection result of two or more polygons.
    """

    def __init__(self, gds_file, config_data):
        self.gds_file = gds_file
        self.config_data = config_data

    def config_layers(self, cellref):
        """
            This function is process specific.
            It looks at each layer and dicides
            what to do with it, for example:

            * If it's a wiring layer, union it.
            * If it's a via then test which wiring
              layers is connect and union them.

            Notes
            -----

                * By default all individual layers should
                  be union.

            Todo
            ----

                Implement the default layer union of other
                layers, not just the wiring layers.
        """

        self.init_layers(cellref)

        Elements = gdsii.top_level()[0].elements
        Layers = self.config_data['Layers']
        Atom = self.config_data['Atom']

        print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
        print('Running Atom:')
        for atom in Atom:
            if is_layer_active(Layers, atom):
                self.calculate_atom(atom)

        if does_contain_junctions(Elements):
            junction_area(Elements)
            resistance_area(Layers)

        return self.config_data

    def init_layers(self, cellref):
        """
            Fills the 'result' and 'jj' lists inside each
            layer in 'Layers' object.

            Todo
            ----

                * Add PolygonPaths
                * Add nTrons
        """

        gdsii.read_gds(self.gds_file, unit=1.0e-12)
        
        Elements = gdsii.top_level()[0].elements
        Layers = self.config_data['Layers']
        
        if cellref:
            gdsii.extract(cellref)
        else:
            top_cell = gdsii.top_level()[0]
            gdsii.extract(top_cell)
        
        # gdspy.LayoutViewer()
        add_elements(Layers, Elements)
        union_polygons(Layers)

    def calculate_atom(self, atom):
        print('      Num: ' + atom['id'])
        for subatom in atom['Subatom']:
            if not json.loads(atom['skip']):
                self.calculate_sub_atom(atom, subatom)

    def calculate_sub_atom(self, atom, subatom):
        """
            1. Calculate the Subject polygon list.
            2. Calculate the Clippers polygon list.
            3. Clip and 1. and 2. using the proposed
               method and save the result.
        """

        print('        Subatom: ' + str(subatom['id']))
        if subatom['method'] == 'offset':
            self.execute_offset(atom, subatom)
        elif subatom['method'] == 'intersection':
            if subatom['type'] == 'boolean':
                self.execute_bool(atom, subatom)
            else:
                self.execute_method(atom, subatom)
        elif subatom['method'] == 'difference':
            self.execute_method(atom, subatom)
        elif subatom['method'] == 'union':
            self.execute_method(atom, subatom)
        else:
            raise Exception('Please specify a valid Clippers method')

    def save_intersected_poly(self, atom, subatom, res_list):
        Layers = self.config_data['Layers']
        layer = subatom['savein']['layer']
        poly = subatom['savein']['poly']
        Layers[layer][poly] = res_list

    def update_layer(self, atom, subatom, result):
        """ Saves the result back into the global Layers dict. """

        Layers = self.config_data['Layers']
        layer = subatom['savein']['layer']
        poly = subatom['savein']['poly']

        if subatom['type'] == 'result':
            subatom['result'] = result
        else:
            Layers[layer][poly] = result

    def subject(self, atom, subatom):
        """
            Parameters
            ----------

                subj_layer : The layer in use.

                subj_class : Can only be "Layers" or "Atom".

                subj_poly : For now it can either be "jj" or "result".
        """

        Layers = self.config_data['Layers']
        subj_class = subatom['subj']['class']
        subj_layer = subatom['subj']['layer']
        subj_poly = subatom['subj']['poly']

        if subj_class == 'Layers':
            subj = Layers[subj_layer][subj_poly]
        return subj

    def clipper(self, atom, subatom):
        """
            Parameters
            ----------

                clip_layer : The layer in use.

                clip_class : Can only be "Layers" or "Atom".

                clip_poly : For now it can either be "jj" or "result".

            Note
            ----
            
                * Subatom classes must be in Clip Object.
        """

        Layers = self.config_data['Layers']
        clip_class = subatom['clip']['class']
        clip_layer = subatom['clip']['layer']
        clip_poly = subatom['clip']['poly']

        if clip_class == 'Layers':
            clip = Layers[clip_layer][clip_poly]
        elif clip_class == 'Atom':
            clip = atom[clip_layer]['result']
        elif clip_class == 'Subatom':
            subatom_num = subatom['clip']['layer']
            clip = atom['Subatom'][subatom_num]['result']
            
        return clip
        
    def execute_offset(self, atom, subatom):
        """ """
        
        result_list = []
        subj = self.subject(atom, subatom)

        if subj:
            result_list = tools.angusj_offset(subj)
            if result_list:
                self.update_layer(atom, subatom, result_list)
                
    def execute_method(self, atom, subatom):
        """ """

        subj = self.subject(atom, subatom)
        clip = self.clipper(atom, subatom)

        result_list = []
        if subj and clip:
            result_list = tools.angusj(clip, subj, subatom['method'])
            if result_list:
                self.update_layer(atom, subatom, result_list)
            else:
                atom['skip'] = 'true'
        else:
            atom['skip'] = 'true'
            
    def execute_bool(self, atom, subatom):
        """ """
        
        subj = self.subject(atom, subatom)
        clip = self.clipper(atom, subatom)
        
        result_list = []
        inter_list = []
        for poly in clip:
            result_list = tools.angusj([poly], subj, subatom['method'])
            if subatom['delete'] == 'True':
                if not result_list:
                    inter_list.append(poly)
            else:
                if result_list:
                    inter_list.append(poly)

        self.save_intersected_poly(atom, subatom, inter_list)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
