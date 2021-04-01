from components.component import Link

class River(Link):
    inflow = None
    outflow = None

    upstream = None
    # upstreamUser = None

    downstream = None
    # downstreamUser = None

    def __init__(self, name, upStream, downStream):
        self.name = name
        self.upstream = upStream
        self.downstream = downStream