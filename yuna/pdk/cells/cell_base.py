


class CellBase(object):
    """

    """

    _ID = 0

    def __init__(self, data):
        self.id = CellBase._ID
        CellBase._ID += 1
