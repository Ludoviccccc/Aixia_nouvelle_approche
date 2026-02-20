import sys
sys.path.append("../../")
sys.path.append("../")
sys.path.append("../../simulator")
sys.path.append("../../exploration/")
from exploration.env.func import Env
from exploration.history import History
from exploration.codegeneration import generate_instruction_sequence
from exploration.test_addr import test_programs
from exploration.imgep.mix import mix_sequences
from exploration.imgep.mutation import mutate_instruction_sequence
import random
import numpy as np
import time
class OPERATORS(test_programs):
    """
    Uses randomly (and thus without knowledge of the outcome space) the sequence mixture and mutation algorithms to study their impacts on diversity.
    N: int. The experimental budget
    N_init: int. Number of experiments at random
    H: History. Buffer containing codes and signature pairs
    """
    def __init__(self,
                    N:int,
                    N_init:int,
                    k:int,
                    num_parts:int,
                    num_mutations:int,
                    E:Env,
                    H:History,
                    min_address_core0 = 0 ,
                    max_address_core0 = 10,
                    min_address_core1 = 11,
                    max_address_core1 = 21,
                    num_instructions = None,
                    max_cycle:int=60,
                    print_freq:int=1000,

            ):
        """
        N: int. The experimental budget
        H: History. Buffer containing codes and signature pairs
        max_l: int. Max length for of the instruction sequences
        E: Env. The environnement.
        """
        super().__init__()
        self.start = 0
        self.env = E
        self.H = H
        self.N = N
        self.N_init = N_init
        self.k = k
        self.num_parts = num_parts
        self.num_mutations = num_mutations
        self.max_cycle = max_cycle
        self.min_address_core0 = min_address_core0
        self.max_address_core0 = max_address_core0
        self.min_address_core1 = min_address_core1
        self.max_address_core1 = max_address_core1
        self.num_instructions = num_instructions
        self.print_freq = print_freq
    def select_codes(self)->dict:
        '''
        randomly picks a selection of k pairs of codes
        '''
        assert len(self.H.memory_program)>0, "history empty"
        output = {"program": {"core0":[],"core1":[]},}
        features = self.H.as_tab()
        idx = random.sample(range(len(self.H)),self.k)
        for id_ in idx:
            output["program"]["core0"].append(self.H.memory_program["core0"][id_])
            output["program"]["core1"].append(self.H.memory_program["core1"][id_])
        return output
    def mix(self,programs:dict[dict]):
        mix0 = mix_sequences(programs["core0"],max_cycle=self.max_cycle,num_parts = self.num_parts    )
        mix1 = mix_sequences(programs["core1"],max_cycle=self.max_cycle,num_parts = self.num_parts    )
        return {'core0':[mix0],'core1':[mix1]}
    def light_code_mutation(self,programs:dict[list[dict]]):
        mutated0 = mutate_instruction_sequence(programs['core0'][0],
                        num_mutations=self.num_mutations,
                        max_cycle=self.max_cycle,
                        min_address=self.min_address_core0,
                        max_address=self.max_address_core0,
                        num_instructions=self.num_instructions)
        mutated1 = mutate_instruction_sequence(programs['core1'][0],
                        num_mutations=self.num_mutations,
                        max_cycle=self.max_cycle,
                        min_address=self.min_address_core1,
                        max_address=self.max_address_core1,
                        num_instructions=self.num_instructions)
        return {'core0':mutated0,'core1':mutated1}
    def __call__(self):
        start_time = time.time()
        for i in range(self.start,self.N):
            if i%self.print_freq==0 or i==self.N-1:
                print(f'step {i}/{self.N-1}')
            if i<self.N_init:
                code0 = generate_instruction_sequence(random.randint(1,
                                                    self.num_instructions),
                                                    max_cycle = self.max_cycle,
                                                    min_address=self.min_address_core0,
                                                    max_address = self.max_address_core0)
                code1 = generate_instruction_sequence(random.randint(1,
                                                        self.num_instructions)
                                                        ,max_cycle = self.max_cycle,
                                                        min_address=self.min_address_core1,
                                                        max_address = self.max_address_core1)
                parameter = {'core0':code0,'core1':code1}
            else:
                #mix random selection of k programs
                selection_codes = self.select_codes()
                parameter = {'core0':selection_codes['program']['core0'],
                         'core1':selection_codes['program']['core1']}
                parameter = self.mix(parameter)
                parameter = self.light_code_mutation(parameter)
            self.H.store({"program":parameter}|self.env(parameter))
        print(time.time() - start_time)
    def take(self,sample:dict,start:int): 
        """Takes the ``start`` first steps from the ``sample`` dictionnary to initialize the exploration. 
        Then the iterator i is set to ``start`` directly
        """
        for key1 in sample['memory_perf']:
            for key2 in sample['memory_perf'][key1].keys():
                shape = sample['memory_perf'][key1][key2].shape
                in_ = np.zeros(shape)
                in_[:start] = sample['memory_perf'][key1][key2][:start]  
                self.H.memory_perf[key1][key2] = in_
        self.H.memory_program["core0"] = sample["memory_program"]["core0"][:start]
        self.H.memory_program["core1"] = sample["memory_program"]["core1"][:start]
        self.H.tab = list(sample['tabular_view'][:start])
        self.H.shared_resource_list = sample['shared_resource_list'][:start]
        self.start = start
        self.N_init = start
        self.H.j = start
