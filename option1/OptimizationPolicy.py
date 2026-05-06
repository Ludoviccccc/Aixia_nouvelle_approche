import random
import numpy as np
import sys
sys.path.append("../")
from option1.history import History
from option1.distance import DistanceMethod
from option1.mutation import MutationInstructions
class OptimizationPolicykNN:
    def __init__(self,
                mutation_method:MutationInstructions,
                mixing_method,
                distance_method:DistanceMethod,
                k=1,
                ):
        super().__init__()
        self.mutation_method = mutation_method
        self.mixing_method = mixing_method
        self.distance_method = distance_method
        self.k = k

    def __call__(self,goal:np.ndarray,H:History)->dict:
        '''
        Outputs candidate parameter for reaching `goal`
        '''
        closest_parameters = self.select_closest_parameters(goal,H) 
        output = closest_parameters 
        if self.k>1:
            output = self.mixing_method(output)
        else:
            output = output[0]
        output = self.mutation_method(output)
        return output

    def feature2closest_parameter(self,goal:np.ndarray,features:dict)->np.ndarray:
        '''
        selects the `self.k` closest parameter outcome indices from the database to the desired goal
        using the loss function `self.loss`
        '''
        d = self.distance_method(goal,features)
        idx = np.argsort(d)[:self.k]
        return idx


    def select_closest_parameters(self,goal: dict,history:History)->dict:
        assert len(history)>0, "history empty"
        features = history.as_tab()
        idx = self.feature2closest_parameter(goal,features)

        output = []
        for id_ in idx:
            output.append(history[id_])
        return output
