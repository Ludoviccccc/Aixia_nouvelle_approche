import random
import numpy as np
import json
import sys


from utils.codegeneration import Address_Management 
from utils.history import History
from utils.OptimizationPolicy import OptimizationPolicykNN
from utils.distance import DistanceMethod
from utils.mutation import MutationInstructions
from utils.mutation2 import MutationInstructions2
from utils.mix_interleaving import Mix_sequences_interleaved
from utils.goal_generation import GoalGenerator
from utils.imgep import run_imgep,Randomexploration
from utils.env import Environment

from diversity.diversty import Diversity


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
    "max_instructions" : 10,
    }



    #Simulation parameters
    max_cycle_instructions = 60 #Maximum cycle in instructions
    max_cycle_simulation = 320
    bandwidth_window_size = 20
 
    #IMGEP parameters
    k = 2 #Number of neighbors in goal achievement strategy
    N = 20000 #Number of imgep iterations
    capacity = N #History capacity
    N_init = 1000 #Number of warming iterations
    print_freq = 100
    num_mutations = 4 #Nb of mutations in goal achievement strategy
    chunk_size = 4
    period = 100

    #address X to work on
    address_x = None
    step = 1
    folder = 'results'

    unused=[
        'time_core0_iso',
        'time_core0_core1']




    #Envionment class 
    environment = Environment(step = step,num_banks=8,max_cycle_simulation = max_cycle_simulation,bandwidth_window_size = bandwidth_window_size,**simu_params)
    
    addr_management = Address_Management(max_cycle = max_cycle_instructions,**simu_params)
    code_generation_method = lambda: addr_management(address_x = address_x)
    #history, this class is used by the goal generator, explorer_random and explorer_imgep
    history = History(capacity=capacity,
                        unused=unused,
                            )

    representation = None
    period_update_rep = None

    #goal generation
    goalgenerator = GoalGenerator(history,representation)

    #optimization policy models

    mutation_method = MutationInstructions(num_mutations,**simu_params)
    mutation_method_informed = MutationInstructions2(num_mutations,**simu_params)
    mixing_method   = Mix_sequences_interleaved(max_cycle=max_cycle_instructions,chunk_size=chunk_size)
    
    weights = None
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
            mutation_method_informed=mutation_method_informed,
            mixing_method=mixing_method,
            representation=representation,
            period_update_rep=period_update_rep,
            period = period,
            )
    history.save_pickle(f'{folder}/imgep_detailled_if_N_{N}_k_{k}')


    history_rand = History(capacity=capacity,unused=unused)
    random_explorer = Randomexploration(N,environment,code_generation_method,history_rand)
    random_explorer()
    history_rand.save_pickle(f'{folder}/random_detailled_if_N_{N}')
