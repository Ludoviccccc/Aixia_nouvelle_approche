import pickle
import numpy  as np
from exploration.load_file import load
from diversity.diversty import Diversity
import matplotlib.pyplot as plt
import torch
from utils.representation2 import VAE,vae_training




folder = "results"
N = 10000
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

vae = VAE(content_imgep_tab.shape[1],5).to(device)
print('device', device)
dataset = torch.Tensor(content_imgep_tab).to(device)
dataset = (dataset - dataset.mean(dim=0))/dataset.var(dim=0)
vae_training(dataset,vae,n_epochs=10000,lr=1e-5)
