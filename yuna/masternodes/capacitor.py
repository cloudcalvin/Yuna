import gdspy

from collections import defaultdict
from collections import namedtuple


class Capacitor(gdspy.Label):
    _ID = 0

    def __init__(self, data, text, position, layer=0, atom=None, id0=None):
        super(Capacitor, self).__init__(text, position, layer=layer)

        if id0 is None:
            self.id = 'C{}'.format(Capacitor._ID)
        else:
            self.id = id0

        Capacitor._ID += 1

        self.plates = defaultdict()

        self.data = data[layer]
        self.master = True

    def set_plates(self, datafield):
        Plates = namedtuple('Plates', ['term', 'label'])

        wires = {**datafield.pcd.layers['ix'],
                 **datafield.pcd.layers['cap']}

        for gds, metal in wires.items():
            if self.text[0] == 'C':
                label = self.text.split(' ')

                m1 = label[1]
                m2 = label[2]

                if metal.name == m1:
                    self.plates[gds] = Plates(term='+', label=m1)
                elif metal.name == m2:
                    self.plates[gds] = Plates(term='-', label=m2)

    def metal_connection(self, datafield):
        wires = {**datafield.pcd.layers['ix'],
                 **datafield.pcd.layers['cap']}

        for gds, metal in wires.items():
            if self.text[0] == 'C':
                label = self.text.split(' ')

                m1 = label[1]
                m2 = label[2]

                # TODO: Solve this fucking issue with the ground M0.
                if metal.name in [m1, m2]:
                    self.data.metals.append(gds)

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)
