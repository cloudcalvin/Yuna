import gdspy

from yuna.pdk.properties import LabelProperties


class UserNode(LabelProperties):
    """

    """

    _ID = 0

    def __init__(self, position, params, id0=None):
        super(UserNode, self).__init__(position, **params)

        if id0 is None:
            self.id = 'usernode_{}'.format(UserNode._ID)
            UserNode._ID += 1
        else:
            self.id = 'poly {}'.format(id0)

        self.master = True

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)
