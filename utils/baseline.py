import random
import sys
sys.path.append("../")
sys.path.append("../../")

from utils.history import History
from utils.env import Environment
from utils.mutation import MutationInstructions
from utils.imgep import Randomexploration
import time
import numpy as np
from tqdm import tqdm
class MixBaseline:
    """
    N: int. Experimental budget.
    N_init: int. Number of experiments at random.
    environment: Environment to explore.
    H: History. Buffer containing paramters and observations.
    randomexploration: random exploration class.
    k:int. Number of programs to mix
    mixing_method: MutationInstructions2. Method for mixing programs.
    """
    def __init__(self,
                N:int,
                N_init:int,
                environment:Environment,
                generator,
                history:History,
                randomexploration,
                k:int,
                mixing_method,
                mutation_method,
                ):

        assert history==randomexploration.history, "provided history class is not equalled to randomexploration's history class"
        self.env = environment
        self.k = k
        self.generator = generator
        self.history = history
        self.random_explor = randomexploration
        self.mixing_method = mixing_method
        self.mutation_method = mutation_method


        #warm-up budget
        self.N_init = N_init
        #budget:
        self.N = N
        #counter
        self.start = 0

    def __call__(self):
        start_time = time.time()
        """Performs the exploration.
        """
        if self.start==0:
            print('initilization')
            self.random_explor()
        assert len(self.history), "no element in history"
        for i in tqdm(range(self.N_init,self.N)):
            parameter = self.mixing_method([self.generator() for _ in range(self.k)])
            parameter = self.mutation_method(parameter,None)
            observation = self.env(parameter)
            self.history.store(parameter,observation)
                
        print(time.time() - start_time)

    def take(self,content,count):
        self.start = count
        self.history.take(content,count)
