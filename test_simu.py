from exploration.codegeneration import Address_Management 
from exploration.env.func import Experiment
import random
import numpy as np
from exploration.history import History
from exploration.imgep.OptimizationPolicy import OptimizationPolicykNN
from simulator.sim3 import Var

def print_dict(dict_):
    for key in dict_:
        print(key,dict_[key])

def distance_between_outcome(outcome1,outcome2):
    print('distance function')
    tab = (outcome1 != outcome2)*1.0
    print(tab)
    out = np.sum(tab.values)
    return out

cut_program = lambda program,len_: {key:program[key] for j,key in enumerate(program) if j<min(len_,len(program))}



num_addr = 40
num_banks = 4
min_address = 0
max_address = 19
num_instructions = 40
k = 3
addr_management = Address_Management(max_instructions=10,
                                    min_address=min_address,
                                    max_address=max_address,
                                    num_banks=num_banks,
                                    num_addr=num_addr,
                                    num_instructions=num_instructions)



bank,row = random.choice(addr_management.address2loc.available_rows)
print(f'(bank,row) = ({bank},{row})')


for _ in range(5):
    vars_ = Var()
    history = History(length_ = num_instructions)
    experiment = Experiment(vars_ =vars_,num_banks=num_banks,num_addr=num_addr)
    program, adjoint_program = addr_management.generate_instruction_sequence(bank,row)

    experiment.load_instr(core0_inst=program,
            core1_inst=[])


    experiment.simulate(1000)
     
    history.store({'program':{'core0':program}},
                    {'cache_info_miss':experiment.vars.misses,
                     'cache_info_hits':experiment.vars.hits
                    }
                  )



#print_dict(experiment.vars.events)
print(list(experiment.vars.misses['L2'].values()))
#print_dict(experiment.vars.hits)
print('count',experiment.vars.count)


