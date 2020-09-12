import datetime

class Component(object):
    name = None
    base_type = 'component'
    years = None # planning years
    periods = None # total planning period
    inflowTraces = None # total inflow traces
    depletionTraces = None # total demand traces

    JAN = 0
    FEB = 1
    MAR = 2
    APR = 3
    MAY = 4
    JUN = 5
    JUL = 6
    AUG = 7
    SEP = 8
    OCT = 9
    NOV = 10
    DEC = 11

    def setupPeriods(self):
        pass

class Network(Component):

    base_type = 'network'
    _node_map = {}
    nodes = []
    components = []

    def __init__(self, name):
        self.name = name

    def add_node(self, node):
        """
            Add a single node to the network
        """
        self.nodes.append(node)
        self.components.append(node)

        if node.name in self._node_map:
            raise Exception("An node with the name %s is already defined. Node names must be unique."%node.name)

        self._node_map[node.name] = node

        node.network = self

    def setupPeriods(self, periods, inflowTraces, depletionTraces):
        self.periods = periods
        self.inflowTraces = inflowTraces
        self.depletionTraces = depletionTraces


    def simulation(self):
        nodeLen = len(self.nodes)
        # for k in range (0, self.depletionTraces):
        starttime1 = datetime.datetime.now()

        for k in range(0, 1):
            for i in range (0, self.inflowTraces):
                starttime = datetime.datetime.now()
                if self.nodes[0].base_type == 'reservoir':
                    self.nodes[0].redrillflag = False
                for j in range (0, self.periods):
                    for m in range(0, nodeLen):
                        if self.nodes[m].base_type == 'reservoir':
                            self.nodes[m].simulationSinglePeriod(k,i,j)

                endtime = datetime.datetime.now()
                print("trace:"+str(i) + " time:" + str(endtime-starttime))

        endtime1 = datetime.datetime.now()
        print("total time:" + str(endtime - starttime))

class Node(Component):

    base_type = 'node'
    network = None

    def __init__(self, name, x, y, **kwargs):
        super(Node, self).__init__(name, **kwargs)

    def setupPeriods(self):
        pass

class Link (Component):

    base_type='link'
    network = None

    def setupPeriods(self):
        pass
