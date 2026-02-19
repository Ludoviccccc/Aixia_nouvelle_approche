import numpy as np
import os
import matplotlib.pyplot as plt

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
def diversity(data:[np.ndarray,np.ndarray],bins:[np.ndarray, np.ndarray]):
    H,_,_ = np.histogram2d(data[0],data[1],bins)
    divers = np.sum(H>0)
    return divers
def hist_diversity_misses(content_random, contents:list, name = None, title = None,label_algo = 'imgep',num_bank=4,num_row = 2,labels=[f'k={j}' for j in range(1,4)]):
    A_core0_rand = []
    B_core0_rand = []
    A_core1_rand = []
    B_core1_rand = []
    A_core0_imgep = [[] for j in range(len(contents))]
    A_core1_imgep = [[] for j in range(len(contents))]
    bins = np.arange(-1.0,1.0,0.05)
    for j in range(num_bank):
        for row in range(num_row):
            diversity_ratio_random0 = diversity([content_random['mutual']['miss_ratios_detailled'][:,row-1,j],  content_random['core0']['miss_ratios_detailled'][:,row-1,j]], [bins, bins])
            A_core0_rand.append(diversity_ratio_random0)
            B_core0_rand.append(f'b{j},r{row}')

            diversity_ratio_random1 = diversity([content_random['mutual']['miss_ratios_detailled'][:,row-1,j],  content_random['core1']['miss_ratios_detailled'][:,row-1,j]], [bins, bins])
            A_core1_rand.append(diversity_ratio_random1)
            B_core1_rand.append(f'b{j},r{row}')
            for j_c,content_imgep in enumerate(contents):
                diversity_ratio_imgep0 = diversity([content_imgep['mutual']['miss_ratios_detailled'][:,row-1,j],  content_imgep['core0']['miss_ratios_detailled'][:,row-1,j]], [bins, bins])
                A_core0_imgep[j_c].append(diversity_ratio_imgep0)

                diversity_ratio_imgep1 = diversity([content_imgep['mutual']['miss_ratios_detailled'][:,row-1,j],  content_imgep['core1']['miss_ratios_detailled'][:,row-1,j]], [bins, bins])
                A_core1_imgep[j_c].append(diversity_ratio_imgep1)
    fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Core 0', 'Core 1'),
    horizontal_spacing=0.1
    )
    data_hist_misses = pd.DataFrame([])
    data_hist_misses['random_core0'] = A_core0_rand
    data_hist_misses['random_core1'] = A_core1_rand
    for j in range(len(labels)):
        data_hist_misses[['k1','k2','k3'][j]+"core0"] = A_core0_imgep[j]
        data_hist_misses[['k1','k2','k3'][j]+"core1"] = A_core1_imgep[j]
    data_hist_misses["idx"] = B_core0_rand
    data_hist_misses.to_csv("data_hist_misses.csv",header = True)
    
    # Core 0 data
    for j in range(len(contents)):
        fig.add_trace(go.Bar(
            x=B_core0_rand,
            y=A_core0_imgep[j],
            name=labels[j],
            marker_color=px.colors.qualitative.Plotly[j],
            #showlegend=(j==0)  # Only show legend for first trace to avoid duplicates
        ), row=1, col=1)
    
    fig.add_trace(go.Bar(
        x=B_core0_rand,
        y=A_core0_rand,
        name='random',
        marker_color='lightgray',
        showlegend=True
    ), row=1, col=1)
    
    # Core 1 data
    for j in range(len(contents)):
        fig.add_trace(go.Bar(
            x=B_core1_rand,
            y=A_core1_imgep[j],
            name=labels[j],
            marker_color=px.colors.qualitative.Plotly[j],
            showlegend=False  # Don't show duplicate legends
        ), row=1, col=2)
    
    fig.add_trace(go.Bar(
        x=B_core1_rand,
        y=A_core1_rand,
        name='random',
        marker_color='lightgray',
        showlegend=False
    ), row=1, col=2)
    
    fig.update_layout(
        title_text=title if title else 'Diversity Comparison',
        width=2000,
        height=500,
        showlegend=True,
        template='plotly_white',
        bargap=0.1,
        font=dict(
        #family="Courier New, monospace",
        size=24,
        color="Black"
    )
    )
    
    fig.update_xaxes(title_text='core 0, bank b, row r', row=1, col=1)
    fig.update_xaxes(title_text='core 1, bank b, row r', row=1, col=2)
    fig.update_yaxes(title_text='diversity', row=1, col=1)
    fig.update_yaxes(title_text='diversity', row=1, col=2)
    
    fig.show()
    
    # Save the combined figure
    fig.write_image(name+'_both_cores.png')
    fig.write_image(name+'_both_cores.pdf')
