import gdspy


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
