import gdspy
import itertools as it

from yuna import utils
from yuna import process

from yuna import masternodes as mn


def capacitors(cell, datafield):
    for lbl in cell.labels:
        if lbl.text[0] == 'C':
            cap = mn.Capacitor(datafield.pcd.layers['cap'],
                               lbl.text,
                               lbl.position,
                               lbl.layer)

            cap.set_plates(datafield)
            cap.metal_connection(datafield)
            datafield.labels.append(cap)


def terminals(cell, datafield):
    for lbl in cell.labels:
        term = mn.Terminal(datafield.pcd.layers['term'],
                           lbl.text,
                           lbl.position,
                           lbl.layer)

        term.metal_connection(datafield)
        datafield.labels.append(term)