def plot_ddr_miss_ratio_diversity(content_random:dict, content_imgep:dict = None, name = None, title = None,label_algo = 'imgep',num_bank=4,num_row = 2,show=False):
    fig, axs = plt.subplots(num_row*num_bank,4, figsize = (28,80), layout='constrained')
    fontsize = 22
    fontsize_label = 32
    fontsize3 = 22
    for j in range(num_bank):
        for row in range(num_row):
            bins = np.arange(-1.0,1.0,0.05)
            axs[num_bank*row+j,0].hist(content_imgep['mutual']['miss_ratios_detailled'][:,row,j] - content_imgep['core0']['miss_ratios_detailled'][:,row,j],bins=bins,alpha = .5, label=label_algo)
            #axs[num_bank*row+j,0].set_yscale('log')
            axs[num_bank*row+j,0].hist(content_random['mutual']['miss_ratios_detailled'][:,row,j] - content_random['core0']['miss_ratios_detailled'][:,row,j],  bins=bins,alpha = .5, label='random')
        
            axs[num_bank*row+j,0].set_xlabel('miss ratio diff',fontsize=fontsize_label)
            axs[num_bank*row+j,0].set_title(f'[b{j+1},rw{row}][(S_0,S_1)]-(S_0,)]', fontsize=fontsize)
            if row==0 and j==0:
                axs[num_bank*row+j,0].legend(fontsize=fontsize)
            else:
                axs[num_bank*row+j,0].legend()
            #axs[num_bank*row+j,0].set_yscale('log')

            axs[num_bank*row+j,1].hist(content_imgep['mutual']['miss_ratios_detailled'][:,row,j] - content_imgep['core1']['miss_ratios_detailled'][:,row,j],bins=bins,alpha = .5, label=label_algo)
            axs[num_bank*row+j,1].hist(content_random['mutual']['miss_ratios_detailled'][:,row,j] - content_random['core1']['miss_ratios_detailled'][:,row,j],  bins=bins,alpha = .5, label='random')
            axs[num_bank*row+j,1].set_xlabel('miss ratio diff', fontsize = fontsize_label)
            axs[num_bank*row+j,1].set_title(f'r[b{j+1},rw{row}][(S_0,S_1)-(,S_1)]', fontsize=fontsize)
            axs[num_bank*row+j,1].legend()
            #axs[num_bank*row+j,1].set_yscale('log')

            diversity_ratio_random = diversity([content_random['mutual']['miss_ratios_detailled'][:,row,j],  content_random['core0']['miss_ratios_detailled'][:,row,j]], [bins, bins])
            diversity_ratio_imgep = diversity([content_imgep['mutual']['miss_ratios_detailled'][:,row,j],  content_imgep['core0']['miss_ratios_detailled'][:,row,j]], [bins, bins])
            axs[num_bank*row+j,2].scatter(content_imgep['core0']['miss_ratios_detailled'][:,row,j],  content_imgep['mutual']['miss_ratios_detailled'][:,row,j],label=label_algo, alpha = .5)
            axs[num_bank*row+j,2].scatter(content_random['core0']['miss_ratios_detailled'][:,row,j],  content_random['mutual']['miss_ratios_detailled'][:,row,j],  label='random', alpha = .5)
            axs[num_bank*row+j,2].set_xlabel('miss ratio alone (S_0,)',fontsize=fontsize_label)
            axs[num_bank*row+j,2].set_ylabel('(S_0,S_1)', fontsize=fontsize_label)
            axs[num_bank*row+j,2].axline(xy1=(0, 0), slope=1, color='r', lw=2)
            axs[num_bank*row+j,2].set_title(f'bank {j+1}, row {row}, imgep:{diversity_ratio_imgep}, rand:{diversity_ratio_random}', fontsize=fontsize3)
            axs[num_bank*row+j,2].legend()
            axs[num_bank*row+j,2].set_xticks(np.linspace(0,1,11))
            axs[num_bank*row+j,2].set_yticks(np.linspace(0,1,11))
            axs[num_bank*row+j,2].grid()

            diversity_ratio_random = diversity([content_random['mutual']['miss_ratios_detailled'][:,row,j],  content_random['core1']['miss_ratios_detailled'][:,row,j]], [bins, bins])
            diversity_ratio_imgep = diversity([content_imgep['mutual']['miss_ratios_detailled'][:,row,j],  content_imgep['core1']['miss_ratios_detailled'][:,row,j]], [bins, bins])
            axs[num_bank*row+j,3].scatter(content_imgep['core1']['miss_ratios_detailled'][:,row,j],  content_imgep['mutual']['miss_ratios_detailled'][:,row,j],label=label_algo, alpha = .5)
            axs[num_bank*row+j,3].scatter(content_random['core1']['miss_ratios_detailled'][:,row,j],  content_random['mutual']['miss_ratios_detailled'][:,row,j],  label='random', alpha = .5)
            axs[num_bank*row+j,3].set_xlabel('miss ratio alone (S_1,)',fontsize=fontsize_label)
            axs[num_bank*row+j,3].set_ylabel('(S_0,S_1)', fontsize=fontsize_label)
            axs[num_bank*row+j,3].axline(xy1=(0, 0), slope=1, color='r', lw=2)
            axs[num_bank*row+j,3].set_title(f'bank {j+1}, row {row}, imgep:{diversity_ratio_imgep}, rand:{diversity_ratio_random}', fontsize=fontsize3)
            axs[num_bank*row+j,3].legend()
            axs[num_bank*row+j,3].set_xticks(np.linspace(0,1,11))
            axs[num_bank*row+j,3].set_yticks(np.linspace(0,1,11))
            axs[num_bank*row+j,3].grid()

    if title:
        fig.suptitle(title,fontsize = fontsize_label)
    if name:
        k = 0
        while os.path.isfile(f'{name}_{k}.png'):
            k+=1
        plt.savefig(f'{name}_{k}.png')
    if show:
        plt.show()
    plt.close()


