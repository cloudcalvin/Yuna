import gdspy

from collections import namedtuple
from collections import defaultdict


class Inductor(gdspy.Label):
    _ID = 0

    def __init__(self, text, position, layer=0, id0=None):
        super(Inductor, self).__init__(text, position, layer=layer)

        if id0 is None:
            self.id = 'L{}'.format(Inductor._ID)
        else:
            self.id = 'poly {}'.format(id0)

        Inductor._ID += 1

        self.data = {}
        self.data['color'] = '#66FFB2'
        self.master = False


class Remove(gdspy.Label):
    _ID = 0

    def __init__(self, text, position, layer=0, id0=None):
        super(Remove, self).__init__(text, position, layer=layer)

        if id0 is None:
            self.id = 'rm_{}'.format(Remove._ID)
        else:
            self.id = 'poly {}'.format(id0)

        Remove._ID += 1

        self.data = {}
        self.data['color'] = '#CC99FF'
        self.master = False


class Unique(gdspy.Label):
    _ID = 0

    def __init__(self, text, position, layer=0, id0=None):
        super(Unique, self).__init__(text, position, layer=layer)

        if id0 is None:
            self.id = 'unique_{}'.format(Unique._ID)
        else:
            self.id = 'poly {}'.format(id0)

        Unique._ID += 1

        self.data = {}
        self.data['color'] = '#CC99FF'
        self.master = False


class Terminal(gdspy.Label):
    _ID = 0

    def __init__(self, data, text, position, layer=0):
        super(Terminal, self).__init__(text, position, layer=layer)

        self.id = 'P{}'.format(Terminal._ID)
        Terminal._ID += 1

        self.data = data[layer]
        self.master = True

    def metal_connection(self, datafield):
        wires = {**datafield.pcd.layers['ix'],
                 **datafield.pcd.layers['term'],
                 **datafield.pcd.layers['res']}
        for gds, metal in wires.items():

            if self.text[0] == 'P':
                label = self.text.split(' ')

                # TODO: Solve this fucking issue with the ground M0.
                if metal.name in label[1:]:
                    self.data.metals.append(gds)

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)


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


class Via(gdspy.Label):
    _ID = 0

    def __init__(self, text, position, rotation=0, layer=0, atom=None, id0=None):
        super(Via, self).__init__(text, position, rotation=rotation, layer=layer)

        if id0 is None:
            self.id = 'via_{}'.format(Via._ID)
        else:
            self.id = 'poly {}'.format(id0)

        Via._ID += 1

        if atom is not None:
            self.data = atom[text]
        else:
            self.data = {}
            self.data['color'] = "#A0A0A0"

        self.master = True

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)

    def update_id(self, id0=None):
        self.id = self.pid
        self.data['color'] = "#A0A0A0"


class Junction(gdspy.Label):
    """
    Arguments
    ---------
    id0 : string
        This is id of the junction polygon from the datafield object.
    """

    _ID = 0

    def __init__(self, text, position, layer=0, atom=None, id0=None):
        super(Junction, self).__init__(text, position, layer=layer)

        if id0 is None:
            self.id = 'jj_{}'.format(Junction._ID)
        else:
            self.id = 'poly {}'.format(id0)

        Junction._ID += 1

        if atom is not None:
            self.data = atom[text]
        else:
            self.data = {}
            self.data['color'] = '#FFCC99'

        self.master = True

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)


class Shunt(gdspy.Label):
    """
    Arguments
    ---------
    id0 : string
        This is id of the junction polygon from the datafield object.
    """

    _ID = 0

    def __init__(self, text, position, layer=0, atom=None, id0=None):
        super(Shunt, self).__init__(text, position, layer=layer)

        if id0 is None:
            self.id = 'shunt_{}'.format(Shunt._ID)
        else:
            self.id = 'poly {}'.format(id0)

        Shunt._ID += 1

        if atom is not None:
            self.data = atom[text]
        else:
            self.data = {}
            self.data['color'] = '#FF6666'

        self.master = True

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)


class Ground(gdspy.Label):
    """
    Arguments
    ---------
    id0 : string
        This is id of the junction polygon from the datafield object.
    """

    _ID = 0

    def __init__(self, text, position, layer=0, atom=None, id0=None):
        super(Ground, self).__init__(text, position, layer=layer)

        if id0 is None:
            self.id = 'gnd_{}'.format(Ground._ID)
        else:
            self.id = 'poly {}'.format(id0)

        Ground._ID += 1

        if atom is not None:
            self.data = atom[text]
        else:
            self.data = {}
            self.data['color'] = '#FF66B2'

        self.master = True

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)


class Ntron(gdspy.Label):
    _ID = 0

    def __init__(self, text, position, rotation=0, layer=0, atom=None, id0=None):
        super(Ntron, self).__init__(text, position, rotation=rotation, layer=layer)

        if id0 is None:
            self.id = 'ntron_{}'.format(Ntron._ID)
        else:
            self.id = 'poly {}'.format(id0)

        Ntron._ID += 1

        if atom is not None:
            self.data = atom[text]
        else:
            self.data = {}
            self.data['color'] = '#FF5555'

        self.master = True

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)


class UserNode(gdspy.Label):
    _ID = 0

    def __init__(self, text, position, rotation=0, layer=0, atom=None, id0=None):
        super(UserNode, self).__init__(text, position, rotation=rotation, layer=layer)

        if id0 is None:
            self.id = 'un_{}'.format(UserNode._ID)
        else:
            self.id = 'poly {}'.format(id0)

        UserNode._ID += 1

        if atom is not None:
            self.data = atom[text]
        else:
            self.data = {}
            self.data['color'] = '#76D7C4'

        self.master = True

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)
