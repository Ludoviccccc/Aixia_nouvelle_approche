import random
import numpy as np
import sys
sys.path.append("../")
from utils.history import History
from utils.distance import DistanceMethod
from utils.mutation import MutationInstructions
class OptimizationPolicykNN:
    def __init__(self,
                mutation_method:MutationInstructions,
                mixing_method,
                distance_method:DistanceMethod,
                representation=None,
                k=1,
                ):
        super().__init__()
        self.mutation_method = mutation_method
        self.mixing_method = mixing_method
        self.distance_method = distance_method
        self.representation = representation
        self.k = k

    def __call__(self,goal:np.ndarray,H:History)->dict:
        '''
        Outputs candidate parameter for reaching `goal`
        '''
        closest_parameters = self.select_closest_parameters(goal,H) 
        programs_to_mix = []
        for if_type in closest_parameters:
            if self.k>1:
                output = self.mixing_method(closest_parameters[if_type])
                programs_to_mix.append(output)
            else:
                programs_to_mix.append(output)
        candidate = self.mixing_method(programs_to_mix)
        return candidate

    def feature2closest_parameter(self,goal:np.ndarray,history:History)->np.ndarray:
        '''
        selects the `self.k` closest parameter outcome indices from the database to the desired goal
        using the loss function `self.loss`
        '''
        idx = {}
        for elem in goal:
            if_type = elem[0] 
            goal_elem = elem[2].reshape((-1,1))# (D,1)
            features = history.as_tab(if_type)[:-1] #(D,Nb of found if)
            idx_elem = np.argsort(np.sum((goal_elem-features)**2,axis=0)) #(D,Nb of found if)
            idx_elem = [history.memory_observation[if_type]['idx'][j] for j in idx_elem]
            idx[elem[0]] = idx_elem[:self.k]
        return idx


    def select_closest_parameters(self,goal: dict,history:History)->dict:
        assert len(history)>0, "history empty"
        idx = self.feature2closest_parameter(goal,history)
        closest_codes_per_if_type = {elem[0]:[] for elem in goal}
        for if_type in closest_codes_per_if_type:
            for id_ in idx[if_type]:
                closest_codes_per_if_type[if_type].append(history[id_])
        return closest_codes_per_if_type