def plot_time_diversity(content_random, content_imgep = None, name = None, title = None,label_algo = 'imgep',num_bank=4,num_row = 2,show=False):
    fig = plt.figure(figsize = (12,12))#, layout='constrained')

    bins = np.arange(0,max(np.max(content_imgep['core0']['time_core0']),np.max(content_imgep['mutual']['time_core0'])),5)
    diversity_time_rand = diversity([content_random['core0']['time_core0'],content_random['mutual']['time_core0']], [bins, bins])
    diversity_time_imgep = diversity([content_imgep['core0']['time_core0'],content_imgep['mutual']['time_core0']], [bins, bins])

    ax1 = plt.subplot(321)
    ax1.scatter(content_imgep['core0']['time_core0'],content_imgep['mutual']['time_core0'], label='imgep', alpha = .5)
    ax1.scatter(content_random['core0']['time_core0'],content_random['mutual']['time_core0'], label='random', alpha = .5)
    ax1.axline(xy1=(0, 0), slope=1, color='r', lw=2)
    ax1.set_xlabel('time_core0_alone')
    ax1.set_ylabel('time_core0_together')
    ax1.legend()
    ax1.set_xticks(bins,minor=True)
    ax1.set_yticks(bins,minor=True)
    ax1.grid(which='minor')
    ax1.set_title(f'imgep:{diversity_time_imgep}, rand:{diversity_time_rand}')

    bins = np.arange(0,max(np.max(content_imgep['core1']['time_core1']),np.max(content_imgep['mutual']['time_core1'])),5)
    diversity_time_rand = diversity([content_random['core1']['time_core1'],content_random['mutual']['time_core1']], [bins, bins])
    diversity_time_imgep = diversity([content_imgep['core1']['time_core1'],content_imgep['mutual']['time_core1']], [bins, bins])



    ax2 = plt.subplot(322)
    ax2.scatter(content_imgep['core1']['time_core1'],content_imgep['mutual']['time_core1'], alpha = .5, label='imgep')
    ax2.scatter(content_random['core1']['time_core1'],content_random['mutual']['time_core1'], alpha = .5, label='random')
    ax2.axline(xy1=(0, 0), slope=1, color='r', lw=2)
    ax2.set_xlabel('time_core1_alone')
    ax2.set_ylabel('time_core1_together')
    ax2.legend()
    ax2.set_xticks(bins,minor=True)
    ax2.set_yticks(bins,minor=True)
    ax2.grid(which='minor')
    ax2.set_title(f'imgep:{diversity_time_imgep}, rand:{diversity_time_rand}')


    bins_hist= np.arange(-100,100,5)
    bins = np.arange(0,100,5)
    ax3 = plt.subplot(323)
    ax3.hist(content_imgep['mutual']['time_core0'] - content_imgep['core0']['time_core0'], bins=bins_hist,alpha=.5, label='imgep')
    ax3.hist(content_random['mutual']['time_core0'] - content_random['core0']['time_core0'], bins=bins_hist,alpha=.5, label='random')
    ax3.set_xlabel('time[together] - time[alone]')
    ax3.legend()


    ax4 = plt.subplot(324)
    ax4.hist(content_imgep['mutual']['time_core1'] - content_imgep['core1']['time_core1'], bins=bins_hist,alpha=.5, label='imgep')
    ax4.hist(content_random['mutual']['time_core1'] - content_random['core1']['time_core1'], bins=bins_hist,alpha=.5, label='random')
    ax4.set_xlabel('time[together] - time[alone]')
    ax4.legend()




    ax5 = plt.subplot(313)
    bins = np.arange(0,max(np.max(content_imgep['mutual']['time_core0']),np.max(content_imgep['mutual']['time_core1'])),5)
    diversity_time_rand = diversity([content_random['mutual']['time_core0'],content_random['mutual']['time_core1']], [bins, bins])
    diversity_time_imgep = diversity([content_imgep['mutual']['time_core0'],content_imgep['mutual']['time_core1']], [bins, bins])
    ax5.scatter(content_imgep['mutual']['time_core0'],content_imgep['mutual']['time_core1'], label='imgep', alpha = .5)
    ax5.scatter(content_random['mutual']['time_core0'],content_random['mutual']['time_core1'], label='random', alpha = .5)
    ax5.set_xlabel('time_core0_together')
    ax5.set_ylabel('time_core1_together')
    ax5.legend()
    ax5.set_xticks(bins,minor=True)
    ax5.set_yticks(bins,minor=True)
    ax5.grid(which='minor')
    ax5.set_title(f'imgep:{diversity_time_imgep}, rand:{diversity_time_rand}')
    if title:
        fig.suptitle(title,fontsize = 15,y = .95)
    if name:
        k = 0
        while os.path.isfile(f'{name}_{k}.png'):
            k+=1
        plt.savefig(f'{name}_{k}.png',bbox_inches = 'tight',pad_inches = 0)
    if show:
        plt.show()
    plt.close()


