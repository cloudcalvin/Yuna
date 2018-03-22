import gdsyuna
from yuna import tools

from yuna import process

from .datafield import Label

import itertools as it


def terminals(cell, datafield):
    for lbl in cell.labels:
        datafield.labels[lbl.text]['name'] = datafield.pcd.layers['term'][63].name
        datafield.labels[lbl.text]['color'] = datafield.pcd.layers['term'][63].color
        datafield.labels[lbl.text]['type'] = 2
        datafield.labels[lbl.text]['labels'] = []
        datafield.labels[lbl.text]['labels'].append(lbl)

    print(datafield.labels)


def add_label(cell, element, name, datafield):
    print('--- Adding label')
    bb = element.get_bounding_box()
    cx = ( (bb[0][0] + bb[1][0]) / 2.0 ) + 1.0
    cy = ( (bb[0][1] + bb[1][1]) / 2.0 )

    lbl = gdsyuna.Label(name, (cx, cy), 0, layer=64)
    cell.add(lbl)

    datafield.labels[lbl.text] = datafield.pcd.atoms['vias'][name]
    datafield.labels[lbl.text]['type'] = 1


def intersect(pair):
    """ return the intersection of two lists """
    return list(set(pair[0]) & set(pair[1]))


def difference(a, b):
    """ return the union of two lists """
    return list(set(a) - set(b))


def vias(cell, datafield):
    print('--- flattening ' + cell.name)
    cell.flatten(single_datatype=1)

    # metals = pdd.atoms['vias'][cell.name]['metals']
    # connect = list(it.combinations(metals, 2))
    #
    # print(connect)

    # stacks = pdd.atoms['vias'][cell.name]['stack']
    #
    # all_wires = []
    # for stack in stacks:
    #     wires = pdd.vias[(int(stack), 0)].wires
    #     all_wires.append(wires)
    #
    # print(all_wires)
    # emerge = list(set(it.chain(*all_wires)))
    # print(emerge)
    # all_wires = list(it.combinations(all_wires, 2))
    # print(all_wires)
    #
    # intermitted_metals = []
    # if len(all_wires) > 0:
    #     for pair in all_wires:
    #         ii = intersect(pair)
    #         if len(ii) > 0:
    #             intermitted_metals.append(ii[0])
    #
    # print(intermitted_metals)
    #
    #
    # awe = difference(emerge, intermitted_metals)
    # print(awe)

    # connections = set(all_wires[0]).intersection(*all_wires)
    # connections = set.intersection(*map(set, all_wires))
    # print(connections)

    # polygons = cell.get_polygons(True)
    #
    # for gds, viadata in pdd.vias.items():
    #     for metal in viadata.wires:
    #         key = (int(metal), 0)
    #
    #         if gds in polygons and key in polygons:
    #             for points in tools.angusj(polygons[gds], polygons[key], 'intersection'):
    #                 poly = gdsyuna.Polygon(points, gds[0], verbose=False)
    #                 add_label(cell, poly, viadata.name, 1)

    ttype = datafield.pcd.atoms['vias'][cell.name]['type']
    add_label(cell, cell, cell.name, datafield)


def junctions(cell, datafield):
    print('--- flattening ' + cell.name)
    cell.flatten(single_datatype=3)

    ttype = datafield.pcd.atoms['jjs']['type']

    for component in datafield.pcd.components:
        if isinstance(component, process.Junction):
            for element in cell.elements:
                if isinstance(element, gdsyuna.PolygonSet):
                    if element.layers[0] == component.gds:
                        jj_poly = tools.angusj(element.polygons, element.polygons, 'union')
                        poly = gdsyuna.Polygon(jj_poly, element.layers[0], verbose=False)

                        add_label(cell, poly, cell.name, datafield)
                elif isinstance(element, gdsyuna.Polygon):
                    if element.layers == component.gds:
                        jj_poly = tools.angusj(element.polygons, element.polygons, 'union')
                        poly = gdsyuna.Polygon(jj_poly, element.layers[0], verbose=False)

                        add_label(cell, poly, cell.name, datafield)

    # jjs = datafield.pcd.atoms['jjs']
    #
    # get_shunt_connections(cell, jjs, ttype)
    #
    # if tools.has_ground(cell, jjs):
    #     get_ground_connection(cell, jjs, ttype)


def get_shunt_connections(cell, jj_atom, ttype):
    gds = jj_atom['shunt']['gds']
    name = jj_atom['shunt']['name']

    polygons = cell.get_polygons(True)

    via_key = (int(gds), 3)
    shunt_key = (int(jj_atom['shunt']['layers'][1]), 3)

    for points in tools.angusj(polygons[via_key], polygons[shunt_key], 'intersection'):
        poly = gdsyuna.Polygon(points, gds, verbose=False)
        add_label(cell, poly, name, ttype)


def get_ground_connection(cell, jj_atom, ttype):
    gds = jj_atom['ground']['gds']
    name = jj_atom['ground']['name']

    polygons = cell.get_polygons(True)

    via_key = (int(gds), 3)
    shunt_key = (int(jj_atom['ground']['layers'][1]), 3)

    if shunt_key != (30, 3):
        for points in tools.angusj(polygons[via_key], polygons[shunt_key], 'intersection'):
            poly = gdsyuna.Polygon(points, gds, verbose=false)
            add_label(cell, poly, name, ttype)


# def loop_pcf_vias(cell, pdd):
#     """
#     Loop through all the via information in the process
#     configuration file. Then apply polygon intersection
#     tests to see if via connections are made.
#     """
#
#     polygons = cell.get_polygons(True)
#
#     for gds, viadata in pdd.vias.items():
#         for metal in viadata.wires:
#             key = (int(metal), 0)
#
#             if gds in polygons and key in polygons:
#                 for points in tools.angusj(polygons[gds], polygons[key], 'intersection'):
#                     poly = gdsyuna.Polygon(points, gds[0], verbose=False)
#                     add_label(cell, poly, viadata.name, 1)


def get_ntron_layer(cell, atom, ttype):
    points = cell.get_polygons(True)[(42, 0)]
    poly = gdsyuna.Polygon(points, 42, verbose=False)
    add_label(cell, poly, 'via_PlugVia', ttype)


def ntrons(cell, pdd):
    print('--- flattening ' + cell.name)
    cell.flatten(single_datatype=4)
