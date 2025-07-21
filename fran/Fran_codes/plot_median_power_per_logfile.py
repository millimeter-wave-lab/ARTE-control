import numpy as np
import matplotlib.pyplot as plt
import os, sys
from log_red_V2v2f import *




#path = '/media/arte/ARTE_SATA4_8T/18_abril/logs'
#path = '/media/arte/ARTE_SATA4_8T/test_disparoV2_mount_off/logs'
path = '/media/arte/ARTE_SATA4_8T/19_abril_ac_new/logs'
logs = os.listdir(path)
logs.sort()

win_size = 10
spect_time = 1e-2
decimation = 10
file_time = 5
tails = 1
spect_size = int(file_time*60/spect_time-tails)
i = 0

plt.ion()

for i in range(len(logs)):
    sample = read_10gbe_data(path+'/'+logs[i])
    sample_spect, header = sample.get_complete()
    sample.close_file()

    P = np.median(sample_spect,axis = 1)
    plt.plot(10*np.log10(P), label = 'Power' + 'logfile'+ str(i), alpha = 0.5)
    plt.show()
    del P, sample_spect

plt.title('Comparison median power since '+ str(logs[0])+' until '+ str(logs[-1]),size=8)
plt.xlabel('Samples in time')
plt.ylabel('Power dB')
plt.xlim(0,30400)
plt.grid()
plt.legend()
#plt.show()
