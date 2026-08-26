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
        dict_ddr_scheduler = self.dict_extractor(keys,ddr_scheduler_interference)
        attacker = {key+'_attacker':[dict_['higher_priority_requests'][0][key] if key!='type' else 1*(dict_['higher_priority_requests'][0][key]=='read')-1*(dict_['higher_priority_requests'][0][key]!='read') for dict_ in ddr_scheduler_interference] for key in keys_attacker}
        return dict_ddr_scheduler | attacker


    def extract_L2_cache_interference(self,output):
        '''extracts relevant values of shared L2 events to make an array
        '''
        keys = [
                'set_idx', 
                'tag', 
                'evicted_core_id', 
                'evicted_instr_id',
                'evicted_addr',
                'causing_core_id',
                'causing_addr',
                ]
        #values_tab = []
        events = output['cache_interferences']['L2']
        return self.dict_extractor(keys,events)

    def extract_bus_interference(self,output):
        keys = ['competing_requests']
        values_tab = []
        events = output['bus_contention']
        return self.dict_extractor(keys,events)


class Environment(ExtractValues):
    def __init__(self,
            min_address_core_0 = 0,
            max_address_core_0 = 19,
            min_address_core_1 = 0,
            max_address_core_1 = 19,
            num_banks = 8,
            max_instructions:int=100,
            step:int=10,
            max_cycle_simulation = 120,
            bandwidth_window_size:int=10,
            ):
        super().__init__()
        self.num_banks = num_banks
        self.num_addr = max_address_core_1 - min_address_core_0
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
        return dict_,self.embedding_out(dict_)
    def encod(self,dict_,minmax_dict):
        out = {}
        for key in minmax_dict:
            if minmax_dict[key][1]==minmax_dict[key][0]==0:
                if len(dict_[key]):
                    out[key] = np.array([np.array(dict_[key][0])])
                else:
                    out[key] = []
            else:
                if len(dict_[key])>0:
                    out[key] = np.zeros((minmax_dict[key][1]-minmax_dict[key][0]+1,))
                    out[key][dict_[key][0]] = 1
        return out
    def embedding_out(self,dict_):
        size= 64
        line_size= 4
        assoc = 4


        to_array = lambda encod,minmax:self._dict_to_array(encod) if len(encod[list(encod.keys())[0]])>0 else np.zeros((sum([minmax[key][1]+1 if minmax[key][0]!=minmax[key][1] else 1 for key in minmax]),))

        num_sets = (size // line_size) // assoc
        max_tag = 20 // (line_size * num_sets)
        #minmax_ddr = {'row':(0,2),'bank':(0,7),'addr':(0,20),'req_type':(0,1),'scheduled_delay': (0,0), 'core_id': (0,1)}
        minmax_ddr = {'row':(0,2),'bank':(0,7),'scheduled_delay': (0,0), 'core_id': (0,1)}
        encod_ddr = self.encod(dict_['ddr_interference'],minmax_ddr)
        encod_ddr = to_array(encod_ddr,minmax_ddr)
        minmax_ddr_scheduler = {'bank': (0,7), 'scheduled_delay': (0,0), 'core_id': (0,1), 'core_attacker': (0,1), 'type_attacker': (0,1),  'bank_attacker': (0,7), 'row_attacker': (0,2)}
        encod_ddr_scheduler = self.encod(dict_['ddr_scheduler_interference'],minmax_ddr_scheduler)

        encod_ddr_scheduler = to_array(encod_ddr_scheduler,minmax_ddr_scheduler)

        #minmax_L2 = {'set_idx': (0, num_sets), 'tag': [0, 0], 'evicted_core_id': (0, 1), 'evicted_instr_id': (0, 10), 'evicted_addr': (0,20), 'causing_core_id': (0, 1), 'causing_addr': [0,20]}
        minmax_L2 = {'set_idx': (0, num_sets), 'tag': [0, 0], 'evicted_core_id': (0, 1), 'evicted_instr_id': (0, 10), 'causing_core_id': (0, 1)}
        encod_L2 = self.encod(dict_['L2_cache_interference'],minmax_L2)
        encod_L2 = to_array(encod_L2,minmax_L2)

        if len(dict_['bus_interference']['competing_requests'])>0:
            encod_bus = np.array([dict_['bus_interference']['competing_requests'][0]]) 
        else:
            encod_bus = np.array([0])
        #print((encod_bus.shape,encod_ddr.shape,encod_ddr_scheduler.shape,encod_L2.shape))
        output = np.concatenate((encod_bus,encod_ddr,encod_ddr_scheduler,encod_L2),axis=0)
        return output
    def _dict_to_array(self,dict_):
        return np.concatenate(list(dict_.values()),axis=0)

