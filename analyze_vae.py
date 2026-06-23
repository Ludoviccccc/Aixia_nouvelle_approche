import pickle
import numpy  as np
from exploration.load_file import load
from diversity.diversty import Diversity
import matplotlib.pyplot as plt
folder = "results"
N = 10000
k=1
address_x = 5
print_freq = 1000
name_imgep = f'{folder}/imgep_N_{N}_k_{k}'
name_random = f'{folder}/random_expl_N_{N}'
content_imgep = load(name_imgep)
content_imgep_tab = content_imgep['numpy_view']
content_random = load(name_random)
content_random_tab = content_random['numpy_view']
dim_out = 40
min_tab = np.zeros((dim_out,))
max_tab = np.ones((dim_out,))*10
min_tab[-1] = 0
#max_tab[-1] = 300

from option1.representation2 import VAE,vae_training

import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

vae = VAE(content_imgep_tab.shape[1],5).to(device)
import torch
print('device', device)
dataset = torch.Tensor(content_imgep_tab).to(device)
print(sum(dataset[:,-1]))
print(dataset.min(dim=0)[0].shape)
dataset = (dataset - dataset.min(dim=0)[0])/(1+dataset.max(dim=0)[0] - dataset.min(dim=0)[0])
vae_training(dataset,vae,n_epochs=10000,lr=1e-5)
