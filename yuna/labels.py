import gdsyuna
import tools


def detect_jj_using_cells(cell, Layers):
    """ We have to temporelaly flatten the JJ cell to get the 
    JJ layer, since the JJ layer can be inside another cell. """
    
    for key, layer in Layers.items():
        if layer['type'] == 'junction':
            for element in cell.elements:
                if isinstance(element, gdsyuna.PolygonSet):
                    if element.layers[0] == int(key):
                        jj_poly = tools.angusj(element.polygons, element.polygons, 'union')
                        poly = gdsyuna.Polygon(jj_poly, element.layers[0])
                        bb = poly.get_bounding_box()
                        add_label(cell, cell.name, bb)
                elif isinstance(element, gdsyuna.Polygon):
                    if element.layers == int(key):
                        add_label(cell, cell.name, bb)


def add_label(cell, name, bb):
    cx = ( (bb[0][0] + bb[1][0]) / 2.0 ) + 1.0
    cy = ( (bb[0][1] + bb[1][1]) / 2.0 )
    label = gdsyuna.Label(name, (cx, cy), 'nw', layer=11)
    cell.add(label)


def add_to_polygon_center(cell, points, gds, name):
    poly = gdsyuna.Polygon(points, gds)
    bb = poly.get_bounding_box()
    add_label(cell, name, bb)


def add_to_cell_center(cell):
    bb = cell.get_bounding_box()
    add_label(cell, cell.name, bb)


def label_jj_shunt_connections(cell, jj_atom):
    jj_cell = gdsyuna.Cell('jj_cell_' + cell.name)
    atom = jj_atom['shunt']

    gds = atom['via']
    name = atom['name']
    
    polygons = cell.get_polygons(True)
    
    via_key = (int(atom['via']), 3)
    shunt_key = (int(atom['shunt']), 3)
    
    for via in tools.angusj(polygons[via_key], polygons[shunt_key], 'intersection'):
        add_to_polygon_center(cell, via, gds, name)
        # jj_cell.add(polygons)
        
def label_jj_ground_connection(cell, jj_atom):
    jj_cell = gdsyuna.Cell('jj_gnd_' + cell.name)
    atom = jj_atom['ground']

    gds = atom['via']
    name = atom['name']
    
    polygons = cell.get_polygons(True)
    
    via_key = (int(atom['via']), 3)
    shunt_key = (int(atom['gnd']), 3)
    
    for via in tools.angusj(polygons[via_key], polygons[shunt_key], 'intersection'):
        add_to_polygon_center(cell, via, gds, name)
        # jj_cell.add(polygons)
        
def label_ntron_connection(cell, atom):
    ntron_cell = gdsyuna.Cell('ntron' + cell.name)
    
    key = (int(atom['ferro']), 4)
    polygons = cell.get_polygons(True)[key]

    gds = atom['ferro']
    name = atom['name']

    add_to_polygon_center(cell, polygons, gds, name)
        
def has_ground(cell, jj_atom):
    atom = jj_atom['ground']
    key = (int(atom['via']), 3)
    
    if key in cell.get_polygons(True):
        return True
    else:
        return False