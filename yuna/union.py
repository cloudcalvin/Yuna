import tools
import gdsyuna


def default_layer_polygons(gds, polygons):
    """  """

    tools.green_print('Union wires: ' + str(gds))

    wires = None
    if (gds, 0) in polygons:
        wires = polygons[(gds, 0)]
        wires = tools.angusj(wires, wires, 'union')
    return wires

def connect_wire_to_vias(gds, wires, polygons):
    """ Union vias with wires, but remove redundant 
    vias that are not connected to any wires. """

    for via in polygons[(gds, 1)]:
        via_offset = tools.angusj_offset([via], 'up')
        if tools.angusj(via_offset, wires, 'intersection'):
            wires = tools.angusj([via], wires, 'union')
    return wires

def connect_wire_to_jjs(gds, wires, polygons):
    """ We know the wires inside a jj, so we only have to 
    union it with wires and don't have to remove any jj layers. """

    for jj in polygons[(gds, 3)]:
        wires = tools.angusj([jj], wires, 'union')
    return wires

def connect_wire_to_ntrons(gds, polygons, atom, auron_cell):
    """  """
    
    if gds == atom['wires']:
        for ntron in polygons[(gds, 4)]:
            box_poly = gdsyuna.Polygon(ntron, layer=gds, datatype=4)
            bb = box_poly.get_bounding_box()
            bb_poly = [[bb[0][0], bb[0][1]], 
                       [bb[1][0], bb[0][1]],
                       [bb[1][0], bb[1][1]],
                       [bb[0][0], bb[1][1]]]
            auron_cell.add(gdsyuna.Polygon(bb_poly, layer=gds, datatype=4))
    return auron_cell


# def union_same_vias(vias, wire):
#     """ Union vias of the same type. """

#     tools.green_print('Union vias:')

#     via_union = list()
#     for v1 in vias:
#         for v2 in vias:
#             if v1 is not v2:
#                 if tools.does_layers_intersect([v1], [v2]):
#                     for union in tools.angusj([v1], [v2], 'union'):
#                         via_union.append(union)

#     return list(via_union for via_union,_ in itertools.groupby(via_union))









