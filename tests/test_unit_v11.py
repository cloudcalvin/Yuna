'''
Module showing how doctests can be included with source code
Each '>>>' line is run as if in a python shell, and counts as a test.
The next line, if not '>>>' is the expected output of the previous line.
If anything doesn't match exactly (including trailing spaces), the test fails.
'''


import yuna
import os
import gdspy
import pytest
import networkx as nx
from auron import mesh

 
@pytest.fixture(scope='module')
def geometry():
    basedir = os.getcwd() + '/tests/data' + '/unit_v11'
    return yuna.grand_summon(basedir, 'OneBit', 'pdf.json')
    
    
@pytest.fixture(scope='module')
def networks(geometry):
    return mesh.mask_network(geometry)

    
def test_polygons(geometry):
    assert len(geometry.polygons) > 0
    

def test_labels(geometry):
    assert len(geometry.labels) > 0
    
    
def test_gmsh_mesh(networks):
    assert len(networks) > 0

    assert len(networks[5]) > 0
    assert len(networks[4]) > 0

    # for gds, graph in networks.items():

        # assert len(topolgy.mesh['points']) > 0
        # assert len(topolgy.mesh['cells']) > 0
        
        # assert bool(topolgy.mesh['cell_data'])
        # assert bool(topolgy.mesh['field_data'])
        
        # assert len(topolgy.mesh['cell_data']['triangle']['gmsh:physical']) > 0
        # assert len(topolgy.mesh['cell_data']['triangle']['gmsh:geometrical']) > 0
            
    
# def test_labels_in_mesh(gds_layout, get_topology):
#     layoutcell = gds_layout[0]
#     configdata = gds_layout[1]
    
#     for gds, topolgy in get_topology.items():
#         lbl = topolgy.add_network_labels(configdata, gds, layoutcell)
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
