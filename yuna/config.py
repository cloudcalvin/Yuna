


class Layer:
    """  """

    def __init__(self):
        self.name = None
        self.type = None
        self.active = None
        self.union = None
        self.debug = None
        self.gds = None
        self.jj = None
        self.result = None


class Atom:
    """  """

    def __init__(self):
        self.id = None
        self.desc = None
        self.check = None
        self.skip = None
        self.Subatom = None


class Subatom:
    """  """

    def __init__(self):
        self.id = None
        self.gds = None
        self.name = None
        self.debug = None
        self.moduledata = None
        self.result = None

    def update_subatom(self, subatom, my_modules):
        self.id = subatom['id']
        self.gds = subatom['gds']
        self.name = subatom['name']
        self.debug = subatom['debug']
        self.result = subatom['result']
        self.moduledata = my_modules


class Module:
    """  """

    def __init__(self):
        self.id = None
        self.desc = None
        self.method = None
        self.type = None
        self.delete = None
        self.debug = None
        self.subj = None
        self.clip = None
        self.savein = None
        self.result = None

    def update_module(self, module):
        self.id = module['id']
        self.desc = module['desc']
        self.method = module['method']
        self.type = module['type']
        self.delete = module['delete']
        self.debug = module['debug']
        self.subj = module['subj']
        self.clip = module['clip']
        self.savein = module['savein']
        self.result = module['result']











