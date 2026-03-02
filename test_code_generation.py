from exploration.codegeneration import Address_Management 
from exploration.env.func import Experiment
import random

def print_dict(dict_):
    for key in dict_:
        print(key,dict_[key])


num_addr = 40
num_banks = 4
min_address = 0
max_address = 19
addr_management = Address_Management(max_instructions=10,
                                    min_address=min_address,
                                    max_address=max_address,
                                    num_banks=num_banks,
                                    num_addr=num_addr)

#env_simulator = Env(cycles=400,num_banks=num_banks,num_addr=num_addr)
print('available rows', addr_management.address2loc.available_rows)
experiment = Experiment(num_banks=num_banks,num_addr=num_addr)
experiment.load_instr


for j in range(4):
    #ex.clear_history()
    bank,row = random.choice(addr_management.address2loc.available_rows)
    program, ajoint_program = addr_management.generate_instruction_sequence(bank,row)
    print_dict(program)
    experiment.load_instr(core0_inst=program,core1_inst=[])
    output = experiment.simulate(400)
    print(output.keys())
exit()

for j in range(4):
    GlobalVar.clear_history()
    #print(f"trial {j}")
    bank,row = random.choice(addr_management.address2loc.available_rows)
    print('row',row)
    print('bank',bank)
    program, ajoint_program = addr_management.generate_instruction_sequence(bank,row)
    #print_dict(ajoint_program)
    print_dict(program)
    output = env_simulator({'core0':program,'core1':[]})
    print(output['core0'])
    break
