import numpy as np
import calandigital as calan
import matplotlib.pyplot as plt
import time, corr



path0 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/arte_data_ch1_ch2_full_arte_comb_2_1_wo_sw_wo_uln.npz' #1440

path1 =  '/home/arte/Workspace/ARTE-control/debug_codes/correlator/arte_data_ch1_ch2_full_arte_comb_4_1_wo_sw_wo_uln.npz'
#1440

path2 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/arte_data_ch1_ch2_full_arte_comb_2_1_wo_sw_wo_uln_wire_16cms.npz'#1*(360*6)

path3 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/arte_data_ch1_ch2_full_arte_comb_2_1_wo_sw_wo_uln_wire_10cms.npz'#+360

path4 =  '/home/arte/Workspace/ARTE-control/debug_codes/correlator/arte_data_ch1_ch2_full_arte_comb_2_1_wo_sw_wo_uln_wire_3cms.npz'#-360*3

path = path0.split('/')

freq = np.linspace(1201,1799,2046)

file0 = np.load(path0)
data0 = file0['data']

file2 = np.load(path2)
data2 = file2['data']

file3 = np.load(path3)
data3 = file3['data']

file4 = np.load(path4)
data4 = file4['data']

plt.plot(freq, 360+ np.unwrap(np.rad2deg(np.angle(data0[4,:]))), alpha = 0.5, label = 'original')
plt.plot(freq,np.unwrap(np.rad2deg(np.angle(data2[4,:]))), alpha = 0.5, label = 'desfase 360')
plt.plot(freq, 360+ np.unwrap(np.rad2deg(np.angle(data3[4,:]))), alpha = 0.5, label = 'desfase 135')

plt.plot(freq, 360+np.unwrap(np.rad2deg(np.angle(data4[4,:]))), alpha = 0.5, label = 'desfase 67.5')
#plt.plot(freq,360*3-1*np.rad2deg(np.unwrap(np.angle(data0[4,:]))), alpha = 0.5)# data[4,:] primera diferencia adc0-ad1 vs chns

plt.legend()
plt.grid()
plt.xlim(1275,1700)
plt.ylim(100,360)
plt.title('Phase rx1 rx2'+path[7])
plt.xlabel('Freq MHz')
plt.ylabel('Angle deg')
plt.show()
