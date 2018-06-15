import gdspy

from yuna.pdk.properties import LabelProperties


class Inductor(LabelProperties):
    """

    """

    _ID = 0

    def __init__(self, position, params, id0=None):
        super(Inductor, self).__init__(position, **params)

        if id0 is None:
            self.id = 'L{}'.format(Inductor._ID)
            Inductor._ID += 1
        else:
            self.id = 'poly {}'.format(id0)
