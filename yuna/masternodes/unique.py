import gdspy


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
