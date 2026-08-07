import sys
sys.path.append('../../')
sys.path.append('../')
from simulator.sim070726 import Var
from exploration.env.func import Experiment
import numpy as np

class ExtractValues:
    def __init__(self):
        pass
    def convert(self,features,dict_:dict):
        values = [dict_[key] if key!='req_type' else 1*(dict_[key]=='read')-1*(dict_[key]!='read') for key in features]
        return values
    def dict_extractor(self,keys,input_):
        big_dict = {key:[dict_[key] if key!='req_type' else 1*(dict_[key]=='read')-1*(dict_[key]!='read') for dict_ in input_] for key in keys}
        return big_dict
    def extract_ddr_if_array(self,output):
        '''extracts relevant values of ddr events to make an array
        remark: reads will be convert to 1 and writes will be convert to -1.
        '''
        keys = ['row','bank','addr','req_type','scheduled_delay','core_id']
        out = output['ddr_bank_conflicts']
        return self.dict_extractor(keys,out)
    def extract_ddr_scheduler_if_array(self,output):
        keys = ['bank','addr','req_type','scheduled_delay','core_id']#,'higher_priority_requests']
        keys_attacker = ['core','type','addr','bank','row']
        ddr_scheduler_interference = output['ddr_scheduler_interference']
        #values_tab = []
        #for dict_ in out:
        #    values = self.convert(keys,dict_)
        #    #values = [dict_[key] if key!='req_type' else 1*(dict_[key]=='read')-1*(dict_[key]!='read') for key in keys]
        #    instr_a = dict_['higher_priority_requests'][0]
        #    attacker_instruction_values = [instr_a[key] if key!='type' else 1*(instr_a[key]=='read')-1*(instr_a[key]!='read') for key in keys_attacker]
        #    values = values + attacker_instruction_values
        #    values_tab.append(values)
        #return values_tab,keys + keys_attacker
        dict_ddr_scheduler = self.dict_extractor(keys,ddr_scheduler_interference)
        attacker = {key+'_attacker':[dict_['higher_priority_requests'][0][key] if key!='type' else 1*(dict_['higher_priority_requests'][0][key]=='read')-1*(dict_['higher_priority_requests'][0][key]!='read') for dict_ in ddr_scheduler_interference] for key in keys_attacker}
        return dict_ddr_scheduler | attacker


    def extract_L2_cache_interference(self,output):
        '''extracts relevant values of shared L2 events to make an array
        '''
        keys = ['set_idx', 
                'tag', 
                'evicted_core_id', 
                'evicted_instr_id',
                'evicted_addr',
                'causing_core_id',
                'causing_addr',
                ]
        #values_tab = []
        events = output['cache_interferences']['L2']
        #for dict_ in events:
        #    #values = [dict_[key] if key!='req_type' else 1*(dict_[key]=='read')-1*(dict_[key]!='read') for key in keys]
        #    values = self.convert(keys,dict_)
        #    values_tab.append(values)
        #return values_tab,keys
        return self.dict_extractor(keys,events)

    def extract_bus_interference(self,output):
        keys = ['competing_requests']
        values_tab = []
        events = output['bus_contention']
        #for dict_ in events:
        #    #values = [dict_[key] if key!='req_type' else 1*(dict_[key]=='read')-1*(dict_[key]!='read') for key in keys]
        #    values = self.convert(keys,dict_)
        #    values_tab.append(values)
        #return values_tab,keys
        return self.dict_extractor(keys,events)


class Environment(ExtractValues):
    def __init__(self,
            min_address = 0,
            max_address = 19,
            num_banks = 8,
            max_instructions:int=100,
            step:int=10,
            max_cycle_simulation = 120,
            bandwidth_window_size:int=10,
            ):
        super().__init__()
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
        obs = self.var.get_interference_summary()['events']
        return obs
    def __call__(self,program:dict):
        output = self.run_experiment(program)
        dict_ = {'bus_interference':self.extract_bus_interference(output),
                 'ddr_interference':self.extract_ddr_if_array(output),
                 'ddr_scheduler_interference':self.extract_ddr_scheduler_if_array(output),
                 'L2_cache_interference':self.extract_L2_cache_interference(output),
                 }
        return dict_
