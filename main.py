import random
import numpy as np
import json
import sys


from option1.codegeneration import Address_Management 
from option1.history import History
from option1.OptimizationPolicy import OptimizationPolicykNN
from option1.distance import DistanceMethod
from option1.mutation import MutationInstructions
from option1.mix_interleaving import Mix_sequences_interleaved
from option1.goal_generation import GoalGenerator
from option1.imgep import run_imgep,Randomexploration
from option1.env import Environment


from diversity.diversty import Diversity


import matplotlib.pyplot as plt
def distance_function(goal,features):
    x = goal
    v = x-features
    out = np.sum(v**2,axis=1)
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
    k = 1 #Number of neighbors in goal achievement strategy
    N = 10000 #Number of imgep iterations
    capacity = N #History capacity
    N_init = 1000 #Number of warming iterations
    print_freq = 100 #print iteration step every print_freq
    num_mutations = 3 #Nb of mutations in goal achievement strategy

    #address X to work on
    address_x = 5
    step = 2
    folder = 'results'

    #Envionment class 
    environment = Environment(step = step,num_banks=8,**simu_params)
    
    addr_management = Address_Management(**simu_params)
    code_generation_method = lambda: addr_management.generate_instruction_sequence(address_x = address_x)
    #history, this class is used by the goal generator, explorer_random and explorer_imgep
    history = History(capacity=capacity)

    #goal generation
    goalgenerator = GoalGenerator(history)

    #optimization policy models

    mutation_method = MutationInstructions(num_mutations,**simu_params)
    mixing_method   = Mix_sequences_interleaved(max_cycle)

    distance_method = DistanceMethod(distance_function)

    
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
            print_freq=print_freq)
    history.save_pickle(f'{folder}/imgep_N_{N}_k_{k}')
    dim_out = 20
    diversity_ = Diversity(min_tab = np.zeros((dim_out,)),
                            max_tab = np.ones((dim_out,))*10,
                            num_bins = 10)
    
    print(f'diversity imgep {diversity_(history.as_tab())}/10**{dim_out}')
    diversity_imgep_list = [diversity_(history.as_tab()[:print_freq*step]) for step in range(N//print_freq)]
    plt.plot(range(0,N,print_freq),diversity_imgep_list,label="imgep")

    history_rand = History(capacity=capacity)
    random_explorer = Randomexploration(N,environment,code_generation_method,history_rand,print_freq)
    random_explorer()
    history_rand.save_pickle(f'{folder}/random_expl_N_{N}')

    print(f'diversity random {diversity_(history_rand.as_tab())}/10**{dim_out}')

    diversity_random_list = [diversity_(history_rand.as_tab()[:print_freq*step]) for step in range(N//print_freq)]
    plt.plot(range(0,N,print_freq),diversity_random_list,label="random")
    plt.legend()
    plt.title('diversity over experiences')
    plt.xlabel('experience')
    plt.ylabel(f'number of bins filled out of 10**{dim_out}')
    plt.show()
