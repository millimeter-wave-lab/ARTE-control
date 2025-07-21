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
        read the complete data, be carefull on the sizes of your file+
        """
        data, header = self.get_spectra(self.n_spect)
        return data, header

    def close_file(self):
        self.f.close()

# ipdb.set_trace()

######
######
# Medicion
path = '/home/roach/seba/ARTE-control/logger_fran_test_Lunes21NOV/logs'

logs = os.listdir(path)
logs.sort()

# ipdb.set_trace()

for i in range(len(logs)):
    s = read_10gbe_data(path +'/'+logs[i])
    d,h = s.get_complete()
    print(h)
    # h.shape()
    fig, axes = plt.subplots(2,1)
    axes[0].set_title('Headers 0xaabbcc 0,2,3')
    axes[0].plot(h[:,0], label = 'header1')
    axes[0].plot(h[:,2], label = 'header3')
    axes[0].plot(h[:,3], label = 'header4')
    axes[1].set_title('Headers 0xaabbcc 1 (flag)')
    axes[1].plot(h[:,1], label = 'header2')
    axes[0].grid()
    axes[1].grid()
    axes[0].legend()
    axes[1].legend()
    # plt.show()
    plt.savefig(str(i)+'_log.png')
    fig.clear()
    plt.close(fig)
    del h

# ipdb.set_trace()

# path = '/home/roach/seba/simulink_models/FRB_detection/ROACH2/actual/logger_test_tx_DAC_mdl_old/logs'

# path = '/home/roach/seba/simulink_models/FRB_detection/ROACH2/actual/logger_test_tx_DAC_roach_lab/logs'


# #Med roach DAC modelo antiguo
# log1 = '2022-11-10 16:06:23.644210'#
# log2 = '2022-11-10 16:11:24.836700'#
# log3 = '2022-11-10 16:16:25.976623'
# log4 = '2022-11-10 16:21:27.141489'
# log5 = '2022-11-10 16:26:28.308099'
# log6 = '2022-11-10 16:31:29.459786'
# log7 = '2022-11-10 16:36:30.636866'
# log8 = '2022-11-10 16:41:31.770844'
# log9 = '2022-11-10 16:46:33.190860'
# log10 = '2022-11-10 16:51:34.361652'


#Med roach DAC modelo antiguo
# log1 = '2022-11-10 17:57:46.505986'#
# log2 = '2022-11-10 17:59:04.163217'#
# log3 = '2022-11-10 18:04:05.344717'
# log4 = '2022-11-10 18:09:06.496069'
# log5 = '2022-11-10 18:14:07.658156'
# log6 = '2022-11-10 18:19:08.805742'
# log7 = '2022-11-10 18:24:09.967827'
# log8 = '2022-11-10 18:29:11.145402'
# log9 = '2022-11-10 18:34:12.361955'
# log10 = '2022-11-10 18:39:13.510492'
#
# log11 = '2022-11-10 18:44:14.643663'
# log12 = '2022-11-10 18:49:15.814327'
#
#
# s1 = read_10gbe_data(path +'/'+ log1)
# s2 = read_10gbe_data(path +'/'+ log2)
# s3 = read_10gbe_data(path +'/'+ log3)
# s4 = read_10gbe_data(path +'/'+ log4)
# s5 = read_10gbe_data(path +'/'+ log5)
# s6 = read_10gbe_data(path +'/'+ log6)
# s7 = read_10gbe_data(path +'/'+ log7)
# s8 = read_10gbe_data(path +'/'+ log8)
# s9 = read_10gbe_data(path +'/'+ log9)
# s10 = read_10gbe_data(path +'/'+ log10)
# s11 = read_10gbe_data(path +'/'+ log11)
# s12 = read_10gbe_data(path +'/'+ log12)



#
# d1, h1 = s1.get_complete()
# d2, h2 = s2.get_complete()
# d3, h3 = s3.get_complete()
# d4, h4 = s4.get_complete()
# d5, h5 = s5.get_complete()
# d6, h6 = s6.get_complete()
# d7, h7 = s7.get_complete()
# d8, h8 = s8.get_complete()
# d9, h9 = s9.get_complete()
# d10, h10 = s10.get_complete()
# d11, h11 = s11.get_complete()
# d12, h12 = s12.get_complete()























#
#
# #Med 13 db sin AC modelo antiguo 1,2 malos, 3 bueno
# log1 = '2022-11-10 11:23:49.722821'# sat
# log2 = '2022-11-10 11:28:50.884705'# desfase
# log3 = '2022-11-10 11:33:52.009271'# ok

# # Med 13 db sin AC modelo nuevo 1 bueno, 2 malo
# log4 = '2022-11-10 11:47:48.939240' #ok
# log5 = '2022-11-10 11:52:50.140814' #sat


# Med DAC
# log10 = '2022-11-10 15:01:39.366780'
# log11 = '2022-11-10 15:06:40.529368'
# log12 = '2022-11-10 15:11:41.708513'
# log13 = '2022-11-10 15:16:42.900660'
# log14 = '2022-11-10 15:21:44.229456'
# log15 = '2022-11-10 15:26:45.405830'
# log16 = '2022-11-10 15:31:46.601567'
# log17 = '2022-11-10 15:36:47.734954'
# log18 = '2022-11-10 15:41:48.879380'
# log19 = ''
# log20 = ''
# log21 = ''
#
#
#
#
# s1 = read_10gbe_data(log1)
# s2 = read_10gbe_data(log2)
# s3 = read_10gbe_data(log3)
#
# s4 = read_10gbe_data(log4)
# s5 = read_10gbe_data(log5)
#
#
# s10 = read_10gbe_data(log10)
# s11 = read_10gbe_data(log11)
# s12 = read_10gbe_data(log12)
# s13 = read_10gbe_data(log13)
# s14 = read_10gbe_data(log14)
# s15 = read_10gbe_data(log15)
# s16 = read_10gbe_data(log16)
# s17 = read_10gbe_data(log17)
# # s18 = read_10gbe_data(log18)
# # s19 = read_10gbe_data(log19)
# # s20 = read_10gbe_data(log20)
# # s21 = read_10gbe_data(log21)


# spectra1, header1 = s1.get_spectra(30000)
# spectra2, header2 = s2.get_spectra(30000)
# spectra3, header3 = s3.get_spectra(30000)
# spectra4, header4 = s4.get_spectra(30000)
# spectra5, header5 = s5.get_spectra(30000)
#
# d1, h1 = s1.get_complete()
# d2, h2 = s2.get_complete()
# d3, h3 = s3.get_complete()
# d4, h4 = s4.get_complete()
# d5, h5 = s5.get_complete()
#


#
#
#
# d10, h10 = s10.get_complete()
# d11, h11 = s11.get_complete()
# d12, h12 = s12.get_complete()
# d13, h13 = s13.get_complete()
# d14, h14 = s14.get_complete()
# d15, h15 = s15.get_complete()
#
# d16, h16 = s16.get_complete()
# d17, h17 = s17.get_complete()
# # d18, h18 = s18.get_complete()
# # d19, h19 = s19.get_complete()
# # d20, h20 = s20.get_complete()
# # d21, h21 = s21.get_complete()
#
#
#
#
#
#
# #
#
# ind1 = s1.find_first_header()
# ind2 = s2.find_first_header()
# ind3 = s3.find_first_header()
# ind4 = s4.find_first_header()
# ind5 = s5.find_first_header()


