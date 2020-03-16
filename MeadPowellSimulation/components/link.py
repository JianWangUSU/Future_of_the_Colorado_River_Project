from pynsim import Link

class RiverSection(Link):
    """
        A simple link type with a max and min flow value.
        Nothing is currently done with this and is just a demonstration
        of how to subclass a link.
    """

    _properties = dict(
        min_flow=None,
        max_flow=None,
    )
