import gdspy
import itertools as it

from yuna import utils
from yuna import process

from yuna import masternodes as mn


def add_label(cell, element, name, datafield):
    print('--- Adding label: ' + name)
    bb = element.get_bounding_box()
    cx = ( (bb[0][0] + bb[1][0]) / 2.0 ) + 10.0 #TODO: Watchout for this caveat
    cy = ( (bb[0][1] + bb[1][1]) / 2.0 )

    lbl = gdspy.Label(name, (cx, cy), 0, layer=64)
    cell.add(lbl)


# def intersect(pair):
#     """ return the intersection of two lists """
#     return list(set(pair[0]) & set(pair[1]))
#
#
# def difference(a, b):
#     """ return the union of two lists """
#     return list(set(a) - set(b))


def vias(cell, datafield):
    print('--- flattening ' + cell.name)
    cell.flatten(single_datatype=1)

    add_label(cell, cell, cell.name, datafield)


def junctions(cell, datafield):
    print('--- flattening ' + cell.name)
    cell.flatten(single_datatype=3)

    jjs = datafield.pcd.atoms['jjs']

    for element in cell.elements:
        if isinstance(element, gdspy.PolygonSet):
            if element.layers[0] == jjs[cell.name]['gds']:
                jj_poly = utils.angusj(element.polygons, element.polygons, 'union')
                poly = gdspy.Polygon(jj_poly, element.layers[0], verbose=False)

                add_label(cell, poly, cell.name, datafield)
        elif isinstance(element, gdspy.Polygon):
            if element.layers == jjs[cell.name]['gds']:
                jj_poly = utils.angusj(element.polygons, element.polygons, 'union')
                poly = gdspy.Polygon(jj_poly, element.layers[0], verbose=False)

                add_label(cell, poly, cell.name, datafield)

    jjs = datafield.pcd.atoms['jjs']

    get_shunt_connections(cell, jjs, datafield)
    get_ground_connection(cell, jjs, datafield)

    # if utils.has_ground(cell, jjs):
    #     get_ground_connection(cell, jjs, datafield)


def get_shunt_connections(cell, jj_atom, datafield):
    gds = jj_atom['shunt']['gds']

    polygons = cell.get_polygons(True)

    via_key = (int(gds), 3)
    shunt_key = (int(jj_atom['shunt']['metals'][1]), 3)

    for points in utils.angusj(polygons[via_key], polygons[shunt_key], 'intersection'):
        poly = gdspy.Polygon(points, gds, verbose=False)
        add_label(cell, poly, 'shunt', datafield)


def get_ground_connection(cell, jj_atom, datafield):
    gds = jj_atom['ground']['gds']

    polygons = cell.get_polygons(True)

    via = (int(gds), 3)

    ii = polygons[via]

    for layer in jj_atom['ground']['metals']:
        pp = (int(layer), 3)

        ii = utils.angusj(ii, polygons[pp], 'intersection')

        # for points in utils.angusj(polygons[via_key], polygons[pp], 'intersection'):
        #     poly = gdspy.Polygon(points, gds, verbose=False)
        #     add_label(cell, poly, 'ground', datafield)

    for points in ii:
        poly = gdspy.Polygon(points, gds, verbose=False)
        add_label(cell, poly, 'ground', datafield)


def ntrons(cell, datafield):
    print('--- flattening ' + cell.name)
    data = datafield.pcd.atoms['ntrons'][cell.name]

    cell.flatten(single_layer=data['metals'][0], single_datatype=7)

    add_label(cell, cell, cell.name, datafield)
