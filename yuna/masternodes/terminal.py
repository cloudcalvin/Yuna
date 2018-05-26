import gdspy


class Terminal(gdspy.Label):
    _ID = 0

    def __init__(self, data, text, position, layer=0):
        super(Terminal, self).__init__(text, position, layer=layer)

        self.id = 'P{}'.format(Terminal._ID)
        Terminal._ID += 1

        if data is not None:
            self.data = data[layer]
        self.master = True

    def metal_connection(self, datafield):
        wires = {**datafield.pcd.layers['ix'],
                 **datafield.pcd.layers['term'],
                 **datafield.pcd.layers['res']}
        for gds, metal in wires.items():

            if self.text[0] == 'P':
                label = self.text.split(' ')

                # TODO: Solve this fucking issue with the ground M0.
                if metal.name in label[1:]:
                    self.data.metals.append(gds)

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)
