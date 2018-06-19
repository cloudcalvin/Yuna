import gdspy


class SRef(gdspy.CellReference):

    def __init__(self, structure, origin, **kwargs):
        self.ref_struct = structure

        ref_cell = structure.get_cell()
        # ref_cell = None

        if kwargs:
            rot = kwargs['rotation']
            mag = kwargs['magnification']
            x_ref = kwargs['x_reflection']
        else:
            rot = None
            mag = None
            x_ref = False

        super().__init__(ref_cell, origin=origin,
                         rotation=rot, magnification=mag,
                         x_reflection=x_ref, ignore_missing=False)

    def __str__(self):
        # if isinstance(self.ref_cell, gdspy.Cell):
        #     name = self.ref_cell.name
        # else:
        #     name = self.ref_cell

        name = self.ref_struct.name

        return ("Yuna -> SRef (\"{0}\", at ({1[0]}, {1[1]}), rotation {2}, "
                "magnification {3}, reflection {4})").format(
                    name, self.origin, self.rotation, self.magnification,
                    self.x_reflection)

    def get(self):
        return gdspy.CellReference(
            self.ref_cell, 
            self.origin,
            self.rotation,
            self.magnification,
            self.x_reflection,
        )
