import random
import numpy as np
import json
import sys


from utils.codegeneration import Address_Management 
from utils.history import History
from utils.OptimizationPolicy import OptimizationPolicykNN
from utils.mutation import MutationInstructions
from utils.mutation2 import MutationInstructions2
from utils.mix_chunk import Mix_sequences_chunks
from utils.goal_generation import GoalGenerator
from utils.imgep import run_imgep,Randomexploration
from utils.env import Environment
from utils.baseline import MixBaseline

from diversity.diversty import Diversity





if __name__=='__main__':
    iterations = 1 #Nb of imgeps

    simu_params = {
    "min_address_core_0" : 0,
    "max_address_core_0" : 9,
    "min_address_core_1" : 10,
    "max_address_core_1" : 19,
    "max_instructions" : 10,
    }

    

    #Simulation parameters
    max_cycle_instructions = 60 #Maximum cycle in instructions
    max_cycle_simulation = 320
    bandwidth_window_size = 20
 
    #IMGEP parameters
    k_list = [1,2] #Number of neighbors in goal achievement strategy
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

    representation = None
    period_update_rep = None


    #optimization policy models

    mutation_method = MutationInstructions(num_mutations,**simu_params)
    mutation_method_informed = MutationInstructions2(num_mutations,**simu_params)
    mixing_method   = Mix_sequences_chunks(max_cycle=max_cycle_instructions,max_instructions = simu_params['max_instructions'])
    
    weights = None

    for k in k_list:
        for _ in range(iterations): 
            history = History(capacity=capacity,
                                unused=unused,
                                    )
            #goal generation
            goalgenerator = GoalGenerator(history,representation)

            #run_imgep(N_init=N_init,
            #        N=N,
            #        capacity=capacity,
            #        k=k,
            #        environment = environment,
            #        history=history,
            #        code_generation_method = code_generation_method,
            #        goal_generator=goalgenerator,
            #        mutation_method=mutation_method,
            #        mutation_method_informed=mutation_method,
            #        mixing_method=mixing_method,
            #        representation=representation,
            #        period_update_rep=period_update_rep,
            #        period = period,
            #        )
            #history.save_pickle(f'{folder}/imgep_non_informed_mutation_if_N_{N}_k_{k}')


            #baseline
            history_baseline = History(capacity=capacity,unused=unused)
            explorer_random = Randomexploration(N_init,environment,code_generation_method,history_baseline)
            baseline_mixing = MixBaseline(N,N_init,environment,code_generation_method,history_baseline,explorer_random,k,mixing_method,mutation_method)
            baseline_mixing()
            history_baseline.save_pickle(f'{folder}/baseline_non_informed_mutation_if_N_{N}_k_{k}')

    
    #history_rand = History(capacity=capacity,unused=unused)
    #random_explorer = Randomexploration(N,environment,code_generation_method,history_rand)
    #random_explorer()
    #history_rand.save_pickle(f'{folder}/random_detailled_if_N_{N}')



