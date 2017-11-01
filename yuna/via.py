

class Via:
    """
    """

    def __init__(self, value):
        """
        """

        self.wire_1 = value['wire_1']
        self.wire_2 = value['wire_2']
        self.via_layer = value['via_layer']

    def subject(self):
        """  """

        Atom = self.config_data['Atom']
        Layers = self.config_data['Layers']

        subj_class = self.wire_1.keys()
        subj_layer = module['subj']['layer']
        subj_poly = module['subj']['savein']

        if subj_class == 'Layers':
            subj = Layers[subj_layer][subj_poly]
        elif subj_class == 'Module':
            subj = Subatom['result']

        return subj

    def clipper(self):
        """  """
