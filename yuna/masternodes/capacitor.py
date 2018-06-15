import gdspy

from yuna.pdk.properties import LabelProperties


class Capacitor(LabelProperties):
    """

    """

    _ID = 0

    def __init__(self, position, params, id0=None):
        super(Capacitor, self).__init__(position, **params)

        if id0 is None:
            self.id = 'C{}'.format(Capacitor._ID)
            Capacitor._ID += 1
        else:
            self.id = id0

        self.master = True

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)
