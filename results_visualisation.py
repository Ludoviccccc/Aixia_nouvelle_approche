import sys
sys.path.append('../../')
import pickle
from exploration.env.func import Experiment, Env
from exploration.random.func import RANDOM
import numpy as np
from exploration.history import History
from visualisation.visu import plot_ddr_miss_ratio_diversity,hist_diversity_misses,hist_diversity_misses_seperate
from visualisation.visu_plotly import plot_time_diversity_plotly
from exploration.load_file import load
from visualisation.visu_total_div import plot_total_diversity, plot_diversity_hist_and_sum, diversity_for_comparaison_bin_method_time
#from visualisation.visu1 import diversity_for_comparaison_bin_method
from visualisation.plot_for_inference import diagnostic_plot
from visualisation.visu_time import scatter_vs_miss
import os
import json
if __name__=='__main__':
    with open(sys.argv[1],"rb") as f:
        config = json.load(f)
    N = config['N']
    k_list = config['k_values']
    folder = 'results' 
    os.system('mkdir images')
    images = 'images'
    excl = 'imgep raw data'

    name = f'{folder}/rand_run_{N}'
    content_rand = load(name)
    #for k in k_list:
    #    name = f'{folder}/imgep_run_{k}_{N}'
    #    content_imgep = load(name)
    #    plot_time_diversity_plotly(content_rand,content_imgep, f'{images}/time_k_{k}_plotly', show=False,title=f'diversity for time {excl} k={k}')
    #    plot_ddr_miss_ratio_diversity(content_rand['memory_perf'],content_imgep['memory_perf'],f'{images}/ddr_miss_ratio_{k}',title='Miss ratio in ddr',num_bank=4,num_row=3)

     
    #plot_diversity_hist_and_sum(content_rand,[(load(f'{folder}/imgep_run_{k}_{N}'),f'imgep k = {k}') for k in k_list],name=f'{images}/diversity_comparaison.pdf')

    #plot_diversity_hist_and_sum(content_rand,
    #        [(load(f'{folder}/imgep_run_{k}_{N}'),f'imgep k = {k}') for k in k_list]+
    #        [(load(f'{folder}/operators_run_{k}_{N}'),f'operators k = {k}') for k in k_list],
    #        name=f'{images}/diversity_comparaison.pdf')
    diagnostic_plot(name,[(f'{folder}/imgep_run_{k}_{N}',f'imgep k = {k}') for k in k_list])

#    diversity_for_comparaison_bin_method_time([(load(f'{folder}/imgep_run_{k}_{N}'),f'imgep k = {k}') for k in k_list]+[(content_rand,'random')]+[(load(f'{folder}/operators_run_{k}_{N}'),f'Operators k = {k}') for k in k_list],name=f'{images}/diversity_comparaison_histogram_seperate.pdf')
#
    hist_diversity_misses(content_rand['memory_perf'],
        [load(f'{folder}/imgep_run_{k}_{N}')['memory_perf'] for k in k_list],
        name=f"{images}/misses",
        num_row=3,
        title=f"Diveristy ddr miss ratio mutual vs isolation with N={N} iterations. b:bank, r:row",
        labels=[f'k={k}' for k in k_list]
    )
    #hist_diversity_misses_seperate(content_rand['memory_perf'],
    #    [load(f'{folder}/imgep_run_{k}_{N}')['memory_perf'] for k in k_list],
    #    name=f"{images}/misses",
    #    num_row=3,
    #    title=f"Diveristy ddr miss ratio mutual vs isolation with N={N} iterations. b:bank, r:row",
    #    labels=[f'k={k}' for k in k_list]
    #)

    #plot_total_diversity(content_rand,[(load(f'{folder}/imgep_run_{k}_{N}'),f'imgep k = {k}') for k in k_list],name=f'{images}/diversity_comparaison')

    scatter_vs_miss([(load(f'{folder}/imgep_run_{k}_{N}'),f'imgep k = {k}') for k in k_list[0:1]],name,title=None, folder="images")
    scatter_vs_miss([(load(f'{folder}/rand_run_{N}'),f'imgep k = {k}') for k in k_list[0:1]],name,title=None, folder="images")
