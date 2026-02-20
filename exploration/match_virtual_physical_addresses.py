import numpy as np
import random
class Address2Loc:
    '''
    makes a bridge between the set of given addresses and the location in DDR
    there exists a function that maps the set of addresses to the set of locations in the DDR
    this function is not bijective.
    '''
    def __init__(self,
            num_addr,
            num_banks = 4,
            min_address = 0,
            max_address = 20,
            ):
        self.min_address = min_address
        self.max_address = max_address
        self.num_addr = num_addr
        self.num_banks = num_banks
        self.num_rows = num_addr//16 +1
        self.ddr_loc2virt = {bank:{row:[] for row in range(self.num_rows)} for bank in range(self.num_banks)}
        self.possible_rows = []
        self._fill_addr2ddr_loc()
    def _get_bank(self, addr):
        '''outputs the bank (int) corresponding to the address 'addr'
        '''
        return addr % self.num_banks
    def _get_row(self, addr):
        '''outputs the row (int) corresponding to the address 'addr'
        '''
        return addr // 16
    def _fill_addr2ddr_loc(self):
        '''builts a map 'self.ddr_loc2virt[bank][row]->addr' from the ddr location set to the address set
        '''
        for addr in range(self.min_address,self.max_address+1):
            self.ddr_loc2virt[self._get_bank(addr)][self._get_row(addr)].append(addr)
        for bank in range(self.num_banks):
            for row in range(self.num_rows):
                self.ddr_loc2virt[bank][row] = np.unique(self.ddr_loc2virt[bank][row])
                if len(self.ddr_loc2virt[bank][row])>0:
                    self.possible_rows.append((bank,row))
    def location2rand_addr(self,bank,row):
        '''makes a random choice of address for a given location
        '''
        addr = int(random.choice(self.ddr_loc2virt[bank][row]))
        return addr
#match_ = address2loc(num_addr=40)
#print(match_.location2rand_addr(3,2))
