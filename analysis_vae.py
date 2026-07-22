import pickle
import numpy  as np
from exploration.load_file import load
from diversity.diversty import Diversity
import matplotlib.pyplot as plt
import torch
from utils.representation2 import VAE,vae_training




folder = "results"
N = 100000
k=1
address_x = 5
max_cycle_simulat = 120
bandwidth_window_size = 20
print_freq = 1000
name_imgep = f'{folder}/imgep_bandwidth_N_{N}_k_{k}'
name_random = f'{folder}/random_bandwidth_expl_N_{N}'
content_imgep = load(name_imgep)
content_imgep_tab = content_imgep['numpy_view']
content_random = load(name_random)
content_random_tab = content_random['numpy_view']

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


feature_list = ['bus_bandwidth_core_0_diff', 'ddr_bandwidth_core_0_diff', 'cache_misses_l2_diff', 'bus_bandwidth_core_0_iso', 'bus_bandwidth_core_0_core1', 'ddr_bandwidth_core_0_iso', 'ddr_bandwidth_core_0_core1']
content_array_time  = np.array([[[content_imgep['memory_observation'][feature][n][t] for feature in feature_list] for t in range(6)] for n in range(N)])
print(content_array_time.shape)
data = content_array_time.reshape((-1,len(feature_list)))
norm = lambda data: (data - data.mean(axis=0))/data.std(axis=0)
data = torch.Tensor(norm(data)).to(device)
print('device', device)
#dataset = torch.Tensor(content_imgep_tab).to(device)
#dataset = (dataset - dataset.mean(dim=0))/dataset.var(dim=0)
vae = VAE(data.shape[1],5).to(device)
vae_training(data,vae,n_epochs=10000,lr=1e-5)
