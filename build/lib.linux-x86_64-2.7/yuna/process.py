# thedon
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


def transpose_cell(Layers, cellpolygons, origin):
    for key, polygons in cellpolygons.items():
        for layer, lay_data in Layers.items():
            if lay_data['gds'] == key[0]:
                for poly in polygons:
                    for coord in poly:
                        coord[0] = coord[0] + origin[0]
                        coord[1] = coord[1] + origin[1]

                    # Save tranposed coordinates in 'Layers' object.
                    if (layer == 'JJ') or (layer == 'JP') or (layer == 'JC'):
                        lay_data['result'].append(poly.tolist())
                    else:
                        lay_data['jj'].append(poly)


def polygon_result(Layers, element):
    """
        Add the polygon to the 'result' key in the 'Layers' object
    """

    for layer, lay_data in Layers.items():
        if lay_data['gds'] == element.layer:
            Layers[layer]['result'].append(element.points.tolist())


def polygon_jj(Layers, element):
    """
        Add the polygon to the 'jj' key in the 'Layers' object
    """

    name = element.ref_cell.name
    if name[:2] == 'JJ':
        print('\n---Add junction: ' + name + ' ----------')
        cellpolygons = gdsii.extract(name).get_polygons(True)
        transpose_cell(Layers, cellpolygons, element.origin)


def union_polygons(Layers):
    for layer, lay_data in Layers.items():
        if (layer == 'JJ') or (layer == 'JP') or (layer == 'JC'):
            tools.union_wire(Layers, layer, 'result')
        else:
            tools.union_wire(Layers, layer, 'jj')
            tools.union_wire(Layers, layer, 'result')


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

    def config_layers(self):
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

        self.init_layers()

        Layers = self.config_data['Layers']
        Atom = self.config_data['Atom']

        for atom in Atom:
            if is_layer_active(Layers, atom):
                print('\n---Running Atom: ' + atom['id'] + ' ----------')
                self.calculate_atom(atom)

        return self.config_data

    def init_layers(self):
        """
            Fills the 'result' and 'jj' lists inside each
            layer in 'Layers' object.

            Todo
            ----

                * Add PolygonPaths
                * Add nTrons
        """

        gdsii.read_gds(self.gds_file, unit=1.0e-12)

        print('\n---Adding components----------')
        Elements = gdsii.top_level()[0].elements
        Layers = self.config_data['Layers']

        for element in Elements:
            if isinstance(element, gdspy.Polygon):
                polygon_result(Layers, element)
            elif isinstance(element, gdspy.CellReference):
                polygon_jj(Layers, element)

        union_polygons(Layers)

    def calculate_atom(self, atom):
        for subatom in atom['Subatom']:
            if not json.loads(atom['skip']):
                print('Subatom: ' + str(subatom['id']))
                self.calculate_sub_atom(atom, subatom)

    def calculate_sub_atom(self, atom, subatom):
        """
            1. Calculate the Subject polygon list
            2. Calculate the Clippers polygon list
            3. Clip and 1. and 2. using the proposed
               method and save the result.
        """

        result_list = []

        subj = self.subject(atom, subatom)
        clip = self.clipper(atom, subatom)

        if subj and clip:
            result_list = tools.angusj(clip, subj, subatom['method'])
            if result_list:
                self.update_layer(atom, subatom, result_list)
            else:
                atom['skip'] = 'true'
        else:
            atom['skip'] = 'true'

    def update_layer(self, atom, subatom, result):
        """
            Saves the result back into the global Layers dict.
        """

        Layers = self.config_data['Layers']
        layer = subatom['savein']['layer']
        poly = subatom['savein']['poly']

        if subatom['type'] == 'result':
            subatom['result'] = result
        elif subatom['type'] == 'boolean':
            # Save the previous subatom's result
            sublayer = subatom['clip']['layer']
            Layers[layer][poly] = atom['Subatom'][sublayer]['result']
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
            clip = atom['Subatom'][subatom['clip']['layer']]['result']
        return clip
