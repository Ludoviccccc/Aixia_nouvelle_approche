import numpy as np
import sys
sys.path.append('../')
from option1.history import History
class GoalGenerator:
    def __init__(self,history:History):
        self.history = history
    def __call__(self):
        features = self.history.as_tab()
        min_ = features.min(axis=0)
        max_ = features.max(axis=0)+1
        goal = np.random.randint(min_,max_)
        return goal
