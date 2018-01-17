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
    

def get_ntron_box(gds, polygons, atom, auron_cell):
    """  """
    
    if gds == atom['wires']:
        for ntron in polygons[(gds, 4)]:
            box_poly = gdsyuna.Polygon(ntron, layer=gds, datatype=4)
            bb = box_poly.get_bounding_box()
            bb_poly = [[bb[0][0], bb[0][1]], 
                       [bb[1][0], bb[0][1]],
                       [bb[1][0], bb[1][1]],
                       [bb[0][0], bb[1][1]]]
            # auron_cell.add(gdsyuna.Polygon(bb_poly, layer=gds, datatype=4))
    return auron_cell
    
    
def connect_wire_to_ntrons(gds, polygons, atom, wires):
    if gds == atom['wires']:
        for poly in polygons[(gds, 4)]:
            wires = tools.angusj([poly], wires, 'union')
    return wires
    

def connect_wire_to_ntron_ground(gds, polygons, atom, wires):
    wire_diff = None
    if gds == atom['wires']:
        # wire_diff = tools.angusj(polygons[(gds, 4)], wires, 'difference')
        wire_diff = tools.angusj(wires, polygons[(gds, 5)], 'difference')
    return wire_diff
    
    
def get_side_direction(p1, p2):
    if p1[0] - p2[0] == 0:
        return 'y'
    elif p1[1] - p2[1] == 0:
        return 'x'
    else:
        return None
    
    
def side_connection(wires, wire_diff):
    print('-------- side poly')
    
    all_sides = list()
    for poly in wire_diff:
        for i in range(len(poly) - 1):
            p1, p2 = poly[i], poly[i+1]
            
            xy = get_side_direction(p1, p2)
            
            l = 0.5e6
            side_poly = list()
            if xy == 'x':
                tl = [p1[0], p1[1]+l]
                bl = [p1[0], p1[1]-l]
                
                br = [p2[0], p2[1]-l]
                tr = [p2[0], p2[1]+l]
                
                all_sides.append([tl, bl, br, tr])
            elif xy == 'y':
                tl = [p1[0]-l, p1[1]]
                bl = [p2[0]-l, p2[1]]
                
                br = [p2[0]+l, p2[1]]
                tr = [p1[0]+l, p1[1]]
                
                all_sides.append([tl, bl, br, tr])
    return all_sides
    
    
def wire_side_intersections(all_sides, wires, auron_cell, device):
    interpoly = []
    wire_poly = []
    for poly in all_sides:
        poly_offset = tools.angusj_offset([poly], 'down')
        if tools.angusj(poly_offset, wires, 'intersection'):
            inter_wire = tools.angusj([poly], wires, 'intersection')
            inter_device = tools.angusj([poly], device, 'intersection')
            
            # if inter_wire:
            # wires = tools.angusj([poly], wires, 'union')
            wire_poly.append([poly])
                
            device = tools.angusj(inter_device, device, 'difference')
            
            # if inter_wire:
            #     wires = tools.angusj([poly], wires, 'union')
            # auron_cell.add(gdsyuna.Polygon(poly_offset, layer=45, datatype=0))
    
    for poly in wire_poly:
        wires = tools.angusj(poly, wires, 'union')
        
    for poly in wires:
        auron_cell.add(gdsyuna.Polygon(poly, layer=45, datatype=0)) 
    for poly in device:
        auron_cell.add(gdsyuna.Polygon(poly, layer=45, datatype=0))
            
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
