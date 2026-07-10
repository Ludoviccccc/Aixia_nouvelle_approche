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
            max_cycle = 120,
            ):
        self.num_banks = num_banks
        self.num_addr = max_address - min_address
        self.step = step
        self.max_instructions = max_instructions
        self.max_cycle = max_cycle
    def __call__(self,program:dict):
        self.var = Var(max_instructions = self.max_instructions,
                       max_cycle = self.max_cycle)
        experiment = Experiment(self.var,
                                num_banks=self.num_banks,
                                num_addr = self.num_addr)
        experiment.load_instr(core0_inst = program,core1_inst =[])
        out = experiment.simulate(self.max_cycle)
        
        
        results =  self.var.analyze_bandwidth_per_core()
        make_empty_dict = lambda:{window:0 for window in range(self.max_cycle//self.var.bandwidth_window_size)}
        bandwidth_core0_bus = make_empty_dict() 
        bandwidth_core1_bus = make_empty_dict() 
        bandwidth_core0_ddr = make_empty_dict() 
        bandwidth_core1_ddr = make_empty_dict() 
        if 0 in results['cores']:
            for id_ in results['cores'][0]['bus']['windows']:
                bandwidth_core0_bus[id_] = results['cores'][0]['bus']['windows'][id_]['total_commands']
        if 0 in results['cores']:
            for id_ in results['cores'][0]['ddr']['windows']:
                bandwidth_core0_ddr[id_] = results['cores'][0]['ddr']['windows'][id_]['total_commands']
        if 1 in results['cores']:
            for id_ in results['cores'][1]['bus']['windows']:
                bandwidth_core1_bus[id_] = results['cores'][1]['bus']['windows'][id_]['total_commands']
        if 1 in results['cores']:
            for id_ in results['cores'][1]['ddr']['windows']:
                bandwidth_core1_ddr[id_] = results['cores'][1]['ddr']['windows'][id_]['total_commands']

        obs = {
            #'cache_hit_l1':self.var.hits['L1'],
            'bus_bandwidth_core_0':bandwidth_core0_bus,
            'bus_bandwidth_core_1':bandwidth_core1_bus,
            'ddr_bandwidth_core_0':bandwidth_core0_ddr,
            'ddr_bandwidth_core_1':bandwidth_core1_ddr,
            #'cache_hit_l2':self.var.hits['L2'],
            #'cache_misses_l1':self.var.misses['L1'],
            'cache_misses_l2':self.var.misses['L2'],
            #'time_core0':out['time_core0']
            }
        return obs
