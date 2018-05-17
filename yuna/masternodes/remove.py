import gdspy

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
