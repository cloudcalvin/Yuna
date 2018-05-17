import gdspy


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
