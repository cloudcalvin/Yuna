import gdspy


class Inductor(object):

    def __init__(self, gds, data):
        self.gds = gds
        self.data = data


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

    # def __init__(self, name, data):
    def __init__(self, atom, text, position, rotation=0, layer=0):
        super(Via, self).__init__(text, position, rotation=rotation, layer=layer)

        self.id = 'v{}'.format(Via._ID)
        Via._ID += 1

        self.data = atom[text]
        self.data['color'] = "#A0A0A0"
        self.master = True

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)


class Capacitor(object):

    def __init__(self, gds, data):
        self.gds = gds
        self.data = data
        self.master = True


class Junction(gdspy.Label):
    _ID = 0

    # def __init__(self, name, data):
    def __init__(self, text, position, rotation=0, layer=0):
        super(Junction, self).__init__(text, position, rotation=rotation, layer=layer)

        self.id = 'j{}'.format(Junction._ID)
        Junction._ID += 1

        # self.data = data
        self.master = True

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)


class Ntron(gdspy.Label):
    _ID = 0

    # def __init__(self, name, data):
    def __init__(self, text, position, rotation=0, layer=0):
        super(Ntron, self).__init__(text, position, rotation=rotation, layer=layer)

        self.id = 'j{}'.format(Ntron._ID)
        Ntron._ID += 1

        # self.data = data
        self.master = True

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)
