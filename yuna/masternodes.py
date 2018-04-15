import gdspy


class Inductor(gdspy.Label):
    _ID = 0

    def __init__(self, text, position, layer=0, id0=None):
        super(Inductor, self).__init__(text, position, layer=layer)

        if id0 is None:
            self.id = 'i{}'.format(Inductor._ID)
        else:
            self.id = 'poly {}'.format(id0)

        Inductor._ID += 1

        self.data = {}
        self.data['color'] = '#66FFB2'
        self.master = False


class Resistors(object):

    def __init__(self):
        pass


class Hole(object):

    def __init__(self):
        pass


class Terminal(gdspy.Label):
    _ID = 0

    def __init__(self, data, text, position, layer=0):
        super(Terminal, self).__init__(text, position, layer=layer)

        self.id = 't{}'.format(Terminal._ID)
        Terminal._ID += 1

        self.data = data[layer]
        self.master = True

    def metal_connection(self, datafield):
        wires = {**datafield.pcd.layers['ix'],
                 **datafield.pcd.layers['term'],
                 **datafield.pcd.layers['res']}

        for gds, metal in wires.items():
            m1 = self.text.split(' ')[1]
            m2 = self.text.split(' ')[2]

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
            self.id = 'v{}'.format(Via._ID)
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


class Capacitor(object):

    def __init__(self, gds, data):
        self.gds = gds
        self.data = data
        self.master = True


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
            self.id = 'j{}'.format(Junction._ID)
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
            self.id = 's{}'.format(Shunt._ID)
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
            self.id = 'g{}'.format(Ground._ID)
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

    def __init__(self, text, position, rotation=0, layer=0):
        super(Ntron, self).__init__(text, position, rotation=rotation, layer=layer)

        self.id = 'j{}'.format(Ntron._ID)
        Ntron._ID += 1

        self.data = {}
        self.data['color'] = '#FF5555'
        self.master = True

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)
