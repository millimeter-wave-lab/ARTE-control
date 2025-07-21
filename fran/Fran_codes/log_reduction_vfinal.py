import numpy as np
import matplotlib.pyplot as plt
import copy
from matplotlib import gridspec, cm
import os, sys
from datetime import datetime
from datetime import timedelta
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from scipy.signal import savgol_filter, medfilt
import ipdb #ipdb.set_trace()
import argparse
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.ndimage import interpolation
from scipy import signal
#import warnings

CMAP = copy.copy(cm.get_cmap("viridis"))
CMAP.set_bad(color='k')

# Y = N1/N2 = P_hot/P_cold
# Te = (T_hot-Y*T_cold)/(Y-1)

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder_name", dest="folder_name", default=None)
parser.add_argument("-l", "--log_per_img", dest="log_per_img", default=1, type=int)
parser.add_argument("-c", "--cal_time", dest="cal_time", default=1, type=float)
parser.add_argument("-ft", "--file_time", dest="file_time", default=5, type=float)
parser.add_argument("-st", "--spect_time", dest="spect_time", default=1e-2)
parser.add_argument("-d", "--decimation", dest="decimation", default=10, type=int)
parser.add_argument("-w", "--avg_win", dest="mov_avg_size", default=15, type=int)
parser.add_argument("-t", "--tails", dest="tails", default=32, type=int)
parser.add_argument("-i", "--img_folder", dest="img_folder", type=str)
parser.add_argument("-m", "--plot_misc", dest="plot_misc", action="store_true")
parser.add_argument("-pc", "--plot_clip", dest="plot_clip", action="store_true")
parser.add_argument("-ant", "--plot_antenna", dest="plot_antenna", action="store_true")

class read_10gbe_data():
    """Class to read the data comming from the 10Gbe
    """
    def __init__(self, filename):
        """ Filename: name of the file to read from
        """
        self.f = open(filename, 'rb')
        ind = self.find_first_header()
        self.f.seek(ind*4)
        size = os.path.getsize(filename)
        self.n_spect = (size-ind*4)//(2052*4)

    def find_first_header(self):
        """ Find the first header in the file bacause after the header is the first
        FFT channel.
        """
        data = np.frombuffer(self.f.read(2052*4), '>I')
        ind = np.where(data==0xaabbccdd)[0][0]
        return ind

    def get_spectra(self, number):
        """
        number  :   requested number of spectrums
        You have to be aware that you have enough data to read in the n_spect
        """
        spect = np.frombuffer(self.f.read(2052*4*number), '>I')
        spect = spect.reshape([-1, 2052])
        self.n_spect -= number
        spectra = spect[:,4:]
        header = spect[:,:4]
        ##change even and odd channels (bug from the fpga..)
        even = spectra[:,::2]
        odd = spectra[:,1::2]
        spectra = np.array((odd, even))
        spectra = np.swapaxes(spectra.T, 0,1)
        spectra = spectra.reshape((-1,2048))
        spectra = spectra.astype(float)
        return spectra, header


    def get_complete(self):
        """
        read the complete data, be carefull on the sizes of your file
        """
        data, header = self.get_spectra(self.n_spect)
        return data, header

    def close_file(self):
        self.f.close()

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





