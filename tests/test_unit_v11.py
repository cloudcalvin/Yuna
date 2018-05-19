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
    return yuna.grand_summon('OneBit', 'pdf.json', basedir)


@pytest.fixture(scope='module')
def networks(geometry):
    return mesh.mask_network(geometry)


def test_polygons(geometry):
    assert len(geometry.polygons) > 0


def test_user_labels(geometry):
    from yuna.masternodes.capacitor import Capacitor
    from yuna.masternodes.terminal import Terminal

    num_caps = 0
    for label in geometry.labels:
        if isinstance(label, Capacitor):
            num_caps += 1
    assert num_caps == 1

    num_terms = 0
    for label in geometry.labels:
        if isinstance(label, Terminal):
            num_terms += 1
    assert num_terms == 4


def test_cell_labels(geometry):
    assert len(geometry.labels) > 0

