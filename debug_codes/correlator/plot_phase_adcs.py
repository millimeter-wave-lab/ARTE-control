import numpy as np
import calandigital as calan
import matplotlib.pyplot as plt
import time, corr




path0 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_adcs_25_10_24_20dBm_attenuation_3dB.npz'

path = path0.split('/')

freq = np.linspace(1,599,2046)

file0 = np.load(path0)
data0 = file0['data']


plt.plot(freq,  np.unwrap(np.rad2deg(np.angle(data0[4,:]))), alpha = 0.5)
'''
plt.plot(freq,np.unwrap(np.rad2deg(np.angle(data2[4,:]))), alpha = 0.5, label = 'desfase 360')
plt.plot(freq, 360+ np.unwrap(np.rad2deg(np.angle(data3[4,:]))), alpha = 0.5, label = 'desfase 135')

plt.plot(freq, 360+np.unwrap(np.rad2deg(np.angle(data4[4,:]))), alpha = 0.5, label = 'desfase 67.5')
'''
#plt.plot(freq,360*3-1*np.rad2deg(np.unwrap(np.angle(data0[4,:]))), alpha = 0.5)# data[4,:] primera diferencia adc0-ad1 vs chns

#plt.legend()
plt.grid()
plt.xlim(0,600)
#plt.ylim(100,360)
#plt.title('Phase rx1 rx2'+path[7])
plt.title('Phase difference ADCs splitter ZFSC-2-4 20dBm with 3 dB attenuation')
plt.xlabel('Freq MHz')
plt.ylabel('Angle deg')
plt.show()
