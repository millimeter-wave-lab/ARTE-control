import numpy as np
import calandigital as calan
import matplotlib.pyplot as plt
import time, corr




path0 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_27_11_2024_antenas_diode_0.npz'
path1 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_27_11_2024_antenas_diode_0_second.npz'
#path2 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_28_11_2024_antenas_diff_polarization_third.npz'
#path3 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_28_11_2024_antenas_diff_polarization_fourth.npz'
#path4 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_26_11_2024_rxs_new_fifth.npz'



path = path0.split('/')

freq = np.linspace(1201,1799,2046)

file0 = np.load(path0)
data0 = file0['data']

file1 = np.load(path1)
data1 = file1['data']

#file2 = np.load(path2)
#data2 = file2['data']

#file3 = np.load(path3)
#data3 = file3['data']

#file4 = np.load(path4)
#data4 = file4['data']

plt.plot(freq,  np.rad2deg(np.unwrap(np.angle(data0[4,:]))), alpha = 0.5, label='First Test')
plt.plot(freq,  np.rad2deg(np.unwrap(np.angle(data1[4,:]))), alpha = 0.5, label='Second Test')
#plt.plot(freq,  np.rad2deg(np.unwrap(np.angle(data2[4,:]))), alpha = 0.5, label='Third Test')
#plt.plot(freq,  np.rad2deg(np.unwrap(np.angle(data3[4,:]))), alpha = 0.5, label='Fourth Test')
#plt.plot(freq,  np.rad2deg(np.unwrap(np.angle(data4[4,:]))), alpha = 0.5, label='Fifth Test')

'''
plt.plot(freq,np.unwrap(np.rad2deg(np.angle(data2[4,:]))), alpha = 0.5, label = 'desfase 360')
plt.plot(freq, 360+ np.unwrap(np.rad2deg(np.angle(data3[4,:]))), alpha = 0.5, label = 'desfase 135')

plt.plot(freq, 360+np.unwrap(np.rad2deg(np.angle(data4[4,:]))), alpha = 0.5, label = 'desfase 67.5')
'''
#plt.plot(freq,360*3-1*np.rad2deg(np.unwrap(np.angle(data0[4,:]))), alpha = 0.5)# data[4,:] primera diferencia adc0-ad1 vs chns

#plt.legend()
plt.grid()
plt.xlim(1200,1800)
plt.ylim(-120,120)
#plt.title('Phase rx1 rx2'+path[7])
plt.title('Phase difference between rxs + antennas')
plt.xlabel('Freq MHz')
plt.ylabel('Angle deg')
plt.legend()
plt.show()