def comparaison_ratios_iterations(contents:list[tuple], name = None,k = None,num_rows=2,num_banks=4):
    plt.figure()
    fig, axs = plt.subplots(num_banks*num_rows,1, figsize = (25,100), layout='constrained')

    bins = np.arange(-1.0,1.0,0.05)
    for j in range(num_banks):
        for row in range(num_rows):
            for label, content in contents:
                ll = len(content['core0']['miss_ratios_detailled'])
                diversity_ratio_core0 = [diversity([content['core0']['miss_ratios_detailled'][:k,row,j],  content['mutual']['miss_ratios_detailled'][:k,row,j]], [bins, bins]) for k in range(0,ll+1,100)]
                axs[j+row*num_banks].plot(range(0,ll+1,100),diversity_ratio_core0, label=label)
                axs[j+row*num_banks].set_xlabel('iteration',fontsize=18)
                axs[j+row*num_banks].set_ylabel('diversity',fontsize=18)
                axs[j+row*num_banks].legend()
                axs[j+row*num_banks].set_title(f'Mutual Vs Isolation bank {j},row {row}', fontsize=20)
    if name:
        plt.savefig(name+'_core0')
    plt.close()

    for j in range(num_banks):
        for row in range(num_rows):
            for label, content in contents:
                diversity_ratio_core1 = [diversity([content['core1']['miss_ratios_detailled'][:k,row,j],  content['mutual']['miss_ratios_detailled'][:k,row,j]], [bins, bins]) for k in range(0,ll+1,100)]
                axs[j+row*num_banks].plot(range(0,ll+1,100),diversity_ratio_core1, label=label)
                axs[j+row*num_banks].set_xlabel('iteration',fontsize=18)
                axs[j+row*num_banks].set_ylabel('diversity',fontsize=18)
                axs[j+row*num_banks].legend()
                axs[j+row*num_banks].set_title(f'Mutual Vs Isolation bank {j},row {row}', fontsize=20)
    if name:
        plt.savefig(name+'_core1')
    plt.close()


