class test_programs:
    def __init__(self):
        pass
    def _test_program_addr(self,program0,program1):
        for k in program0:
            if program0[k][1]>self.max_address_core0 and program0[k][1]<self.min_address_core0:
                raise NameError(f'addres {program0[k][1]} not in correct interval')
        for k in program1:
            if program1[k][1]>self.max_address_core1 or program1[k][1]<self.min_address_core1:
                raise NameError(f'addres {program1[k][1]} not in correct interval')
