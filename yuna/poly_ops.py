import pyclipper


def bool_operation(subj, clip=None, method=None, closed=True):
    """ Angusj clipping library """

    pc = pyclipper.Pyclipper()

    setattr(pc, 'StrictlySimple', True)

    if clip is not None:
        pc.AddPaths(clip, pyclipper.PT_CLIP, True)

    pc.AddPaths(subj, pyclipper.PT_SUBJECT, closed)

    subj = None
    if method == 'difference':
        subj = pc.Execute(pyclipper.CT_DIFFERENCE,
                          pyclipper.PFT_EVENODD,
                          pyclipper.PFT_EVENODD)
    elif method == 'union':
        subj = pc.Execute(pyclipper.CT_UNION,
                          pyclipper.PFT_NONZERO,
                          pyclipper.PFT_NONZERO)
    elif method == 'intersection':
        subj = pc.Execute(pyclipper.CT_INTERSECTION,
                          pyclipper.PFT_NONZERO,
                          pyclipper.PFT_NONZERO)
    elif method == 'exclusive':
        subj = pc.Execute(pyclipper.CT_XOR,
                          pyclipper.PFT_NONZERO,
                          pyclipper.PFT_NONZERO)
    else:
        raise ValueError('please specify a clipping method')

    return subj


def offset_operation(layer, size):
    """
    Apply polygon offsetting using Angusj.
    Either blow up polygons or blow it down.
    """

    pco = pyclipper.PyclipperOffset()
    pco.AddPath(layer, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)

    if size == 'down':
        return pco.Execute(-10000)[0]
    elif size == 'up':
        return pco.Execute(10.0)
    else:
        raise ValueError('please select the Offset function to use')

