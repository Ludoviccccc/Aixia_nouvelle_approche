import sys
sys.path.append('../../')
from simulator.sim3 import *
import numpy as np
import pandas as pd



class Experiment:
    def __init__(self,
        num_banks = 4,
        num_addr = 20,
            ):
        self.vars = Var()       
        self.num_banks = num_banks
        self.num_addr  = num_addr 
        self.num_rows = self.num_addr//16+1
        self.ddr_stats = {}
        self.time_values = {'core0':[0],'core1':[0]}
        # Instantiate the DDR Memory
        self.ddr_memory_physical = DDRMemory(num_banks=self.num_banks)

        # Instantiate the DDR Memory Controller, connected to the physical DDR
        self.ddr_controller = DDRMemoryController(
            self.ddr_memory_physical,
            tRCD=15,    # Row to Column Delay
            tRP=15,     # Row Precharge
            tCAS=15,    # Column Access Strobe latency
            tRC=30,     # Row Cycle time
            tWR=15,     # Write Recovery Time
            tRTP=8,     # Read to Precharge Time
            tCCD=4,# Column to Column Delay
            vars_=self.vars)     

        # Create interconnect, connected to the DDR Memory Controller
        self.interconnect = Interconnect(self.ddr_controller, delay=5, bandwidth=4,vars_=self.vars)

        # Create cache configurations
        l1_conf = {'size': 32, 'line_size': 4, 'assoc': 2}
        l2_conf = {'size': 512, 'line_size': 4, 'assoc': 16}


        # Create shared L2 Cache, connected to the Interconnect
        shared_l2 = CacheLevel("L2", core_id="anycore", memory=self.interconnect, **l2_conf,vars_=self.vars)

        self.num_set = shared_l2.num_sets 
        self._index = shared_l2._index
        #shared_l2.num_tags = shared_l2._tag(self.num_addr)
        #shared_l2.tab_miss = self.

        # Create Core-specific Multi-Level Caches, connected to the shared L2
        self.mem_core0 = MultiLevelCache(0, l1_conf, shared_l2)
        self.mem_core1 = MultiLevelCache(1, l1_conf, shared_l2)

        self.mem_core0.l1.vars = self.vars
        self.mem_core1.l1.vars = self.vars

        # Create cores
        self.core0 = Core(0, self.mem_core0,vars_=self.vars)
        self.core1 = Core(1, self.mem_core1,vars_=self.vars)
    def add_time_values(self,values:dict[list]):
        if type(values['core0'])!=type(None):
                self.time_values['core0'].append(values['core0'])
        if type(values['core1'])!=type(None):
                self.time_values['core1'].append(values['core1'])
    def add_values(self,ddr_stats):
        if type(ddr_stats)!=type(None):
            for key in ddr_stats:
                if key in self.ddr_stats and key!='completion_time':
                    self.ddr_stats[key].append(ddr_stats[key])
                elif key =='completion_time':
                    self.time_values[['core0','core1'][ddr_stats['core']]].append(ddr_stats[key])
                else:
                    self.ddr_stats[key]=[ddr_stats[key]]
    def load_instr(self, core0_inst, core1_inst):
        self.core0.load_instr(core0_inst)
        self.core1.load_instr(core1_inst)

    def simulate(self, cycles,display_stats=False):
        self.vars.global_cycle = 0
        for cycle in range(cycles):
            # /!\ All components tick at the same frequency
            time0 = self.core0.tick()
            time1 = self.core1.tick()
            self.interconnect.tick()
            ddr_stats = self.ddr_controller.tick()
            self.add_values(ddr_stats)
            self.add_time_values({'core0':time0,'core1':time1})
            self.ddr_memory_physical.tick()
            # Update global clock (shared variable)
            self.vars.global_cycle+=1

        self.cache_stats_core_0 = self.mem_core0.stats()
        self.cache_stats_core_1 = self.mem_core1.stats()
        self.reorder()
        if display_stats:
            # Report results
            print("\n--- Simulation Stats ---")
            dict0 = self.cache_stats_core_0['L1'].copy()
            dict1 = self.cache_stats_core_1['L1'].copy()
            display_dict = self.cache_stats_core_0['L2'].copy()
            del dict0['cache_miss_detailled']
            del dict1['cache_miss_detailled']
            del display_dict['cache_miss_detailled']
            print('core0',dict0)
            print('core1',dict1)
            print('shared cache L2',display_dict)
            print('ddr hits', self.hits_tab)
            print('ddr miss', self.miss_tab)
        return self.output_data()
    def reorder(self):
        pass
    def output_data(self):
        ddr_access = pd.DataFrame([])
        ddr_access['id'] = range(len(self.core0.inst))
        ddr_access['row'] = [0]*len(self.core0.inst)
        ddr_access['bank'] = [0]*len(self.core0.inst)
        ddr_access['status'] = [0]*len(self.core0.inst)
        in_ = pd.DataFrame(self.vars.access_ddr)
        ddr_access.loc[self.vars.access_ddr['id'],ddr_access.keys()] = in_[['id','row','bank','status']].values
        ddr_access.set_index('id',inplace=True)
        #print(ddr_access)
        return {
                'time_core0':max(self.time_values['core0']),
                'time_core1':max(self.time_values['core1']),
                'ddr_simpl_vec_core0':ddr_access,
                #'shared_resource_events':self.vars.shared_resource_events,
                }
