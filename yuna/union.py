import tools


def union_same_vias(vias, wire):
    """ Union vias of the same type. """

    tools.green_print('Union vias:')

    via_union = list()
    for v1 in vias:
        for v2 in vias:
            if v1 is not v2:
                if tools.does_layers_intersect([v1], [v2]):
                    for union in tools.angusj([v1], [v2], 'union'):
                        via_union.append(union)

    return list(via_union for via_union,_ in itertools.groupby(via_union))


def union_wires(yuna_flatten, auron_cell, wire, mtype):
    """  """

    tools.green_print('Union wires: ' + str(wire))

    polygons = yuna_flatten.get_polygons(True)

    wires = None
    if (wire, 0) in polygons:
        print('Layers active: ' + str(wire))
        wires = yuna_flatten.get_polygons(True)[(wire, 0)]
        wires = tools.angusj(wires, wires, 'union')
        
    return wires


def union_vias(yuna_flatten, auron_cell, wire, wires):
    """ Union vias with wires, but remove redundant 
    vias that are not connected to any wires. """
    
    polygons = yuna_flatten.get_polygons(True)
    if wires is not None:
        if (wire, 1) in polygons:
            for via in yuna_flatten.get_polygons(True)[(wire, 1)]:
                via_offset = tools.angusj_offset([via], 'up')
                if tools.does_layers_intersect(via_offset, wires):
                    wires = tools.angusj([via], wires, 'union')

    return wires

            
def union_jjs(yuna_flatten, auron_cell, wire, wires, mtype):
    """ We know the wires inside a jj, so
    we only have to union it with wires
    and don't have to remove any jj layers. """
    
    polygons = yuna_flatten.get_polygons(True)
    if wires is not None:
        if (wire, 3) in polygons:
            for jj in yuna_flatten.get_polygons(True)[(wire, 3)]:
                wires = tools.angusj([jj], wires, 'union')
    else:
        if mtype == 'shunt':
            if (wire, 3) in polygons:
                for jj in yuna_flatten.get_polygons(True)[(wire, 3)]:
                    auron_cell.add(gdsyuna.Polygon(jj, layer=wire, datatype=0))
                    
    return wires

        
def union_ntrons(yuna_flatten, auron_cell, wire, wires, mtype):
    """  """
    polygons = yuna_flatten.get_polygons(True)
    if wires is not None:
        if (wire, 4) in polygons:
            for ntron in yuna_flatten.get_polygons(True)[(wire, 4)]:
                wires = tools.angusj([ntron], wires, 'union')
    return wires