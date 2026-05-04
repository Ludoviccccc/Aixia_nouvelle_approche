import random
import numpy as np
import sys
sys.path.append("../")
from exploration.imgep.mutation import mutate_instruction_sequence
from option1.history import History
from exploration.imgep.mix import mix_sequences
from exploration.test_addr import test_programs
from option1.distance import DistanceMethod
from option1.mutation import MutationInstructions
class OptimizationPolicykNN(test_programs):
    def __init__(self,
            mutation_method:MutationInstructions,
                distance_method:DistanceMethod,
                k=1,
                segment_method=True,
                num_instructions=10,
                ):
        super().__init__()
        self.segment_method = segment_method
        self.mutation_method = mutation_method
        self.distance_method = distance_method
        self.k = k
        self.num_instructions = num_instructions

    def __call__(self,goal:np.ndarray,H:History)->dict:
        '''
        Outputs candidate program  for reaching `goal`
        '''
        closest_parameters = self.select_closest_parameters(goal,H) 
        output = closest_parameters 
        if self.k>1:
            output = self.mix(output)
        else:
            output = output[0]
        output = self.light_parameter_mutation(output)
        return output




    def mix(self,paramters:list[dict]):
        mix0 = mix_sequences(paramters)
        return {'core0':[mix0],'core1':[mix1]}

    def feature2closest_parameter(self,goal:np.ndarray,features:dict)->np.ndarray:
        '''
        selects the `self.k` closest program outcome indices from the database to the desired goal
        using the loss function `self.loss`
        '''
        d = self.distance_method(goal,features)
        idx = np.argsort(d)[:self.k]
        return idx


    def select_closest_parameters(self,goal: dict,history:History)->dict:
        assert len(history.memory_program)>0, "history empty"
        features = history.as_tab()
        idx = self.feature2closest_parameter(goal,features)

        output = []
        for id_ in idx:
            output.append(history[id_])
        return output


    def light_parameter_mutation(self,program):
        '''slight random mutations using the bank and row informations
        '''
        mutated = self.mutation_method(program)
        return mutated
