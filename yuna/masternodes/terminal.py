import gdspy

from yuna.pdk.properties import LabelProperties


class Terminal(LabelProperties):
    _ID = 0

    def __init__(self, position, params, id0=None):
        super(Terminal, self).__init__(position, **params)

        if id0 is None:
            self.id = 'P{}'.format(Terminal._ID)
            Terminal._ID += 1
        else:
            self.id = id0

        self.master = True

    # def _metal_connection(self, raw_pdk_data):
    #     metals = []
    #     print(self.text)
    #     label = self.text.split(' ')
    #
    #     ix_names = [data['name'] for data in raw_pdk_data['Layers']['ix']]
    #
    #     # TODO: Solve this fucking issue with the ground M0.
    #     if ix_names in label[1:]:
    #         gds = self._get_gds(name, raw_pdk_data)
    #
    #         if gds is not None:
    #             metals.append(gds)
    #         else:
    #             raise ValueError('gdsnumber cannot be None')
    #     return metals

    # def _get_gds(name, raw_pdk_data):
    #     for gds, data in raw_pdk_data['Layers']['ix'].items():
    #         if data.name == name:
    #             return gds
    #     return None

    def get_label(self):
        return gdspy.Label(self.text, self.position,
                           rotation=0, layer=64)
