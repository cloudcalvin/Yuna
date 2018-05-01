import gdspy
import itertools as it

from yuna import utils
from yuna import process

from yuna import masternodes as mn


def capacitors(cell, datafield):
    for lbl in cell.labels:
        if lbl.text[0] == 'C':
            cap = mn.Capacitor(datafield.pcd.layers['cap'], lbl.text, lbl.position, lbl.layer)
            cap.metal_connection(datafield)
            datafield.labels.append(cap)


def terminals(cell, datafield):
    for lbl in cell.labels:
        term = mn.Terminal(datafield.pcd.layers['term'], lbl.text, lbl.position, lbl.layer)
        term.metal_connection(datafield)
        datafield.labels.append(term)

        # datafield.labels[lbl.text]['name'] = datafield.pcd.layers['term'][63].name
        # datafield.labels[lbl.text]['type'] = 2
        # datafield.labels[lbl.text]['labels'] = []
        # datafield.labels[lbl.text]['labels'].append(lbl)
        #
        # for gds, metal in datafield.pcd.layers['ix'].items():
        #     m1 = lbl.text.split(' ')[1]
        #     m2 = lbl.text.split(' ')[2]
        #     if metal.name in [m1, m2]:
        #         if 'metals' in datafield.labels[lbl.text]:
        #             datafield.labels[lbl.text]['metals'].append(int(gds))
        #         else:
        #             datafield.labels[lbl.text]['metals'] = []
        #             datafield.labels[lbl.text]['metals'].append(int(gds))