def get_image_data_temperature(filenames,cal_time=1,spect_time=1e-2,file_time=5 ,decimation=1,
        win_size=32,tails=32, temperature=True):
    """
    filenames   :   list with the names of the plots
    cal_time    :   calibration time at the begining of each file
    spect_time  :   time between two spectra
    file_time   :   complete time of each file in minutes
    tails       :
    temperature :   Return the data in temperature relative to the hot source
    """
    sample = read_10gbe_data(filenames[0])
    sample_spect, header = sample.get_complete()
    sample.close_file()

    P = np.median(sample_spect,axis = 1)
    gradiente = np.abs(np.gradient(P))
    maxim = np.max(gradiente)
    index  = np.where(gradiente== maxim)
    index  =  index[0][0]

    hot_index = index-30
    P_hot = (np.mean(sample_spect[hot_index:hot_index+5,:],axis=0))
    P_hot = savgol_filter(P_hot, 9, 3)

    load_index = index+ 30
    P_load = (np.mean(sample_spect[load_index:load_index+5,:],axis=0))
    P_load = savgol_filter(P_load, 9, 3)


    flags, baseline_load = get_baseline(P_load)

    spect_size = int(file_time*60/spect_time-tails)
    spect_size2 = int(file_time*60/spect_time-tails-100)
    data = np.zeros([len(filenames)*spect_size//decimation, int(flags.shape[0])])

    data_new = np.zeros([len(filenames)*spect_size//decimation, int(flags.shape[0])])

    bases = np.zeros((len(filenames), 2048))
    clip = np.zeros(len(filenames)*spect_size//decimation, dtype=bool)

    for i in range(0, len(filenames)):
        sample = read_10gbe_data(filenames[i])
        sample_spect, header = sample.get_complete()
        sample.close_file()

        P = np.median(sample_spect,axis = 1)
        gradiente = np.abs(np.gradient(P))
        maxim = np.max(gradiente)
        index  = np.where(gradiente== maxim)
        index  =  index[0][0]

        hot_index = index-30
        P_hot = (np.mean(sample_spect[hot_index:hot_index+5,:],axis=0))
        P_hot = savgol_filter(P_hot, 9, 3)

        load_index = index+ 30
        P_load = (np.mean(sample_spect[load_index:load_index+5,:],axis=0))
        P_load = savgol_filter(P_load, 9, 3)

        flags, baseline_load = get_baseline(P_load)
        bases[i,:] = baseline_load

        t_load = 290 #temp amb
        ENR_ns = (14.85+14.74)/2. #dB
        t_hot = 10**((ENR_ns-7.8/2)/10.)*t_load+t_load # revisar descuento de perdidas  #temp ns on

        t_rx = (t_hot*P_load -t_load*P_hot)/(P_hot-P_load)

        aux = sample_spect[:spect_size,:]
        aux = (aux/P_load)*(t_rx+t_load)-t_rx

        dec_size = aux.shape[0]//decimation
        aux = aux[:dec_size*decimation,:].reshape([-1, decimation, aux.shape[1]])
        aux = np.mean(aux.astype(float), axis=1)#(1997, 2048)

        aux = aux[100:,:] #(1897, 2048)

        data[i*(spect_size2//decimation):(i+1)*(spect_size2//decimation),flags] = aux[:,flags]#(1897, 1433) - (1997, 1433)

        #data = data[100:,:]

        mediana = (np.nanmedian(data[:,:],axis=0))
        data_new = np.subtract(data,mediana)
        data_new/= np.nanstd(data_new[:,:],axis=0)

        data_new[i*(spect_size2//decimation):(i+1)*(spect_size2//decimation),flags] = aux[:,flags]

        #ipdb.set_trace()

        #
        #data_new[i*(spect_size//decimation):(i+1)*(spect_size//decimation),flags] =data_new[i*(spect_size//decimation):(i+1)*(spect_size//decimation),flags]
        #Fin editado fran

       #now we look at the clipping
        sat = np.bitwise_and(header[:spect_size,1],2**4-1) #just take the cliping values
        sat = sat[:dec_size*decimation].reshape([-1, decimation])
        sat = np.sum(sat, axis=1)
        sat = np.invert(sat==0)
        # clip[i*((spect_size)//decimation):(i+1)*((spect_size)//decimation)] = sat


    avg_pow = np.mean(data[:,flags], axis=1)
    avg_pow = moving_average(avg_pow, win_size=win_size)



    #data_new/= np.std(data_new[100:,:],axis=0)
    #data_new/= np.std(data_new[:,:],axis=0)

    snr = np.mean(data_new[:,flags], axis=1)
    snr = moving_average(snr, win_size=win_size)

    clip = moving_average(clip, win_size=win_size)
    clip = np.invert(clip==0)

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


        name = os.path.join(img_folder,  hr_i +'_to_'+hr_f)
        print('Making 10Gbe plot')
        fig, axes = plt.subplots(2,1, sharex=True, gridspec_kw={'height_ratios': [0.2,0.8]})
        axes[0].set_title('Average power UTC'+ ' ' + hr_i+'_to_'+hr_f,fontsize=20)
        #axes[0].plot(t,snr,linewidth=1.5)
        axes[0].plot(t,avg_pow,linewidth=1.5)
        axes[0].axis(ymin =  np.median(avg_pow)-4, ymax = np.median(avg_pow)+4)
        #axes[0].vlines([1,2,3,4],np.median(avg_pow)-5, np.median(avg_pow)+5, linestyles='dashed',linewidth= 0.1, colors='grey')
        #,2,3,4]   286 ,294 ,
        axes[0].grid()
        axes[0].set_ylabel('Temperature K',fontsize=15)
        #axes[0].set_ylabel('SNR',fontsize=15)
        axes[0].tick_params(axis= 'y', labelsize=15)


        if(plot_clip):
            #find rising/falling edges
            ind = np.diff(clip.astype(int))
            ris = np.where(ind==1)[0]
            fall = np.where(ind==-1)[0]
            ##check weird cases
            if(clip[0]):
                #the first sample is already clipped
                ris = np.insert(ris,0,0)
            if(clip[-1]):
                #the last sample is clipped
                fall = np.insert(fall, len(fall), len(clip)-1)
            print("Clipping: \nrising edges: {:} , falling edges: {:}".format(len(ris), len(fall)))
            for up, down in zip(ris, fall):
                axes[0].axvspan(t[up], t[down], color='r', alpha=0.3, lw=0)


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

        del data, avg_pow, bases,flags,clip
        del fig, axes   ##maybe its faster to clean the canvas and keep the figure




if __name__ == '__main__':
    args = parser.parse_args()
    plot_folder(
            folder_name=args.folder_name,
            log_per_img=args.log_per_img,
            cal_time=args.cal_time,
            file_time=args.file_time,
            spect_time=args.spect_time,
            plot_misc=args.plot_misc,
            plot_clip=args.plot_clip,
            plot_antenna=args.plot_antenna,
            decimation=args.decimation,
            mov_avg_size=args.mov_avg_size,
            tails=args.tails,
            img_folder=args.img_folder)
