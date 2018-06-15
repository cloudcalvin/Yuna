


class LayerBase(object):
    """

    """

    _ID = 0

    def __init__(self, data):
        self.name = data['name']
        self.color = data['color']
        self.rank = None
        self.width = None

        self.id = LayerBase._ID
        LayerBase._ID += 1
