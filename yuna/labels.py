import gdsyuna
import tools
import gdsyuna


def add_label(cell, element, name):
    bb = element.get_bounding_box()
    cx = ( (bb[0][0] + bb[1][0]) / 2.0 ) + 1.0
    cy = ( (bb[0][1] + bb[1][1]) / 2.0 )
    label = gdsyuna.Label(name, (cx, cy), 'nw', layer=64)
    cell.add(label)
    
    
def vias(cell, Layers, Atom):
    tools.green_print('Flattening via: ' + cell.name)
    cell.flatten(single_datatype=1)

    add_label(cell, cell, cell.name)
    
    
def junctions(cell, Layers, Atom):
    tools.green_print('Flattening junction: ' + cell.name)
    cell.flatten(single_datatype=3)
    
    get_jj_layer(cell, Layers)
    get_shunt_connections(cell, Atom['jjs'])

    if tools.has_ground(cell, Atom['jjs']):
        get_ground_connection(cell, Atom['jjs'])
        
        
def ntrons(cell, Layers, Atom):
    # if cell.name[-3:] == 'gnd':
    #     tools.green_print('Flattening ntron: ' + cell.name)
    #     cell.flatten(single_datatype=4)
    # 
    #     get_ntron_layer(cell, Atom['ntron'])
    # else:
    #     tools.green_print('Flattening ntron: ' + cell.name)
    #     cell.flatten(single_datatype=5)
    # 
    #     add_label(cell, cell, cell.name)
        
    tools.green_print('Flattening ntron: ' + cell.name)
    cell.flatten(single_datatype=4)
    
    # add_label(cell, cell, cell.name)
    
    for element in cell.elements:
        if isinstance(element, gdsyuna.PolygonSet):
            if element.layers[0] == 45:
                element.polygons = tools.angusj(element.polygons, element.polygons, 'union')
    return cell


def get_jj_layer(cell, Layers):
    """ We have to temporelaly flatten the JJ cell to get the 
    JJ layer, since the JJ layer can be inside another cell. """
    
    for gds, layer in Layers.items():
        if layer['type'] == 'junction':
            for element in cell.elements:
                if isinstance(element, gdsyuna.PolygonSet):
                    if element.layers[0] == int(gds):
                        jj_poly = tools.angusj(element.polygons, element.polygons, 'union')
                        poly = gdsyuna.Polygon(jj_poly, element.layers[0])
                        add_label(cell, poly, cell.name)
                elif isinstance(element, gdsyuna.Polygon):
                    if element.layers == int(gds):
                        add_label(cell, poly, cell.name)


def get_shunt_connections(cell, jj_atom):
    jj_cell = gdsyuna.Cell('jj_cell_' + cell.name)

    gds = jj_atom['shunt']['via']
    name = jj_atom['shunt']['name']
    
    polygons = cell.get_polygons(True)
    
    via_key = (int(gds), 3)
    shunt_key = (int(jj_atom['shunt']['shunt']), 3)
    
    for points in tools.angusj(polygons[via_key], polygons[shunt_key], 'intersection'):
        poly = gdsyuna.Polygon(points, gds)
        add_label(cell, poly, name)
        # jj_cell.add(polygons)
        
def get_ground_connection(cell, jj_atom):
    jj_cell = gdsyuna.Cell('jj_gnd_' + cell.name)

    gds = jj_atom['ground']['via']
    name = jj_atom['ground']['name']
    
    polygons = cell.get_polygons(True)
    
    via_key = (int(gds), 3)
    shunt_key = (int(jj_atom['ground']['gnd']), 3)
    
    for points in tools.angusj(polygons[via_key], polygons[shunt_key], 'intersection'):
        poly = gdsyuna.Polygon(points, gds)
        add_label(cell, poly, name)
        # jj_cell.add(polygons)
        
def get_ntron_layer(cell, atom):
    ntron_cell = gdsyuna.Cell('ntron' + cell.name)
    
    # gds = 45
    # key = (gds, 4)
    # points = cell.get_polygons(True)[key]
    # pp = tools.angusj(points, points, 'union')
    # poly = gdsyuna.Polygon(points, gds)
    # print(poly)
    
    # return ntron_cell.add(pp)
    
    # # for gds, layer in Layers.items():
    # #     if layer['type'] == 'ntron':
    # #         for element in cell.elements:
    # #             if isinstance(element, gdsyuna.PolygonSet):
    # #                 if element.layers[0] == int(gds):
    # #                     jj_poly = tools.angusj(element.polygons, element.polygons, 'union')
    # #                     poly = gdsyuna.Polygon(jj_poly, element.layers[0])
    # #                     add_label(cell, poly, cell.name)
    # #             elif isinstance(element, gdsyuna.Polygon):
    # #                 if element.layers == int(gds):
    # #                     add_label(cell, poly, cell.name)

    points = cell.get_polygons(True)[(42, 0)]
    poly = gdsyuna.Polygon(points, 42)
    add_label(cell, poly, 'via_PlugVia')
    
    
    
    
    
    
    
    
    
    
