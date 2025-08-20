import numpy as np
import calandigital as calan
import matplotlib.pyplot as plt
import time, corr
from sklearn.metrics import mean_squared_error

#Define the path to the data
path0 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_19_05_2025_with_small_grey_cable.npz'
path1 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_22_05_2025_two_grey_cables.npz'

#path2 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_22_05_2025_grey_cable.npz'
#path3 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_20_05_2025_3.npz'
#path4 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_23_01_2025_antennas_4adaptors+2codosacero_90deg_roachoff3_with_init.npz'
#path5 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_24_01_2025_antennas_4adaptors+2codosacero_90deg_roachoff4_with_init.npz'

path = path0.split('/')
freq = np.linspace(1201,1799,2046)

#Load the data 
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
#file5 = np.load(path5)
#data5 = file5['data']

#Option to plot the curves without unwraped
graph1=np.rad2deg((np.angle(data0[4,:])))
graph2=np.rad2deg((np.angle(data1[4,:])))
#graph3=np.rad2deg((np.angle(data2[4,:])))
#graph4=np.rad2deg((np.angle(data3[4,:])))

#This following part is to have all the ploted curves in the same section of the graphic (not 360 degrees lower or upper)
for i in range(len(graph1)):
    if graph1[i]<-100.0:   
        graph1[i]=(graph1[i]+360)
    if graph2[i]<-100.0:
        graph2[i]=(graph2[i]+360)
    #if graph3[i]<-100.0:
    #    graph3[i]=(graph3[i]+360)
    #if graph4[i]<-100.0:
    #    graph4[i]=(graph4[i]+360)

plt.plot(freq,  graph1, alpha = 0.5,label='Phase difference one grey cable')
plt.plot(freq,  graph2, alpha = 0.5,label='Phase difference two grey cables')
#plt.plot(freq,  graph3, alpha = 0.5,label='Phase difference one grey cable 2nd')
#plt.plot(freq,  graph4, alpha = 0.5,label='Phase difference 20/05')

#Option to plot the curves unwraped
#plt.plot(freq[:1850],  np.rad2deg(np.unwrap(np.angle(data3[4,:])))[:1850], alpha = 0.5,label='Two grey cables + adaptor')
#plt.plot(freq[:1850],  np.rad2deg(np.unwrap(np.angle(data4[4,:])))[:1850], alpha = 0.5,label='ROACH off 3')
#plt.plot(freq[:1850],  np.rad2deg(np.unwrap(np.angle(data5[4,:])))[:1850], alpha = 0.5,label='ROACH off 4')

#EXTRA: If you want to calculate the MSE to know which curve is closer to zero
#array_diferences_azul=(np.rad2deg(np.unwrap(np.angle(data0[4,:])))[:1850])**2
#mse_azul = np.mean(array_diferences_azul)

#Plot specifications
plt.legend()
plt.grid()
plt.xlim(1200,1800)
plt.ylim(-100,150)
plt.title('Phase difference rxs + antennas far field')
plt.xlabel('Freq MHz')
plt.ylabel('Angle deg')
#plt.legend()
plt.show()
