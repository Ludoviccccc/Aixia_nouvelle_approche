import random
import numpy as np
import json
import sys


from utils.codegeneration import Address_Management 
from utils.history import History
from utils.OptimizationPolicy import OptimizationPolicykNN
from utils.distance import DistanceMethod
from utils.mutation import MutationInstructions
from utils.mix_interleaving import Mix_sequences_interleaved
from utils.goal_generation import GoalGenerator
from utils.imgep import run_imgep,Randomexploration
from utils.env import Environment
#from utils.representation import Representation

from diversity.diversty import Diversity


#import matplotlib.pyplot as plt
def distance_function(goal,features,weights=None):
    x = goal
    v = x-features
    if type(weights)!=type(None):
        out = np.sum(weights*(v**2),axis=1)
    else:
        out = np.sum(v**2,axis=1)
    return out



if __name__=='__main__':

    simu_params = {
    "min_address" : 0,
    "max_address" : 19,
    "max_instructions" : 50,
    }



    #Simulation parameters
    max_cycle = 60 #Maximum cycle in simulation
 
    #IMGEP parameters
    k = 1 #Number of neighbors in goal achievement strategy
    N = 10000 #Number of imgep iterations
    capacity = N #History capacity
    N_init = 1000 #Number of warming iterations
    print_freq = 100
    num_mutations = 3 #Nb of mutations in goal achievement strategy

    #address X to work on
    address_x = 5
    step = 1
    folder = 'results'

    #Envionment class 
    environment = Environment(step = step,num_banks=8,**simu_params)
    
    addr_management = Address_Management(**simu_params)
    code_generation_method = lambda: addr_management.generate_pair_instruction_sequence(address_x = address_x)
    #history, this class is used by the goal generator, explorer_random and explorer_imgep
    history = History(capacity=capacity,unused=['time_core0'])

    representation = None
    periode_update_rep = None
    #representation
    #periode_update_rep = 1000
    #representation = Representation(dim=10)

    #goal generation
    goalgenerator = GoalGenerator(history,representation)

    #optimization policy models

    mutation_method = MutationInstructions(num_mutations,**simu_params)
    mixing_method   = Mix_sequences_interleaved(max_cycle)
    
    max_tab = np.ones((60,))*10
    #max_tab[-1]  = 300
    weights = 1.0/max_tab
    distance_method = DistanceMethod(distance_function,weights=weights)

    
    run_imgep(N_init=N_init,
            N=N,
            capacity=capacity,
            k=k,
            environment = environment,
            history=history,
            code_generation_method = code_generation_method,
            goal_generator=goalgenerator,
            distance_method=distance_method,
            mutation_method=mutation_method,
            mixing_method=mixing_method,
            representation=representation,
            periode_update_rep=periode_update_rep,
            )
    history.save_pickle(f'{folder}/imgep_bandwidth_N_{N}_k_{k}')


    history_rand = History(capacity=capacity,unused=['time_core0'])
    random_explorer = Randomexploration(N,environment,code_generation_method,history_rand)
    random_explorer()
    history_rand.save_pickle(f'{folder}/random_bandwidth_expl_N_{N}')
