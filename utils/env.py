import sys
sys.path.append('../../')
sys.path.append('../')
from simulator.sim070726 import Var
from exploration.env.func import Experiment
import numpy as np

class Environment:
    def __init__(self,
            min_address = 0,
            max_address = 19,
            num_banks = 8,
            max_instructions:int=100,
            step:int=10,
            max_cycle_simulation = 120,
            bandwidth_window_size:int=10,
            ):
        self.num_banks = num_banks
        self.num_addr = max_address - min_address
        self.step = step
        self.max_instructions = max_instructions
        self.max_cycle_simulation = max_cycle_simulation
        self.bandwidth_window_size = bandwidth_window_size
    def run_experiment(self,program:dict):
        self.var = Var(max_instructions = self.max_instructions,
                       max_cycle = self.max_cycle_simulation,
                       bandwidth_window_size = self.bandwidth_window_size)
        experiment = Experiment(self.var,
                                num_banks=self.num_banks,
                                num_addr = self.num_addr)
        experiment.load_instr(core0_inst = program['core0'],core1_inst =program['core1'])
        out = experiment.simulate(self.max_cycle_simulation)
        
        

        obs = {
            'cache_misses_l2':self.var.misses['L2'],
            'time_core0':out['time_core0']
            }
        return obs
    def __call__(self,program:dict):
        output_core0_iso = self.run_experiment({'core0':program['core0'],'core1':[]})
        output_core0_core1 = self.run_experiment(program)
        output = {}
        output['cache_misses_l2_diff'] = {key:output_core0_core1['cache_misses_l2'][key] - output_core0_iso['cache_misses_l2'][key] for key in output_core0_core1['cache_misses_l2']}


        output['time_core0_iso'] = output_core0_iso['time_core0']
        output['time_core0_core1'] = output_core0_core1['time_core0']
        return output
