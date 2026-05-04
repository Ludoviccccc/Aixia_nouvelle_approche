import sys
sys.path.append("../")
sys.path.append('../../')
sys.path.append("/../simulator")
from option1.env import Environment
from option1.history import History
#from option1.mix import mix_sequences
from option1.mutation import MutationInstructions
import random
import numpy as np
import time
class OPERATORS:
    """
    Uses randomly (and thus without knowledge of the outcome space) the sequence mixture and mutation algorithms to study their impacts on diversity.
    N: int. The experimental budget
    N_init: int. Number of experiments at random
    H: History. Buffer containing codes and signature pairs
    """
    def __init__(self,
                    mutation_method:MutationInstructions,
                    parameter_generator,
                    N:int,
                    N_init:int,
                    E:Environment,
                    history:History,
                    print_freq:int=1000,

            ):
        """
        N: int. The experimental budget
        H: History. Buffer containing codes and signature pairs
        max_l: int. Max length for of the instruction sequences
        E: Env. The environnement.
        """
        super().__init__()
        self.env = E

        self.history = history
        self.mutation_method = mutation_method
        self.parameter_generator = parameter_generator
        self.k = k


        self.N = N
        self.start = 0
        self.N_init = N_init
        self.print_freq = print_freq
    def select_codes(self)->dict:
        '''
        randomly picks a selection of k pairs of codes
        '''
        assert len(history)>0, "history empty"
        output = [] 
        features = self.history.as_tab()
        idx = random.sample(range(len(self.history)),self.k)
        for id_ in idx:
            output.append(self.history[id_])
        return output
    #def mix(self,programs:dict[dict]):
    #    mix0 = mix_sequences(programs["core0"],max_cycle=self.max_cycle,num_parts = self.num_parts    )
    #    mix1 = mix_sequences(programs["core1"],max_cycle=self.max_cycle,num_parts = self.num_parts    )
    #    return {'core0':[mix0],'core1':[mix1]}
    def light_code_mutation(self,parameter):
        mutated = self.mutation_method(parameter)
        return mutated
    def __call__(self):
        start_time = time.time()
        for i in range(self.start,self.N):
            if i%self.print_freq==0 or i==self.N-1:
                print(f'step {i}/{self.N-1}')
            if i<self.N_init:
                parameter = self.parameter_generator()
            else:
                #mix random selection of k programs
                parameters = self.select_codes()
                parameter = self.mix(parameters)
                parameter = self.light_code_mutation(parameter)
            self.history.store({"program":parameter},self.env(parameter))
        print(time.time() - start_time)
    #def take(self,sample:dict,start:int): 
    #    """Takes the ``start`` first steps from the ``sample`` dictionnary to initialize the exploration. 
    #    Then the iterator i is set to ``start`` directly
    #    """
    #    for key1 in sample['memory_perf']:
    #        for key2 in sample['memory_perf'][key1].keys():
    #            shape = sample['memory_perf'][key1][key2].shape
    #            in_ = np.zeros(shape)
    #            in_[:start] = sample['memory_perf'][key1][key2][:start]  
    #            self.history.memory_perf[key1][key2] = in_
    #    self.history.memory_program["core0"] = sample["memory_program"]["core0"][:start]
    #    self.history.memory_program["core1"] = sample["memory_program"]["core1"][:start]
    #    self.history.tab = list(sample['tabular_view'][:start])
    #    self.history.shared_resource_list = sample['shared_resource_list'][:start]
    #    self.start = start
    #    self.N_init = start
    #    self.history.j = start
