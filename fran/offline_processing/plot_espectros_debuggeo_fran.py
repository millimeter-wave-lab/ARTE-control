import numpy as np
import matplotlib.pyplot as plt
import os, sys
from datetime import datetime
from datetime import timedelta
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from scipy.signal import savgol_filter, medfilt
import ipdb #ipdb.set_trace()
import argparse
from mpl_toolkits.axes_grid1 import make_axes_locatable

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
        return spectra, header

    def get_complete(self):
        """
        read the complete data, be carefull on the sizes of your file
        """
        data, header = self.get_spectra(self.n_spect)
        return data, header

    def close_file(self):
        self.f.close()

# ipdb.set_trace()

def identify_rfi(sample_spect):
    """
    Get the channels with RFI
    """
    #TODO: in the meanwhile we flag the DC values
    flags = np.arange(20).tolist()
    flags = flags+[1024]
    #flags += np.arange(85).tolist()
    #flags += np.arange(1792,2048,1).tolist()
    flags += (np.arange(27)+394).tolist()
    flags += (np.arange(8)+1020).tolist()
    flags += (np.arange(5)+1155).tolist()
    flags += (np.arange(12)+1175).tolist()
    flags += (np.arange(21)+1220).tolist()
    flags += (np.arange(16)+1275).tolist()
    flags += (np.arange(18)+1325).tolist()
    flags += (np.arange(10)+1367).tolist()
    flags += (np.arange(16)+1439).tolist()
    flags += (np.arange(2)+1830).tolist()
    flags += (np.arange(3)+2045).tolist()
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

def moving_average(data, win_size=64):
    out = np.zeros(len(data)-win_size+1)
    for i in range(len(data)-win_size+1):
        out[i] = np.mean(data[i:win_size+i])
    return out



path = '/home/roach/seba/simulink_models/FRB_detection/ROACH2/actual/offline_processing/logs_test'
logs = os.listdir(path)
logs.sort()

file_time = 5 #time log minutes
spect_time = 1e-2
spect_size = int(file_time*60/spect_time)


for i in range(len(logs)):
    s = read_10gbe_data(path +'/'+logs[i])
    spect,header = s.get_complete()

    hot_source = spect[2:52,:]
    hot_spect = np.median(hot_source,axis=0)
    sky_spect = np.mean(spect[1000::,:], axis= 0)
    flags, baseline = get_baseline(np.median(hot_source,axis=0))
    suma = np.sum(spect[2:200,:], axis = 1)
    pot = suma/198

    plt.plot(pot)
    plt.grid()
    plt.show()


    fig, axes = plt.subplots(2,1)
    axes[0].set_title('Espectro promedio carga (raw)')
    axes[0].plot(hot_spect)
    axes[1].set_title('Espectro promedio cielo (raw)')
    axes[1].plot(sky_spect)
    axes[0].grid()
    axes[1].grid()
    axes[0].legend()
    axes[1].legend()
    plt.show()




