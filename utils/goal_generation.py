import numpy as np
import sys
sys.path.append('../')
from utils.history import History
from utils.representation import Representation
class GoalGenerator:
    def __init__(self,history:History,
            representation:Representation=None):
        self.history = history
        self.representation = representation
    def __call__(self,n:int=1):
        '''
        defines a goal for imgep.
        Inputs: 
        n:int. number of type of interference to target.
        Ouputs:tuple.
        (if_type,keys,values (ndarray))
        '''
        goals = []
        target_if_types = np.random.choice(list(self.history.memory_observation.keys()),n)
        for target_if_type in target_if_types:
            features = self.history.as_tab(target_if_type)[:-1,:]
            min_ = features.min(axis=1)
            max_ = features.max(axis=1)
            goal = np.random.randint(.1*min_,1*max_)
            goals.append((target_if_type,list(self.history.memory_observation[target_if_type].keys())[:-1],goal))
        return goals
