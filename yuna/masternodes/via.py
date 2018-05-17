import gdspy


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
