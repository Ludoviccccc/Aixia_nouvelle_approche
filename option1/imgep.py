import random
import sys
sys.path.append("../")
sys.path.append("../../")

from option1.history import History
from option1.OptimizationPolicy import OptimizationPolicykNN
from option1.goal_generation import GoalGenerator



from option1.env import Environment

import time
import numpy as np
class IMGEP:
    """
    N: int. The experimental budget
    N_init: int. Number of experiments at random
    H: History. Buffer containing paramters and observations  
    G: GoalGenerator.
    Pi: OptimizationPolicy.
    """
    def __init__(self,
                N:int,
                N_init:int,
                environment:Environment,
                history:History,
                goal_generator:GoalGenerator,
                optimization_policy:OptimizationPolicykNN,
                randomexploration,
                periode:int = 1,
                print_freq:int=1000,
                ):

        self.env = environment

        self.history = history
        self.goal_generator = goal_generator
        self.optimization_policy = optimization_policy
        self.random_explor = randomexploration


        #warm-up budget
        self.N_init = N_init
        #budget:
        self.N = N
        #counter
        self.start = 0
        #update frequency
        self.periode = periode

        #print frequency
        self.print_freq = print_freq
    def __call__(self):
        start_time = time.time()
        """Performs the exploration.
        """
        if self.start==0:
            self.random_explor()
        for i in range(self.N_init,self.N):
            if i%self.print_freq==0 or i==self.N-1:
                print(f'step {i}/{self.N-1}')
            if (i-self.N_init)%self.periode==0 and i>=self.N_init:
                goal = self.goal_generator()
            parameter = self.optimization_policy(goal,self.history)
            observation = self.env(parameter)
            self.history.store(parameter,observation)
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
    #            self.H.memory_perf[key1][key2] = in_
    #    self.H.memory_program["core0"] = sample["memory_program"]["core0"][:start]
    #    self.H.tab = list(sample['tabular_view'][:start])
    #    self.start = start
    #    self.N_init = start
    #    self.H.j = start
