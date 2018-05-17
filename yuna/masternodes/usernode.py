import gdspy


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