def diversity_time_iteration(content_random,content_imgep,title=None, folder="images"):
    count_bins = lambda content: np.arange(0,max(np.max(content['mutual']['time_core0']),np.max(content['mutual']['time_core1'])),5)
    ll = len(content_random['mutual']['time_core0'])
    bins = count_bins(content_imgep)
    plt.figure()
    diversity_time_random = [diversity([content_random['mutual']['time_core0'][:k],content_random['mutual']['time_core1'][:k]], [bins, bins]) for k in range(0,ll,100)]
    plt.plot(range(0,ll,100),diversity_time_random, label='random')

    diversity_time_imgep = [diversity([content_imgep['mutual']["time_core0"][:k],content_imgep['mutual']["time_core1"][:k]],[bins, bins]) for k in range(0,ll,100)]

    plt.plot(range(0,ll,100),diversity_time_imgep)
    plt.xlabel("iteration")
    plt.ylabel("diversity")
    if title:
        plt.title(title)
    else:
        plt.title("time")
    plt.legend(prop={'size': 19})
    if title:
        plt.savefig(f"{folder}/{title}")
    plt.close()
def diversity_time_iteration2(list_,title=None, folder="images"):
    count_bins = lambda content: np.arange(0,max(np.max(content['mutual']['time_core0']),np.max(content['mutual']['time_core1'])),5)

    plt.figure(figsize=(15,10))
    for arg in list_:
        content,label = arg[0],arg[1]
        print('label',label)
        ll = len(content['mutual']['time_core0'])
        bins = count_bins(content)
        diversity_values = [diversity([content['mutual']['time_core0'][:k],content['mutual']['time_core1'][:k]], [bins, bins]) for k in range(0,ll,100)]
        plt.plot(range(0,ll,100),diversity_values, '-o',label=label)
        plt.xlabel("iteration",fontsize=19)
        plt.ylabel("diversity",fontsize=19)
    if title:
        plt.title(title,fontsize=19)
    else:
        plt.title("time",fontsize=19)
    plt.legend(prop={'size': 19})
    if title:
        plt.savefig(f"{folder}/{title}")
    plt.show()
    plt.close()
