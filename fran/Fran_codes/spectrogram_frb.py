import numpy as np
import matplotlib.pyplot as plt
import copy
from matplotlib import gridspec, cm
import os, sys
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from scipy.signal import savgol_filter, medfilt
# import ipdb #ipdb.set_trace()
import argparse
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.ndimage import interpolation
from scipy import signal
#import warnings


CMAP = copy.copy(cm.get_cmap("viridis"))
CMAP.set_bad(color='k')



def identify_rfi(sample_spect):
    """
    Get the channels with RFI
    """
    #TODO: in the meanwhile we flag the DC values

    flags = np.arange(87).tolist()
    flags = flags+[1024]

    flags += (np.arange(10)+290).tolist() #1235
    flags += (np.arange(10)+225).tolist() #1270
    flags += (np.arange(10)+160).tolist() #1250

    flags += (np.arange(27)+394).tolist()
    flags += (np.arange(5)+455).tolist()
    flags += (np.arange(4)+1024).tolist()
    flags += (np.arange(25)+1135).tolist()
    flags += (np.arange(15)+1155).tolist()
    flags += (np.arange(12)+1175).tolist()
    flags += (np.arange(30)+1210).tolist()
    flags += (np.arange(16)+1275).tolist()
    flags += (np.arange(18)+1325).tolist()
    flags += (np.arange(10)+1367).tolist()
    flags += (np.arange(5)+1381).tolist()
    flags += (np.arange(40)+1420).tolist() # 1439
    flags += (np.arange(296)+1752).tolist()
    flags += (np.arange(256)+1792).tolist()

    #flags = []
    return flags

def get_baseline(sample_spect):
    """
    Obtain the base line for the receiver
    """
    flags = identify_rfi(sample_spect)
    mask = np.ones(2048, dtype=bool)
    mask[flags] = False
    base = savgol_filter(sample_spect, 9, 3) #window 9 points, local pol order 3
    base = base*mask
    return mask, base

def moving_average(data, win_size=32):
    out = np.zeros(len(data)-win_size+1)
    for i in range(len(data)-win_size+1):
        out[i] = np.mean(data[i:win_size+i])
    return out


def get_image_data_temperature(filenames,spect_time=1e-2):

        data = np.load('arr_0.npy')
        flags, baseline_load = get_baseline(data[12000,:])
        data = data[:,flags]

        data = data[100:,:]
        mediana = (np.nanmedian(data[:,:],axis=0))
        data_new = np.subtract(data,mediana)

        avg_pow = np.mean(data[:,flags], axis=1)
        avg_pow = moving_average(avg_pow)

        data_new/= np.std(data_new[100:,:],axis=0)

        snr = np.mean(data_new[:,flags], axis=1)
        snr = moving_average(snr, win_size=win_size)

        t = np.arange(len(avg_pow))*spect_time/60.*decimation #time in minutes
    return data, avg_pow, clip, t, bases,flags, data_new,snr


def plot_folder(folder_name, log_per_img=1, cal_time=1, file_time=5,spect_time=1e-2,
        plot_misc=True, decimation=1, mov_avg_size=32, tails=32, img_folder="log_img",
        plot_clip=True,plot_antenna=True):

    if(not os.path.exists(img_folder)):
        os.mkdir(img_folder)
    _log_names = os.listdir(os.path.join(folder_name, 'logs'))
    _log_names.sort()
    log_names = [os.path.join(folder_name,'logs',log) for log in _log_names]
    misc_names = [os.path.join(folder_name,'misc',log) for log in _log_names]
    freq = np.linspace(1200,1800, 2048, endpoint=False)

    n_img = len(log_names)//log_per_img
    for i in range(n_img):
        print("%i of %i"%(i+1,n_img))
        sublogs = log_names[i*log_per_img:(i+1)*log_per_img]
        data, avg_pow, clip, t, bases,flags,data_new,snr = get_image_data_temperature(sublogs,cal_time, spect_time,
                file_time, decimation, mov_avg_size, tails)
        hr_i= sublogs[0].split('/')[-1].split('.')[0]
        hr_f= sublogs[-1].split('/')[-1].split('.')[0]



        name = os.path.join(img_folder,  hr_i)
        #+'_to_'+hr_f)
        print('Making 10Gbe plot')
        fig, axes = plt.subplots(2,1, sharex=True, gridspec_kw={'height_ratios': [0.2,0.8]})
        axes[0].set_title('Average power UTC'+ ' ' + hr_i,fontsize=20)
        #+'_to_'+hr_f,fontsize=20)
        #axes[0].plot(t,snr,linewidth=1.5)
        axes[0].plot(t,avg_pow,linewidth=1.5)
        #axes[0].axis(ymin =  np.median(avg_pow)-2, ymax = np.median(avg_pow)+8)
        axes[0].grid()
        axes[0].set_ylabel('Temperature K',fontsize=15)
        #axes[0].set_ylabel('SNR',fontsize=15)
        axes[0].tick_params(axis= 'y', labelsize=15)



        data_new = data_new*flags
        data_new/= np.nanstd(data_new[:,:],axis=0)

        nan_indices = np.isnan(data_new)
        data_new[nan_indices] = 0

        plim = [1,99]
        vmin, vmax = np.nanpercentile( data_new, plim[0]), np.nanpercentile( data_new, plim[1])

        graph = axes[1].pcolormesh(t,freq , ((data_new[:len(t),::])).T, cmap = CMAP,vmax =vmax, vmin =vmin,shading='auto', rasterized=True,antialiased=True)

        axes[1].set_xlabel('Minutes',fontsize=15)
        axes[1].set_ylabel('MHz',fontsize=15)
        plt.tick_params(axis='both', labelsize=15)
        cax = fig.add_axes([axes[1].get_position().x1+0.01,axes[1].get_position().y0,0.02,axes[1].get_position().height])
        plt.tick_params(axis='both', labelsize=15)
        plt.colorbar(graph, cax=cax)
        fig.set_size_inches(15,12)
        plt.savefig(name+'_log.png',dpi=1000)
        plt.close()

        del data, avg_pow, bases,flags
        del fig, axes

