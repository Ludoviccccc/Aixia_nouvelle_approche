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
#policy = OptimizationPolicykNN(addr_management,k=k,min_address=min_address,max_address = max_address)



bank,row = random.choice(addr_management.address2loc.available_rows)
print(f'(bank,row) = ({bank},{row})')

history = History(length_ = num_instructions)
vars_ = Var()

for _ in range(1):

    experiment = Experiment(vars_ =vars_,num_banks=num_banks,num_addr=num_addr)
    program, adjoint_program = addr_management.generate_instruction_sequence(bank,row)

    experiment.load_instr(core0_inst=program,
            core1_inst=[])
    #print(experiment.core0.inst)
    #exit()
    output = experiment.simulate(40000)
    dt = output['ddr_simpl_vec_core0']
    
    history.store({'program':{'core0':program},
                    'adjoint':{'core0':adjoint_program},
                'event':dt,
                },(bank,row))


#print_dict(adjoint_program)

print_dict(program)

print_dict(experiment.vars.events)
print_dict(experiment.vars.misses)
print_dict(experiment.vars.hits)
print('count',experiment.vars.count)
