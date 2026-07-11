import random
import numpy as np


from utils.codegeneration import Address_Management 
from utils.history import History
from utils.OptimizationPolicy import OptimizationPolicykNN
from utils.distance import DistanceMethod
from utils.mutation import MutationInstructions
from utils.mix_interleaving import Mix_sequences_interleaved
from utils.goal_generation import GoalGenerator
from utils.imgep import IMGEP
from utils.env import Environment

from exploration.env.func import Experiment

import json
import sys
def print_dict(dict_):
    for key in dict_:
        print(key,dict_[key])



class randomexploration:
    def __init__(self,N,environment, generator,history:History,print_freq:int=1000):
        self.generator = generator
        self.environment = environment
        self.N = N
        self.history = history
        self.print_freq = print_freq
    def __call__(self):
        for j in range(self.N):
            if (j+1)%self.print_freq==0:
                print(f'step {j+1}/{self.N}')
            parameter = self.generator()
            obs = self.environment(parameter)
            self.history.store(parameter,obs)


def distance_function(goal,features):
    x = goal
    v = x-features
    out = np.sum(v**2)
    return out


if __name__=='__main__':

    simu_params = {
    "min_address" : 0,
    "max_address" : 19,
    "max_instructions" : 10,
    }



    #Simulation parameters
    max_cycle = 60 #Maximum cycle in simulation
   
 
    #IMGEP parameters
    capacity = 10000 #History capacity
    k = 2 #Number of neighbors in goal achievement strategy
    N = 10000 #Number of imgep iterations
    N_init = 1000 #Number of warming iterations
    print_freq = 100 #print iteration step every print_freq
    num_mutations = 1 #Nb of mutations in goal achievement strategy
    address_x = 5
    test_mode =  True


    #Envionment class 
    environment = Environment()
    
    addr_management = Address_Management(**simu_params)

    #history, this class is used by the goal generator, explorer_random and explorer_imgep
    history = History(capacity=capacity)
    #goal generation
    goalgenerator = GoalGenerator(history)

    #optimization policy models

    mutation_method = MutationInstructions(num_mutations,**simu_params)
    mixing_method = Mix_sequences_interleaved(max_cycle,chunk_size=1)

    distance_method = DistanceMethod(distance_function)
    #Goal achievement strategy
    policy = OptimizationPolicykNN(mutation_method,
                                k=k,
                                distance_method=distance_method,
                                mixing_method = mixing_method)

    

    if test_mode:
        g = lambda: addr_management(address_x=address_x) 
        p1 = g()
        p2 = g()
        print('p1', p1)
        programs = [p1,p2]
        mixture = mixing_method(programs)
        #program = {'core0':p1,'core1':p2}
        #print('p1',p1)
        #print('p2',p2)
        #output = environment(program)
        #results = environment.var.analyze_bandwidth_per_core()
        #print(output)
        print("mixture",mixture)
        print('core 0 p1 len',len(p1['core0'].keys()))
        print('core 1 p1 len',len(p1['core1'].keys()))
        print('core0 len', len(mixture['core0'].keys()))
        print('core1 len', len(mixture['core1'].keys()))
    else:
        #Explorer for random exploration
        explorer_random = randomexploration(N_init,environment,lambda: addr_management.generate_instruction_sequence(address_x=address_x),history,print_freq=print_freq)


        #IMGEP explorer
        explorer_imgep = IMGEP(N,N_init,environment,history,goalgenerator,policy,explorer_random)

        #Run exploration
        explorer_imgep()
