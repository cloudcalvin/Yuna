import gdsyuna
from yuna import tools

from yuna import process


def add_label(cell, element, name):
    bb = element.get_bounding_box()
    cx = ( (bb[0][0] + bb[1][0]) / 2.0 ) + 1.0
    cy = ( (bb[0][1] + bb[1][1]) / 2.0 )
    label = gdsyuna.Label(name, (cx, cy), 'nw', layer=64)
    cell.add(label)


def vias(cell, pdd):
    print('--- flattening ' + cell.name)
    cell.flatten(single_datatype=1)

    add_label(cell, cell, cell.name)


def junctions(cell, pdd):
    print('--- flattening ' + cell.name)
    cell.flatten(single_datatype=3)

    get_jj_layer(cell, pdd)
    get_shunt_connections(cell, pdd.atoms['jjs'])

    if tools.has_ground(cell, pdd.atoms['jjs']):
        get_ground_connection(cell, pdd.atoms['jjs'])


def ntrons(cell, pdd):
    print('--- flattening ' + cell.name)
    cell.flatten(single_datatype=4)


def get_jj_layer(cell, pdd):
    """ We have to temporelaly flatten the JJ cell to get the
    JJ layer, since the JJ layer can be inside another cell. """

    # for key, layer in pdd.junctions.items():
    for component in pdd.components:
        if isinstance(component, process.Junction):
            for element in cell.elements:
                if isinstance(element, gdsyuna.PolygonSet):
                    if element.layers[0] == component.gds:
                        jj_poly = tools.angusj(element.polygons, element.polygons, 'union')
                        poly = gdsyuna.Polygon(jj_poly, element.layers[0], verbose=False)
                        add_label(cell, poly, cell.name)
                elif isinstance(element, gdsyuna.Polygon):
                    if element.layers == component.gds:
                        add_label(cell, poly, cell.name)


def get_shunt_connections(cell, jj_atom):
    jj_cell = gdsyuna.Cell('jj_cell_' + cell.name)

    gds = jj_atom['shunt']['gds']
    name = jj_atom['shunt']['name']

    polygons = cell.get_polygons(True)

    via_key = (int(gds), 3)
    shunt_key = (int(jj_atom['shunt']['layers'][1]), 3)

    for points in tools.angusj(polygons[via_key], polygons[shunt_key], 'intersection'):
        poly = gdsyuna.Polygon(points, gds, verbose=False)
        add_label(cell, poly, name)
        # jj_cell.add(polygons)

def get_ground_connection(cell, jj_atom):
    jj_cell = gdsyuna.Cell('jj_gnd_' + cell.name)

    gds = jj_atom['ground']['gds']
    name = jj_atom['ground']['name']

    polygons = cell.get_polygons(True)

    via_key = (int(gds), 3)
    shunt_key = (int(jj_atom['ground']['layers'][1]), 3)

    for points in tools.angusj(polygons[via_key], polygons[shunt_key], 'intersection'):
        poly = gdsyuna.Polygon(points, gds, verbose=False)
        add_label(cell, poly, name)
        # jj_cell.add(polygons)

def get_ntron_layer(cell, atom):
    points = cell.get_polygons(True)[(42, 0)]
    poly = gdsyuna.Polygon(points, 42, verbose=False)
    add_label(cell, poly, 'via_PlugVia')
