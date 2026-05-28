import sys
sys.path.append('../../')
sys.path.append('../')
from simulator.sim281126 import Var
from exploration.env.func import Experiment


class Environment:
    '''this environment outputs textual description of what happened for each instruction in the simulator, that is in terms of fecthing, replacements, hit, miss ...
    '''
    def __init__(self,
            min_address = 0,
            max_address = 19,
            num_banks = 8,
            max_instructions:int=100,
            step:int=10,
            ):
        self.num_banks = num_banks
        self.num_addr = max_address - min_address
        self.step = step
        self.max_instructions = max_instructions
    def __call__(self,program):
        self.var = Var(step = self.step,
                       max_instructions = self.max_instructions)
        experiment = Experiment(self.var,
                                num_banks=self.num_banks,
                                num_addr = self.num_addr)
        experiment.load_instr(core0_inst = program,core1_inst = [])
        out = experiment.simulate(400)
        
        obs = self.var.get_instruction_sequences_formatted()
        return obs
