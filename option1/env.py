import sys
sys.path.append('../../')
sys.path.append('../')
from simulator.sim3 import Var
from exploration.env.func import Experiment


class Environment:
    def __init__(self,
            num_addr = 40,
            num_banks = 8,
            ):
        self.num_banks = num_banks
        self.num_addr = num_addr
    def __call__(self,program):
        self.var = Var()
        experiment = Experiment(self.var,
                                num_banks=self.num_banks,
                                num_addr = self.num_addr)
        experiment.load_instr(core0_inst = program,core1_inst = [])
        experiment.simulate(400)
        

        obs = {
            'cache_hit_l1':self.var.hits['L1'],
            'cache_hit_l2':self.var.hits['L2'],
            'cache_misses_l1':self.var.misses['L1'],
            'cache_misses_l2':self.var.misses['L2']}
        return obs
