import random
import numpy as np
import sys
sys.path.append("../../")
from exploration.imgep.mutation import mutate_instruction_sequence
from exploration.history import History
from exploration.imgep.mix import mix_sequences
from exploration.test_addr import test_programs
from exploration.codegeneration import Address_Management
class OptimizationPolicykNN(test_programs):
    def __init__(self,
                address_management:Address_Management,
                k=1,
                num_mutations = 1,
                max_cycle = 60,
                min_address = 0,
                max_address = 10,
                num_parts = 2,
                segment_method=True,
                num_instructions=None,
                ):
        super().__init__()
        self.segment_method = segment_method
        self.min_address = min_address
        self.max_address = max_address
        self.num_parts = num_parts
        self.k = k
        self.num_mutations = num_mutations
        self.max_cycle = max_cycle
        self.num_instructions = num_instructions



    def __call__(self,goal:np.ndarray,H:History,stats:dict)->dict:
        '''
        Outputs candidate program  for reaching `goal`
        '''
        closest_codes = self.select_closest_codes(H,goal,stats) 
        output = {'core0':closest_codes['adjoint']['core0'],}
        if self.k>1:
            output = self.mix(output)
        output = self.light_code_mutation(output)
        #self._test_program_addr(mutated0,mutated1) 
        return output




    def mix(self,programs:list[dict]):
        mix0 = mix_sequences(programs["core0"],max_cycle=self.max_cycle,num_parts = self.num_parts)
        mix1 = mix_sequences(programs["core1"],max_cycle=self.max_cycle,num_parts = self.num_parts)
        return {'core0':[mix0],'core1':[mix1]}



    def loss(self,goal,features):
        out = np.array([np.sum(1.0*(goal!=F)) for F in features])
        return out




    def feature2closest_code(self,features:dict,signature:np.ndarray)->np.ndarray:
        '''
        selects the `self.k` closest program outcome indices from the database to the desired signature
        using the loss function `self.loss`
        '''
        d = self.loss(signature,features)
        #print('distances', d)
        idx = np.argsort(d)[:self.k]
        return idx



    def select_closest_codes(self,history:History,signature: dict,location:tuple)->dict:
        assert len(history.memory_program)>0, "history empty"
        output = {"adjoint": {"core0":[]}}
        #print(f"pointer for loc {location}:{history.pointer[location]}")
        features = history.event[location][:history.pointer[location]]
        #print('features shape', features.shape)
        idx = self.feature2closest_code(features,signature)
        for id_ in idx:
            output["adjoint"]["core0"].append(history.memory_program_adjoint["core0"][location][id_])
        return output


    def light_code_mutation(self,program):
        mutated = mutate_instruction_sequence(program,)
