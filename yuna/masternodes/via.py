import gdspy

from yuna.pdk.properties import LabelProperties


class Via(LabelProperties):
    """

    """

    _ID = 0

    def __init__(self, position, params, id0=None):
        super(Via, self).__init__(position, **params)

        if id0 is None:
            self.id = 'via_{}'.format(Via._ID)
            Via._ID += 1
        else:
            self.id = 'poly {}'.format(id0)

        self.master = True

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)
