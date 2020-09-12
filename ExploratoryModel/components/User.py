from components.component import Node
import numpy as np
import pandas as pd
import os

class User(Node):
    upDepletion = None # demand above this reservoir
    downDepletion = None

    base_type = 'user'

    def __init__(self, name):
        self.name = name

    def setupPeriodsandTraces(self, periods, tracesInflow, tracesDepletion):
        self.upDepletion = np.zeros([tracesDepletion][periods])
        self.downDepletion = np.zeros([tracesDepletion][periods])

    def setupPeriodsandTraces(self):
        self.inflowTraces = self.network.inflowTraces
        self.depletionTraces = self.network.depletionTraces
        self.periods = self.network.periods