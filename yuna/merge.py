import numpy as np
import networkx as nx
import itertools
import json
import gdsyuna
import pyclipper

from yuna import labels
from yuna import connect

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from yuna import tools

# def component(datafield, key, polygons, metals):
#     if key in polygons:
#         poly = polygons[key]
#         components = tools.angusj(poly, poly, 'union')
#
#         for pp in components:
#             datafield.add(structure.Polygon(pp, *key))
#
#         return tools.angusj(components, metals, 'difference')
