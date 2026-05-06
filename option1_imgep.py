import random
import numpy as np

from simulator.sim3 import Var

from option1.codegeneration import Address_Management 
from option1.history import History
from option1.OptimizationPolicy import OptimizationPolicykNN
from option1.distance import DistanceMethod
from option1.mutation import MutationInstructions
from option1.goal_generation import GoalGenerator
from option1.imgep import IMGEP
from option1.env import Environment

from exploration.env.func import Experiment

def print_dict(dict_):
    for key in dict_:
        print(key,dict_[key])



class randomexploration:
    def __init__(self,N,environment, generator,history:History):
        self.generator = generator
        self.environment = environment
        self.N = N
        self.history = history
    def __call__(self):
        for j in range(self.N):
            if j%1000==0:
                print(f'iteration j={j}')
            parameter = self.generator()
            obs = self.environment(parameter)
            self.history.store(parameter,obs)


def distance_function(goal,features):
    x = goal
    v = x-features
    out = np.sum(v**2)
    return out


if __name__=='__main__':

    num_addr = 40
    num_banks = 4
    min_address = 0
    max_address = 19
    num_instructions = 10
    capacity = 1000 
    
    #IMGEP parameters
    k = 1
    N = 10000
    N_init = 1000
    
    num_mutations = 1
    max_cycle = 60



    #Envionment class 
    environment = Environment()
    
    addr_management = Address_Management(max_instructions=10,
                                        min_address=min_address,
                                        max_address=max_address,
                                        num_banks=num_banks,
                                        num_addr=num_addr,
                                        num_instructions=num_instructions)
    #history
    history = History(length_ = num_instructions,capacity=capacity)
    #goal generation
    goalgenerator = GoalGenerator(history)

    #optimization policy models
    mutation_method = MutationInstructions(num_instructions,
                                        max_cycle,min_address,
                                        max_address,
                                        num_instructions)

    distance_method = DistanceMethod(distance_function)
    policy = OptimizationPolicykNN(mutation_method,k=k,distance_method=distance_method)



    explorer_random = randomexploration(N_init,environment,lambda: addr_management.generate_instruction_sequence()[0],history)


    explorer_imgep = IMGEP(N,N_init,environment,history,goalgenerator,policy,explorer_random)

    explorer_imgep()
