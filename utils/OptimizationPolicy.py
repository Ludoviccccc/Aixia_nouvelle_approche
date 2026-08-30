import random
import numpy as np
import sys
sys.path.append("../")
from utils.history import History
from utils.distance import DistanceMethod
from utils.mutation import MutationInstructions
from utils.mutation2 import MutationInstructions2 
class OptimizationPolicykNN:
    def __init__(self,
                mutation_method:MutationInstructions,
                mutation_method_informed:MutationInstructions2,
                mixing_method,
                representation=None,
                k=1,
                ):
        super().__init__()
        self.mutation_method = mutation_method
        self.mutation_method_informed = mutation_method_informed
        self.mixing_method = mixing_method
        self.representation = representation
        self.k = k

    def __call__(self,goal:np.ndarray,H:History)->dict:
        '''
        Outputs candidate parameter for reaching `goal`
        '''
        closest_parameters,closest_obs = self.select_closest_parameters(goal,H) 
        if goal['type']=='precise_if':
            programs_to_mix = []
            for if_type in closest_parameters:
                if self.k>1:
                    output = self.mixing_method(closest_parameters[if_type])
                    programs_to_mix.append(output)
                else:
                    programs_to_mix.append(closest_parameters[if_type][0])
            if len(programs_to_mix)>1:
                candidate = self.mixing_method(programs_to_mix)
            else:
                if len(programs_to_mix)>=1:
                    candidate = programs_to_mix[0]
                else:
                    raise ValueError(f'closest parameters:{ closest_parameters},goal idx:{len(goal['idx'])},if_types:{closest_parameters.keys()}')
            candidate = self.mutation_method(candidate,goal)
        elif goal['type']=='behavior':
            #print(goal['goal'])
            goal = {'ddr': goal['goal'][1], 'ddr_scheduler': goal['goal'][2], 'L2_cache': goal['goal'][3], 'bus': goal['goal'][0]}
            #exit()
            programs_to_mix = closest_parameters
            candidate = self.mutation_method_informed(closest_parameters[0],goal,closest_obs[0])
        return candidate
    def feature2closest_observations(self,goal:np.ndarray,history:History)->np.ndarray:
        '''
        selects the `self.k` closest observations indices from the database to the desired goal
        using a loss function.
        '''
        closest_obs = {}
        if goal['type'] =='precise_if':
            for elem in goal['goal']:
                if_type = elem[0] 
                goal_elem = elem[2].reshape((-1,1))# (D,1)
                min_ = elem[3]['min']
                max_ = elem[3]['max']
                denominator = max_ - min_
                denominator = denominator.reshape((-1,1))
                denominator[denominator==0]=1
                features = history.as_tab(if_type) #(D,Nb of found if)
                out = np.sum(((goal_elem - features)/denominator)**2,axis=0)
                #idx_elem = np.argsort(np.sum((goal_elem-features)**2,axis=0)) #(D,Nb of found if)
                idx_elem = np.argsort(out) #(D,Nb of found if)
                obs = [{key:history.memory_observation[elem[0]][key][id_] if key in history.memory_observation[elem[0]] else [] for key in history.memory_observation[elem[0]].index} for id_ in idx_elem[:self.k]]
                if len(goal['idx'])>0:
                    idx_elem = [history.memory_observation[if_type].columns[j] for j in idx_elem if history.memory_observation[if_type].columns[j] in goal['idx']]
                else:
                    idx_elem = [history.memory_observation[if_type].columns[j] for j in idx_elem]
                closest_obs[elem[0]] = {'idx':idx_elem[:self.k],'obs':obs}
            return closest_obs
        elif goal['type']=="behavior":
            features = history.memory_components
            idx_elem = np.argsort(np.sum((goal['goal']-features)**2,axis=0))[:self.k] #(D,Nb of found if)
            return idx_elem
        else:
            features = history.memory_micro_components
            idx_elem = np.argsort(np.sum((goal['goal']-features)**2,axis=0))[:self.k] #(D,Nb of found if)
            return idx_elem



    def select_closest_parameters(self,goal: dict,history:History)->dict:
        assert len(history)>0, "history empty"
        if goal['type']=='precise_if':
            closest_ = self.feature2closest_observations(goal,history)
            closest_codes_per_if_type = {if_type[0]:[history[id_] for id_ in closest_[if_type[0]]['idx']] for if_type in goal['goal']}

            closest_obs = []#closest_['obs']
            return closest_codes_per_if_type,closest_obs
        else:
            closest_idx = self.feature2closest_observations(goal,history)
            closest_parameters = [history[id_] for id_ in closest_idx]
            closest_obs = [{if_type:history.memory_observation[if_type][id_].to_dict() if history.memory_components[id_][j]==1 else {} for j,if_type in enumerate(history.components) } for id_ in closest_idx]
            return closest_parameters,closest_obs

