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
from simulator.sim070726 import *
import json
import sys
import time
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
    max_cycle = 60 #Maximum cycle in instructions
    max_cycle_simulation = 120 #Maximum cycle in simulation
    bandwidth_window_size = 20
   
 
    #IMGEP parameters
    capacity = 10000 #History capacity
    k = 2 #Number of neighbors in goal achievement strategy
    N = 1000 #Number of imgep iterations
    N_init = 100 #Number of warming iterations
    print_freq = 100 #print iteration step every print_freq
    num_mutations = 1 #Nb of mutations in goal achievement strategy
    address_x = None
    test_mode =  True
    size= 64
    line_size= 4 
    assoc = 4
    num_sets = (size // line_size) // assoc
    max_tag = 20 // (line_size * num_sets) 

    #Envionment class 
    environment = Environment(max_cycle_simulation = max_cycle_simulation,bandwidth_window_size = bandwidth_window_size)
    
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
        output = environment({'core0':p1['core0'],'core1':p1['core0']})
        #encod = environment.encod(output['ddr_interference'],{'row':(0,2),'bank':(0,7),'addr':(0,20),'req_type':(0,1),'scheduled_delay': (0,0), 'core_id': (0,1)})
        #encod = environment.encod(output['ddr_scheduler_interference'],{'bank': (0,7), 'addr': (0,20), 'req_type': (0,1), 'scheduled_delay': (0,0), 'core_id': (0,1), 'core_attacker': (0,1), 'type_attacker': (0,1), 'addr_attacker': (0,20), 'bank_attacker': (0,7), 'row_attacker': (0,2)})
        #encod = environment.encod(output['L2_cache_interference'],{'set_idx': (0, num_sets), 'tag': [0, 0], 'evicted_core_id': (0, 1), 'evicted_instr_id': (0, 10), 'evicted_addr': (0,20), 'causing_core_id': (0, 1), 'causing_addr': [0,20]})
        #if 'set_idx' in encod:
        #    print(output)
        #    print(encod)
        #    ll = list(encod.values())
        #    print([v.shape for v in ll])
        #    print(np.concatenate(ll,axis=0).shape)
        #    break
        start_time = time.time()
        for j in range(1000):
            p = g()
            output = environment(p)
            history.store(p,output)
        print(f'duration: {time.time() - start_time}')
        goals = goalgenerator()
        print(goalgenerator.encod_goal())
        candidate = policy(goals,history)
        #print(policy.feature2closest_observations(goals,history))
        #print(goals[0])

    else:
        #Explorer for random exploration
        explorer_random = randomexploration(N_init,environment,lambda: addr_management(address_x=address_x),history,print_freq=print_freq)


        #IMGEP explorer
        explorer_imgep = IMGEP(N,N_init,environment,history,goalgenerator,policy,explorer_random)

        #Run exploration
        explorer_imgep()
