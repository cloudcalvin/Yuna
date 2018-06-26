import gdspy
import numpy


class SRef(gdspy.CellReference):

    def __init__(self, structure, origin, **kwargs):
        self.ref_struct = structure

        ref_cell = structure.get_cell()

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

    def flat_labels(self, depth=None):
        """
        Returns a list of labels created by this reference.
        Parameters
        ----------
        depth : integer or ``None``
            If not ``None``, defines from how many reference levels to retrieve
            labels from.
        Returns
        -------
        out : list of ``Label``
            List containing the labels in this cell and its references.
        """
        if self.rotation is not None:
            ct = numpy.cos(self.rotation * numpy.pi / 180.0)
            st = numpy.sin(self.rotation * numpy.pi / 180.0)
            st = numpy.array([-st, st])
        if self.x_reflection:
            xrefl = numpy.array([1, -1], dtype='int')
        if self.magnification is not None:
            mag = numpy.array([self.magnification, self.magnification])
        if self.origin is not None:
            orgn = numpy.array(self.origin)
        labels = self.ref_struct.flat_labels(depth=depth)
        for lbl in labels:
            if self.x_reflection:
                lbl.position = lbl.position * xrefl
            if self.magnification is not None:
                lbl.position = lbl.position * mag
            if self.rotation is not None:
                lbl.position = lbl.position * ct + lbl.position[::-1] * st
            if self.origin is not None:
                lbl.position = lbl.position + orgn
        return labels

    def get(self):
        return gdspy.CellReference(
            self.ref_cell,
            self.origin,
            self.rotation,
            self.magnification,
            self.x_reflection,
        )