def hist_diversity_misses_seperate(content_random, contents:list, name = None, title = None,label_algo = 'imgep',num_bank=4,num_row = 2,labels=[f'k={j}' for j in range(1,4)]):
    A_core0_rand_write = []
    B_core0_rand_write = []
    A_core1_rand_write = []
    B_core1_rand_write = []
    A_core0_rand_read = []
    B_core0_rand_read = []
    A_core1_rand_read = []
    B_core1_rand_read = []
    A_core0_imgep_read = [[] for j in range(len(contents))]
    A_core1_imgep_read = [[] for j in range(len(contents))]
    A_core0_imgep_write = [[] for j in range(len(contents))]
    A_core1_imgep_write = [[] for j in range(len(contents))]
    bins = np.arange(-1.0,1.0,0.05)
    for j in range(num_bank):
        for row in range(num_row):
            diversity_ratio_random0_read = diversity([content_random['mutual']['miss_ratios_detailled_read'][:,row,j],  content_random['core0']['miss_ratios_detailled_read'][:,row,j]], [bins, bins])
            diversity_ratio_random0_write = diversity([content_random['mutual']['miss_ratios_detailled_write'][:,row,j],  content_random['core0']['miss_ratios_detailled_write'][:,row,j]], [bins, bins])

            A_core0_rand_write.append(diversity_ratio_random0_write)
            B_core0_rand_write.append(f'b{j},r{row}')
            A_core0_rand_read.append(diversity_ratio_random0_read)
            B_core0_rand_read.append(f'b{j},r{row}')

            diversity_ratio_random1_write = diversity([content_random['mutual']['miss_ratios_detailled_write'][:,row,j],  content_random['core1']['miss_ratios_detailled_write'][:,row,j]], [bins, bins])
            diversity_ratio_random1_read = diversity([content_random['mutual']['miss_ratios_detailled_read'][:,row,j],  content_random['core1']['miss_ratios_detailled_read'][:,row,j]], [bins, bins])
            A_core1_rand_write.append(diversity_ratio_random1_write)
            B_core1_rand_write.append(f'b{j},r{row}')
            A_core1_rand_read.append(diversity_ratio_random1_read)
            B_core1_rand_read.append(f'b{j},r{row}')
            for j_c,content_imgep in enumerate(contents):
                diversity_ratio_imgep0_write = diversity([content_imgep['mutual']['miss_ratios_detailled_write'][:,row,j],  content_imgep['core0']['miss_ratios_detailled_write'][:,row,j]], [bins, bins])
                diversity_ratio_imgep0_read = diversity([content_imgep['mutual']['miss_ratios_detailled_read'][:,row,j],  content_imgep['core0']['miss_ratios_detailled_read'][:,row,j]], [bins, bins])
                A_core0_imgep_write[j_c].append(diversity_ratio_imgep0_write)
                A_core0_imgep_read[j_c].append(diversity_ratio_imgep0_read)

                diversity_ratio_imgep1_write = diversity([content_imgep['mutual']['miss_ratios_detailled_write'][:,row,j],  content_imgep['core1']['miss_ratios_detailled_write'][:,row,j]], [bins, bins])
                diversity_ratio_imgep1_read = diversity([content_imgep['mutual']['miss_ratios_detailled_read'][:,row,j],  content_imgep['core1']['miss_ratios_detailled_read'][:,row,j]], [bins, bins])
                A_core1_imgep_write[j_c].append(diversity_ratio_imgep1_write)
                A_core1_imgep_read[j_c].append(diversity_ratio_imgep1_read)

    fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Core 0', 'Core 1'),
    horizontal_spacing=0.1
    )
    
    # Core 0 data
    for j in range(len(contents)):
        fig.add_trace(go.Bar(
            x=B_core0_rand_write,
            y=A_core0_imgep_write[j],
            name=labels[j],
            marker_color=px.colors.qualitative.Plotly[j],
            #showlegend=(j==0)  # Only show legend for first trace to avoid duplicates
        ), row=1, col=1)
        fig.add_trace(go.Bar(
            x=B_core0_rand_read,
            y=A_core0_imgep_read[j],
            #name=labels[j]+'read',
            name=None,
            marker_color=px.colors.qualitative.Plotly[j],
            #showlegend=(j==0)  # Only show legend for first trace to avoid duplicates
        ), row=2, col=1)
    
    fig.add_trace(go.Bar(
        x=B_core0_rand_write,
        y=A_core0_rand_write,
        name='random',
        marker_color='lightgray',
        showlegend=True
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=B_core0_rand_read,
        y=A_core0_rand_read,
        #name='random'+'read',
        name=None,
        marker_color='lightgray',
        showlegend=True
    ), row=2, col=1)
    
    # Core 1 data
    for j in range(len(contents)):
        fig.add_trace(go.Bar(
            x=B_core1_rand_write,
            y=A_core1_imgep_write[j],
            name=labels[j],
            marker_color=px.colors.qualitative.Plotly[j],
            showlegend=False  # Don't show duplicate legends
        ), row=1, col=2)
    
        fig.add_trace(go.Bar(
            x=B_core1_rand_read,
            y=A_core1_imgep_read[j],
            name=labels[j],
            marker_color=px.colors.qualitative.Plotly[j],
            showlegend=False  # Don't show duplicate legends
        ), row=2, col=2)
    fig.add_trace(go.Bar(
        x=B_core1_rand_write,
        y=A_core1_rand_write,
        #name='random'+'write',
        name=None,
        marker_color='lightgray',
        showlegend=False
    ), row=1, col=2)
    
    fig.add_trace(go.Bar(
        x=B_core1_rand_read,
        y=A_core1_rand_read,
        name='random',
        marker_color='lightgray',
        showlegend=False
    ), row=2, col=2)

    fig.update_layout(
        title_text=title if title else 'Diversity Comparison',
        width=2000,
        height=500,
        showlegend=True,
        template='plotly_white',
        bargap=0.1
    )
    
    fig.update_xaxes(title_text='core 0, bank b, row r', row=1, col=1)
    fig.update_xaxes(title_text='core 1, bank b, row r', row=1, col=2)
    fig.update_xaxes(title_text='core 0, bank b, row r', row=2, col=1)
    fig.update_xaxes(title_text='core 1, bank b, row r', row=2, col=2)
    fig.update_yaxes(title_text='diversity read instr.', row=1, col=1)
    fig.update_yaxes(title_text='diversity read instr.', row=1, col=2)
    fig.update_yaxes(title_text='diversity write instr.', row=2, col=1)
    fig.update_yaxes(title_text='diversity write instr.', row=2, col=2)
    
    fig.show()
    
    # Save the combined figure
    fig.write_image(name+'_both_cores_type.png')
