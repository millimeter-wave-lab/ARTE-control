import numpy as np
import matplotlib.pyplot as plt
import calandigital as calan
import os
import sys, time
sys.path.append('codes')
import utils, control
import corr
import csv
import ipdb #ipdb.set_trace()

roach_ip ='10.17.89.91'
roach = corr.katcp_wrapper.FpgaClient(roach_ip)
time.sleep(1)

# ipdb.set_trace()
i = 0

while(1):

    antenas = utils.get_antenas(roach)

    a1 = antenas[0]
    a2 = antenas[1]
    a3 = antenas[2]
    a4 = antenas[3]

    f = np.linspace(1200,1800, 2048, endpoint=False)

    # fig, axes = plt.subplots(2,2, figsize = (16, 7.5))
    #
    # axes[0,0].plot(a1[1::],label = 'Antena 1')
    # axes[1,0].plot(a2[1::],label = 'Antena 2 ')
    # axes[0,1].plot(a3[1::],label = 'Antena 3')
    # axes[1,1].plot(a4[1::],label = 'Antena ref ')
    #
    #
    # axes[0,0].set_title('Antenna 1')
    # axes[1,0].set_title('Antenna 2')
    # axes[0,1].set_title('Antenna 3')
    # axes[1,1].set_title('Antenna ref')
    #
    # axes[1,1].set_xlabel('ch')
    # axes[1,0].set_xlabel('ch')
    #
    # axes[1,0].set_ylabel('Power ')
    # axes[0,0].set_ylabel('Power ')
    #
    # axes[0,0].grid()
    # axes[0,1].grid()
    # axes[1,0].grid()
    # axes[1,1].grid()
    #
    #
    # axes[0,0].legend()
    # axes[0,1].legend()
    # axes[1,0].legend()
    # axes[1,1].legend()
    #
    # #plt.show()
    # plt.savefig(str(i)+'Antenas.png')

    fig, axes = plt.subplots(2,2, figsize = (16, 7.5))

    axes[0,0].plot(10*np.log10(a1[1::]),label = 'Antena 0')
    axes[0,1].plot(10*np.log10(a2[1::]),label = 'Antena 1 ')
    axes[1,0].plot(10*np.log10(a3[1::]),label = 'Antena 2')
    axes[1,1].plot(10*np.log10(a4[1::]),label = 'Antena ref ')


    axes[0,0].set_title('Antenna 0')
    axes[0,1].set_title('Antenna 1')
    axes[1,0].set_title('Antenna 2')
    axes[1,1].set_title('Antenna ref')


    axes[0,0].axis(ymin =  30 , ymax = 75)
    axes[0,1].axis(ymin =  30 , ymax = 75)
    axes[1,0].axis(ymin =  30 , ymax = 75)
    axes[1,1].axis(ymin =  30 , ymax = 75)

    axes[1,1].set_xlabel('ch')
    axes[1,0].set_xlabel('ch')

    axes[1,0].set_ylabel('Power dB ')
    axes[0,0].set_ylabel('Power dB ')

    axes[0,0].grid()
    axes[0,1].grid()
    axes[1,0].grid()
    axes[1,1].grid()


    axes[0,0].legend()
    axes[0,1].legend()
    axes[1,0].legend()
    axes[1,1].legend()

    #plt.show()
    plt.savefig(str(i)+'Antenas_db.png')
    # np.savetxt(str(i)+"Antenas.csv", a1, delimiter=',', header="Antenas"+str(i), comments="")
    i = i+1
    time.sleep(15)

