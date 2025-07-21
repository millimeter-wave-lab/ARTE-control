import numpy as np
import calandigital as calan
import matplotlib.pyplot as plt
import time, corr

path0 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_15_01_2025_antennas_4adaptors+2codosacero_50deg.npz'
path1 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_15_01_2025_antennas_4adaptors+2codosacero_40deg.npz'
path2 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_15_01_2025_antennas_4adaptors+2codosacero_30deg.npz'
path3 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_22_01_2025_antennas_4adaptors+2codosacero_50deg_new.npz'
path4 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_22_01_2025_antennas_4adaptors+2codosacero_40deg_new.npz'
path5 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_22_01_2025_antennas_4adaptors+2codosacero_30deg_new.npz'

path = path0.split('/')

channels = 2048
freq = np.linspace(1201,1799,2046)

file0 = np.load(path0)
data0 = file0['data']

file1 = np.load(path1)
data1 = file1['data']

file2 = np.load(path2)
data2 = file2['data']

file3 = np.load(path3)
data3 = file3['data']
file4 = np.load(path4)
data4 = file4['data']
file5 = np.load(path5)
data5 = file5['data']
#file6 = np.load(path6)
#data6 = file6['data']

graph1=np.rad2deg((np.angle(data0[4,:])))
graph2=np.rad2deg((np.angle(data1[4,:])))
graph3=np.rad2deg((np.angle(data2[4,:])))
graph4=np.rad2deg((np.angle(data3[4,:])))
graph5=np.rad2deg((np.angle(data4[4,:])))
graph6=np.rad2deg((np.angle(data5[4,:])))
#graph7=np.rad2deg((np.angle(data6[4,:])))

'''
for i in range(len(graph2)):
    if graph2[i]>100.0:   
        graph2[i]=(graph2[i]-360)
for i in range(len(graph3)):
    if graph3[i]>100.0:      
        graph3[i]=(graph3[i]-360)
for i in range(len(graph4)):
    if graph4[i]>100.0:      
        graph4[i]=(graph4[i]-360)
for i in range(len(graph5)):
    if graph5[i]>100.0:      
        graph5[i]=(graph5[i]-360)
for i in range(len(graph6)):
    if graph6[i]>100.0:      
        graph6[i]=(graph6[i]-360)
for i in range(len(graph7)):
    if graph7[i]>100.0:      
        graph7[i]=(graph7[i]-360)
'''
#plt.plot(freq,  graph1, alpha = 0.5, label='50')
#plt.plot(freq,  graph2, alpha = 0.5, label='40')
plt.plot(freq,  graph3, alpha = 0.5, label='30')
#plt.plot(freq,  graph4, alpha = 0.5, label='50 after CPT + ARTE')
#plt.plot(freq,  graph5, alpha = 0.5, label='40 after CPT + ARTE')
plt.plot(freq,  graph6, alpha = 0.5, label='30 after CPT + ARTE')
'''
plt.plot(freq,  np.rad2deg(np.unwrap(np.angle(data3[4,:]))), alpha = 0.5)
'''
#plt.legend()
plt.grid()
plt.xlim(1200,1800)
#plt.ylim(-120,40)
plt.title('Phase difference rxs + antennas far field')
plt.xlabel('Freq MHz')
plt.ylabel('Angle deg')
plt.legend()
plt.show()
