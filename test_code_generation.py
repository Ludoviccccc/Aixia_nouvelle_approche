from exploration.codegeneration import Address_Management 
from exploration.env.func import Env
import random

def print_dict(dict_):
    for key in dict_:
        print(key,dict_[key])


num_addr = 40
num_banks = 4
min_address = 0
max_address = 19
addr_management = Address_Management(num_instructions=None,
                                    min_address=min_address,
                                    max_address=max_address,
                                    num_banks=num_banks,
                                    num_addr=num_addr)

env_simulator = Env(cycles=400,num_banks=num_banks,num_addr=num_addr)

for j in range(1):
    print(f"trial {j}")
    bank,row = random.choice(addr_management.address2loc.available_rows)
    program, ajoint_program = addr_management.generate_instruction_sequence(bank,row)
    print_dict(ajoint_program)

output = env_simulator({'core0':program,'core1':[]})
print(output)
