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

        assert history==randomexploration.history, "provided history class is not equalled to randomexploration's history class"
        assert history==goal_generator.history, "provided history class is not equalled to goal_generator's history class"
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
        assert len(self.history), "no element in history"

        for i in range(self.N_init,self.N):
            if (i+1)%self.print_freq==0 or i==self.N-1:
                print(f'step {i+1}/{self.N}')
            if (i-self.N_init)%self.periode==0 and i>=self.N_init:
                goal = self.goal_generator()
            parameter = self.optimization_policy(goal,self.history)
            observation = self.env(parameter)
            self.history.store(parameter,observation)
        print(time.time() - start_time)

    def take(self,content,count):
        self.start = count
        self.history.take(content,count)



class Randomexploration:
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


def run_imgep(N_init:int,
        N:int,
        capacity:int,
        k:int,
        environment,
        history:History,
        code_generation_method,
        goal_generator,
        distance_method,
        mutation_method,
        mixing_method,
        print_freq:int):

    policy = OptimizationPolicykNN(mutation_method,
                                k=k,
                                distance_method=distance_method,
                                mixing_method = mixing_method)

    #Explorer for random exploration
    explorer_random = Randomexploration(N_init,environment,code_generation_method,history,print_freq=print_freq)
    #IMGEP explorer
    explorer_imgep = IMGEP(N,N_init,environment,history,goal_generator,policy,explorer_random,print_freq=print_freq)

    #Run exploration
    explorer_imgep()
