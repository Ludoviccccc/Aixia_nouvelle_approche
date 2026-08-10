import numpy as np
import sys
sys.path.append('../')
from utils.history import History
from utils.representation import Representation
class GoalGenerator:
    def __init__(self,history:History,
            representation:Representation=None):
        self.history = history
        self.components = ['bus_interference',
                     'ddr_interference',
                     'ddr_scheduler_interference',
                     'L2_cache_interference']
    def __call__(self):
        '''
        defines a goal for imgep.
        Inputs: 
        n:int. number of type of interference to target.
        Ouputs:tuple.
        (if_type,keys,values (ndarray))
        '''
        n = np.random.randint(1,len(self.history.memory_observation.keys()))
        target_if_types = np.random.choice(list(self.history.memory_observation.keys()),n)
        encod = np.zeros(4)
        if np.random.binomial(1,0.5):
            for i,if_type in enumerate(self.components):
                if if_type in target_if_types:
                    encod[i] = 1
            return {"type":"behavior","goal":encod}
        else:
            goals = []
            for target_if_type in target_if_types:
                features = self.history.as_tab(target_if_type)[:-1,:]
                min_ = features.min(axis=1)
                max_ = features.max(axis=1)
                goal = np.random.randint(0,2*max_)
                goals.append((target_if_type,list(self.history.memory_observation[target_if_type].keys())[:-1],goal))
            return {"type":"precise_if","goal":goals}
