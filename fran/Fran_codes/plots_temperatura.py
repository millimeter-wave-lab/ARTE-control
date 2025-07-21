import numpy as np
import matplotlib.pyplot as plt
import copy
from matplotlib import gridspec, cm
import os, sys
from datetime import datetime
from datetime import timedelta
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

##
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
    #peaks,_ = signal.find_peaks(gradiente,height = 1e4)
    hot_index = index-30
    P_hot = (np.mean(sample_spect[hot_index:hot_index+5,:],axis=0))
    P_hot = savgol_filter(P_hot, 9, 3)

    load_index = index+ 30
    P_load = (np.mean(sample_spect[load_index:load_index+5,:],axis=0))
    P_load = savgol_filter(P_load, 9, 3)

    flags, baseline_load = get_baseline(P_load)
    spect_size = int(file_time*60/spect_time-tails)
    bases = np.zeros((len(filenames), 2048))

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
            ##peaks,_ = signal.find_peaks(gradiente,height = 1e4)
        ##hot_index = peaks[0]+10
        ##P_hot = (np.mean(sample_spect[hot_index:hot_index+5,:],axis=0))
        ##P_hot = savgol_filter(P_hot, 9, 3)

        ##load_index = peaks[1] + 10
        ##P_load = (np.mean(sample_spect[load_index:load_index+5,:],axis=0))
        ##P_load = savgol_filter(P_load, 9, 3)


        flags, baseline_load = get_baseline(P_load)
        bases[i,:] = baseline_load

        t_load = 290 #temp amb
        ENR_ns = (14.85+14.74)/2. #dB
        t_hot = 10**((ENR_ns-7.8/2)/10.)*t_load+t_load # revisar descuento de perdidas  #temp ns on

        t_rx = (t_hot*P_load -t_load*P_hot)/(P_hot-P_load)

        return t_rx,P


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
    fig, axes = plt.subplots()
    for i in range(n_img):
        print("%i of %i"%(i+1,n_img))
        sublogs = log_names[i*log_per_img:(i+1)*log_per_img]
        t_rx = get_image_data_temperature(sublogs,cal_time, spect_time,
                file_time, decimation, mov_avg_size, tails)
        hr_i= sublogs[0].split('/')[-1].split('.')[0]
        hr_f= sublogs[-1].split('/')[-1].split('.')[0]



        #name = os.path.join(img_folder,  hr_i)
        print('Making trx plot')
        #fig, axes = plt.subplots()
        axes.set_title('Receiver noise temperature')
        #+ ' ' + hr_i,fontsize=20)
        axes.plot(freq ,t_rx,linewidth=1.5)
        axes.axis(ymin = 0, ymax =2e3)
        axes.axis(xmin = 1.25e3, xmax = 1.75e3)

        axes.set_ylabel('Temperature K',fontsize=15)
        axes.tick_params(axis= 'y', labelsize=15)
        plt.savefig(str(i)+'trx.png')
        #plt.show()
        #plt.close()

    #plt.savefig('_Trx.png')
       ##maybe its faster to clean the canvas and keep the figure
    plt.grid()
    plt.show()
    #plt.savefig('_Trx.png')



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
