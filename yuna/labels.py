import gdsyuna
import itertools as it

from yuna import utils
from yuna import process


def terminals(cell, datafield):
    for lbl in cell.labels:
        datafield.labels[lbl.text]['name'] = datafield.pcd.layers['term'][63].name
        datafield.labels[lbl.text]['type'] = 2
        datafield.labels[lbl.text]['labels'] = []
        datafield.labels[lbl.text]['labels'].append(lbl)

        for gds, metal in datafield.pcd.layers['ix'].items():
            m1 = lbl.text.split(' ')[1]
            m2 = lbl.text.split(' ')[2]
            if metal.name in [m1, m2]:
                if 'metals' in datafield.labels[lbl.text]:
                    datafield.labels[lbl.text]['metals'].append(int(gds))
                else:
                    datafield.labels[lbl.text]['metals'] = []
                    datafield.labels[lbl.text]['metals'].append(int(gds))


def add_label(cell, element, name, datafield, ttype):
    print('--- Adding label')
    bb = element.get_bounding_box()
    cx = ( (bb[0][0] + bb[1][0]) / 2.0 ) + 1.0
    cy = ( (bb[0][1] + bb[1][1]) / 2.0 )

    lbl = gdsyuna.Label(name, (cx, cy), 0, layer=64)
    cell.add(lbl)

    if ttype == 1:
        datafield.labels[lbl.text] = datafield.pcd.atoms['vias'][name]
        datafield.labels[lbl.text]['type'] = 1
    elif ttype == 3:
        datafield.labels[lbl.text] = datafield.pcd.atoms['jjs'][name]
        datafield.labels[lbl.text]['type'] = 3
    elif ttype == 4:
        datafield.labels[lbl.text] = datafield.pcd.atoms['jjs'][name]
        datafield.labels[lbl.text]['type'] = 4
    elif ttype == 5:
        datafield.labels[lbl.text] = datafield.pcd.atoms['jjs'][name]
        datafield.labels[lbl.text]['type'] = 5


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
    #             for points in utils.angusj(polygons[gds], polygons[key], 'intersection'):
    #                 poly = gdsyuna.Polygon(points, gds[0], verbose=False)
    #                 add_label(cell, poly, viadata.name, 1)

    ttype = datafield.pcd.atoms['vias'][cell.name]['type']
    add_label(cell, cell, cell.name, datafield, 1)


def junctions(cell, datafield):
    print('--- flattening ' + cell.name)
    cell.flatten(single_datatype=3)

    jjs = datafield.pcd.atoms['jjs']

    for element in cell.elements:
        if isinstance(element, gdsyuna.PolygonSet):
            if element.layers[0] == jjs[cell.name]['gds']:
                jj_poly = utils.angusj(element.polygons, element.polygons, 'union')
                poly = gdsyuna.Polygon(jj_poly, element.layers[0], verbose=False)

                add_label(cell, poly, cell.name, datafield, 3)
        elif isinstance(element, gdsyuna.Polygon):
            if element.layers == jjs[cell.name]['gds']:
                jj_poly = utils.angusj(element.polygons, element.polygons, 'union')
                poly = gdsyuna.Polygon(jj_poly, element.layers[0], verbose=False)

                add_label(cell, poly, cell.name, datafield, 3)

    jjs = datafield.pcd.atoms['jjs']

    get_shunt_connections(cell, jjs, datafield)

    if utils.has_ground(cell, jjs):
        get_ground_connection(cell, jjs, datafield)


def get_shunt_connections(cell, jj_atom, datafield):
    gds = jj_atom['shunt']['gds']

    polygons = cell.get_polygons(True)

    via_key = (int(gds), 3)
    shunt_key = (int(jj_atom['shunt']['metals'][1]), 3)

    for points in utils.angusj(polygons[via_key], polygons[shunt_key], 'intersection'):
        poly = gdsyuna.Polygon(points, gds, verbose=False)
        add_label(cell, poly, 'shunt', datafield, 4)


def get_ground_connection(cell, jj_atom, datafield):
    gds = jj_atom['ground']['gds']

    polygons = cell.get_polygons(True)

    via_key = (int(gds), 3)
    shunt_key = (int(jj_atom['ground']['metals'][0]), 3)

    if shunt_key != (30, 3):
        for points in utils.angusj(polygons[via_key], polygons[shunt_key], 'intersection'):
            poly = gdsyuna.Polygon(points, gds, verbose=False)
            add_label(cell, poly, 'ground', datafield, 5)


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
#                 for points in utils.angusj(polygons[gds], polygons[key], 'intersection'):
#                     poly = gdsyuna.Polygon(points, gds[0], verbose=False)
#                     add_label(cell, poly, viadata.name, 1)


# def get_ntron_layer(cell, atom, ttype):
#     points = cell.get_polygons(True)[(42, 0)]
#     poly = gdsyuna.Polygon(points, 42, verbose=False)
#     add_label(cell, poly, 'via_PlugVia', ttype)


def ntrons(cell, pdd):
    print('--- flattening ' + cell.name)
    cell.flatten(single_datatype=7)
