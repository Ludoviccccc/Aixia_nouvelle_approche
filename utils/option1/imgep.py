import random
import sys
sys.path.append("../")
sys.path.append("../../")

from option1.history import History
from option1.OptimizationPolicy import OptimizationPolicykNN
from option1.goal_generation import GoalGenerator

from option1.env import Environment
from option1.representation import Representation

import time
import numpy as np
from tqdm import tqdm
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
                representation:Representation=None,
                periode_update_rep:int=None,
                ):

        assert history==randomexploration.history, "provided history class is not equalled to randomexploration's history class"
        assert history==goal_generator.history, "provided history class is not equalled to goal_generator's history class"
        if periode_update_rep!=None and representation==None:
            raise TypeError("provided refreshment periode and no representation method")
        self.env = environment
        self.representation = representation
        self.history = history
        self.goal_generator = goal_generator
        self.optimization_policy = optimization_policy
        self.random_explor = randomexploration
        self.periode_update_rep = periode_update_rep


        #warm-up budget
        self.N_init = N_init
        #budget:
        self.N = N
        #counter
        self.start = 0
        #update frequency
        self.periode = periode

    def __call__(self):
        start_time = time.time()
        """Performs the exploration.
        """
        if self.start==0:
            print('initilization')
            self.random_explor()
            if self.representation:
                self.representation.update(self.history.as_tab())
        assert len(self.history), "no element in history"
        print('start of imgep')
        for i in tqdm(range(self.N_init,self.N)):
            if (i-self.N_init)%self.periode==0 and i>=self.N_init:
                goal = self.goal_generator()
            parameter = self.optimization_policy(goal,self.history)
            observation = self.env(parameter)
            self.history.store(parameter,observation)
            if self.representation!=None and i%self.periode_update_rep==0:
                self.representation.update(self.history.as_tab())
                
        print(time.time() - start_time)

    def take(self,content,count):
        self.start = count
        self.history.take(content,count)



class Randomexploration:
    def __init__(self,N,environment, generator,history:History):
        self.generator = generator
        self.environment = environment
        self.N = N
        self.history = history
    def __call__(self):
        print('run random exploration')
        for j in tqdm(range(self.N)):
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
        representation:Representation=None,
        periode_update_rep:int=None,
        ):

    policy = OptimizationPolicykNN(mutation_method,
                                k=k,
                                distance_method=distance_method,
                                mixing_method = mixing_method,
                                representation=representation,
                                )

    #Explorer for random exploration
    explorer_random = Randomexploration(N_init,environment,code_generation_method,history)
    #IMGEP explorer
    explorer_imgep = IMGEP(N,N_init,environment,history,goal_generator,policy,explorer_random,representation=representation,periode_update_rep=periode_update_rep)

    #Run exploration
    explorer_imgep()
