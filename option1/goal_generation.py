import numpy as np
import sys
sys.path.append('../')
from option1.history import History
from option1.representation import Representation
class GoalGenerator:
    def __init__(self,history:History,
            representation:Representation=None):
        self.history = history
        self.representation = representation
    def __call__(self):
        features = self.history.as_tab()
        if self.representation:
            features = self.representation(features)
        min_ = features.min(axis=0)
        max_ = features.max(axis=0)+1
        goal = np.random.randint(.5*min_,10*max_)
        return goal
