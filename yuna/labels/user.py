import gdspy
import itertools as it

from yuna import utils
from yuna import process

from ..masternodes.capacitor import Capacitor
from ..masternodes.terminal import Terminal


def capacitors(cell, datafield):
    for lbl in cell.labels:
        if lbl.text[0] == 'C':
            cap = Capacitor(datafield.pcd.layers['cap'],
                               lbl.text,
                               lbl.position,
                               lbl.layer)

            cap.set_plates(datafield)
            cap.metal_connection(datafield)
            datafield.labels.append(cap)


def terminals(cell, datafield):
    for lbl in cell.labels:
        term = Terminal(datafield.pcd.layers['term'],
                           lbl.text,
                           lbl.position,
                           lbl.layer)

        term.metal_connection(datafield)
        datafield.labels.append(term)
