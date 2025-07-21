import numpy as np
import matplotlib.pyplot as plt
import os, sys
from log_red_V2 import *
# import ipdb #ipdb.set_trace()

# path = '/home/roach/seba/ARTE-control/log_Exp_sin_Flags/logs'
path = '/home/roach/seba/ARTE-control/logger_2vuelo_drone/logs'
logs = os.listdir(path)
logs.sort()

for i in range(len(logs)):
    s = read_10gbe_data(path +'/'+logs[i])
    spect,header = s.get_complete()

    adc0 = header[:,1]
    adc1 = header[:,1]
    adc2 = header[:,1]
    adc3 = header[:,1]

    # and entre 1 y cada respectivo bit

    flag0 = np.bitwise_and(adc0,1)
    flag1 = np.bitwise_and(adc1,2)/2
    flag2 = np.bitwise_and(adc2,4)/4
    flag3 = np.bitwise_and(adc3,8)/8

    fig, axes = plt.subplots(2,2, figsize = (16, 7.5))
    fig.suptitle(logs[i],fontsize=20)
    axes[0,0].plot(flag0,label = 'Antena 0')
    axes[0,1].plot(flag1,label = 'Antena 1 ')
    axes[1,0].plot(flag2,label = 'Antena 2')
    axes[1,1].plot(flag3,label = 'Antena ref ')


    axes[0,0].set_title('Antenna 0')
    axes[0,1].set_title('Antenna 1')
    axes[1,0].set_title('Antenna 2')
    axes[1,1].set_title('Antenna ref')


    # axes[0,0].axis(ymin =  30 , ymax = 75)
    # axes[0,1].axis(ymin =  30 , ymax = 75)
    # axes[1,0].axis(ymin =  30 , ymax = 75)
    # axes[1,1].axis(ymin =  30 , ymax = 75)

    axes[1,1].set_xlabel('sample')
    axes[1,0].set_xlabel('sample')

    axes[1,0].set_ylabel('sat ')
    axes[0,0].set_ylabel('sat ')

    axes[0,0].grid()
    axes[0,1].grid()
    axes[1,0].grid()
    axes[1,1].grid()


    axes[0,0].legend()
    axes[0,1].legend()
    axes[1,0].legend()
    axes[1,1].legend()

    plt.savefig('log'+logs[i]+ str(i)+'sats.png')
    plt.show()
    fig.clear()
    plt.close(fig)
