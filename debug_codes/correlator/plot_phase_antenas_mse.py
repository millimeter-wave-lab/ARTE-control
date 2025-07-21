import numpy as np
import calandigital as calan
import matplotlib.pyplot as plt
import time, corr
from sklearn.metrics import mean_squared_error

#path0 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_28_01_2025_antennas_2greycables_adaptor_90deg.npz'
path0 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_29_01_2025_antennas_2greycables_2adaptors_90deg.npz'

path1 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_29_01_2025_antennas_2greycables_2adaptors_90deg_second.npz'

path2 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_09_01_2025_antennas_4adaptors.npz'

path3 = '/home/arte/Workspace/ARTE-control/debug_codes/correlator/phase_difference_10_01_2025_antennas_4adaptors+2codosacero.npz'

path = path0.split('/')

freq = np.linspace(1201,1799,2046)

file0 = np.load(path0)
data0 = file0['data']

file1 = np.load(path1)
data1 = file1['data']

file2 = np.load(path2)
data2 = file2['data']

file3 = np.load(path3)
data3 = file3['data']

array_diferences_azul=(np.rad2deg(np.unwrap(np.angle(data0[4,:])))[:1850])**2
mse_azul = np.mean(array_diferences_azul)
print(mse_azul, 'Dos cables + codo acero')
mse_rojo = np.mean((np.rad2deg(np.unwrap(np.angle(data1[4,:])))[:1850])**2)
print(mse_rojo, 'Dos cables + codo acero')

plt.plot(freq[:1850],  np.rad2deg(np.unwrap(np.angle(data0[4,:])))[:1850], alpha = 0.5,label='Dos cables + 2 adaptadores mse='+str(mse_azul))

plt.plot(freq[:1850],  np.rad2deg(np.unwrap(np.angle(data1[4,:])))[:1850], alpha = 0.5,label='Dos cables + 2 adaptadores segunda mse='+str(mse_rojo))


plt.legend()
plt.grid()
plt.xlim(1200,1800)
plt.ylim(-100,100)
plt.title('Phase difference rxs + antennas far field')
plt.xlabel('Freq MHz')
plt.ylabel('Angle deg')
#plt.legend()
plt.show()
