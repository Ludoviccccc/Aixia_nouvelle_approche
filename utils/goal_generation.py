import numpy as np
import sys
sys.path.append('../')
from utils.history import History
from utils.representation import Representation


from itertools import combinations

def get_all_subsets(input_list):
    subsets = []
    for r in range(len(input_list) + 1):
        # combinations() returns tuples, so we convert them to lists
        for combo in combinations(input_list, r):
            subsets.append(list(combo))
    return subsets


class GoalGenerator:
    def __init__(self,history:History,
            representation:Representation=None):
        self.history = history
        self.components = ['bus_interference',
                     'ddr_interference',
                     'ddr_scheduler_interference',
                     'L2_cache_interference']
        power_set = get_all_subsets(list(range(len(self.components))))
        self.combinations = get_all_subsets(self.components)
        self.encods = []
        self.counts = 0
        for sub in power_set:
            t = np.zeros(4)
            for id_ in sub:
                t[id_] = 1
            self.encods.append(t) 
    def probs(self):
        counts = []
        for encod in self.encods:
            nb = np.sum((encod==self.history.memory_components).sum(axis=1)==4)
            counts.append(nb)
        delta = np.array(counts) - self.counts
        self.counts = np.array(counts)
        #transf = np.exp(np.array(counts)*(-1.0))
        transf = np.exp(np.array(delta)*(-1.0))
        probs = transf/sum(transf)
        return probs
    def __call__(self):
        '''
        defines a goal for imgep.
        Inputs: 
        n:int. number of type of interference to target.
        Ouputs:tuple.
        (if_type,keys,values (ndarray))
        '''
        if np.random.binomial(1,.8):
            probs = self.probs()
            id_ = np.random.choice(range(len(self.combinations)),p=probs)
            encod = self.encods[id_]
            target_if_types = self.combinations[id_]
        else:
            n = np.random.randint(1,len(self.components))
            target_if_types = np.random.choice(list(self.history.memory_observation.keys()),n)
            encod = np.zeros(4)
            for i,if_type in enumerate(self.components):
                if if_type in target_if_types:
                    encod[i] = 1

        if np.random.binomial(1,0.0):
            target_if_type = []
        if np.random.binomial(1,.5):
            return {"type":"behavior","goal":encod}
        else:
            self.history.update_memory()
            cond = True
            idx = []
            while cond:
                goals = []
                tab = []
                for target_if_type in target_if_types:
                    features = self.history.as_tab(target_if_type)
                    min_ = features.min(axis=1)
                    max_ = features.max(axis=1)
                    try:
                        goal = np.random.randint(0.1*min_,1.0*max_+1)
                    except:
                        raise TypeError(f'type if:{target_if_type},features={features}')
                    goals.append((target_if_type,list(self.history.memory_observation[target_if_type].columns),goal))
                if encod in np.array(self.history.memory_components):
                    a = encod
                    b = self.history.memory_components
                    idx = np.where((a==b).sum(axis=1)==4)[0]
                    for id_ in idx:
                        s = 0
                        for comp in goals:
                            try:
                                if not comp[2].all()==self.history.memory_observation[comp[0]][id_].values.all():
                                    break
                                else:
                                    s+=1
                            except:
                                raise TypeError(f'if type={comp[0]} ,encod={encod} index= {self.history.memory_observation[comp[0]].columns},id_={id_}')
                        if s == len(goals):
                            cond = True # we found the goal in the history
                            break
                    if cond==True:
                        break
                    cond = False
            return {"type":"precise_if","goal":goals,"idx":idx}
    #def __call__(self):
    #    dim = np.random.randint(1,4+1)
    #    choice = np.random.choice(list(range(4)),dim)
    #    comb = np.zeros((4,))
    #    for comp in choice:
    #        comb[comp] = 1

    #    size= 64
    #    line_size= 4
    #    assoc = 4

    #    num_sets = (size // line_size) // assoc
    #    max_tag = 20 // (line_size * num_sets)

    #    minmax_ddr = {'row':(0,2),'bank':(0,7),'scheduled_delay': (0,0), 'core_id': (0,1)}
    #    goal_ddr = self.sample_minmax(minmax_ddr)

    #    minmax_ddr_scheduler = {'bank': (0,7), 'scheduled_delay': (0,0), 'core_id': (0,1), 'core_attacker': (0,1), 'type_attacker': (0,1), 'bank_attacker': (0,7), 'row_attacker': (0,2)}
    #    goal_ddr_scheduler = self.sample_minmax(minmax_ddr_scheduler)


    #    minmax_L2 = {'set_idx': (0, num_sets), 'tag': [0, 0], 'evicted_core_id': (0, 1), 'evicted_instr_id': (0, 10), 'causing_core_id': (0, 1)}
    #    goal_L2 = self.sample_minmax(minmax_L2)

    #    #self.history.memory_observation
    #    goal_bus = np.array([0])
    #    ##print((encod_bus.shape,encod_ddr.shape,encod_ddr_scheduler.shape,encod_L2.shape))
    #    output = np.concatenate((goal_bus*comb[0],goal_ddr*comb[1],goal_ddr_scheduler*comb[2],goal_L2*comb[3]),axis=0)
    #    output = {'type':'micro_components','goal':output}
    #    return output
    #def sample_minmax(self,minmax):
    #    sample = lambda minmax: [np.random.randint(minmax[key][0],minmax[key][1]+1) for key in minmax]
    #    choices = sample(minmax)
    #    out = []
    #    for i,key in enumerate(minmax):
    #        if minmax[key][0]!=minmax[key][1]:
    #            vec = np.zeros((minmax[key][1]+1,))
    #            vec[choices[i]] = 1
    #        else:
    #            vec = np.array([choices[i]])
    #        out.append(vec)
    #    out = np.concatenate(out,axis=0)
    #    return out
