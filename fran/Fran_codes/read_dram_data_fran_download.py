import ctypes, struct
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.signal import spectrogram
from scipy import ndimage

lib = ctypes.CDLL('./parse_data.so')

lib.parse_data.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.parse_data.restype = ctypes.POINTER(ctypes.c_char)
lib.freeptr.argtype = ctypes.c_void_p
lib.freeptr.restype = None 

#f = file('data_1_chann','rb')
f = file('data', 'rb')
iters = 762
byte_chunk =220*200*36
chunk = byte_chunk/4#220*200*9

iters = 709

fft_size = 2**15
spect0 = np.zeros([iters, fft_size])
spect1 = np.zeros([iters, fft_size])
spect2 = np.zeros([iters, fft_size])

for i in range(iters):
#for i in range(1):
    #raw_data = f.read(byte_chunk)
    raw_data = f.read(3*2*fft_size)
    dat_4raw = lib.parse_data(raw_data, len(raw_data))
    dat_4char = np.array(struct.unpack(str(len(raw_data)*2)+'b', dat_4raw[0:len(raw_data)*2]))
    lib.freeptr(dat_4raw)
    dat4 = dat_4char.reshape(len(dat_4char)/24,24)
    dat0 = dat4[:,:8]
    dat0 = dat0[:,::-1]
    dat0_flat = dat0.flatten()
    dat1 = dat4[:,8:16]
    dat1 = dat1[:,::-1]
    dat1_flat = dat1.flatten()
    dat2 = dat4[:,16:24]
    dat2 = dat2[:,::-1]
    dat2_flat = dat2.flatten()
    
    aux0 = fft(dat0_flat[0:2*fft_size]-np.mean(dat0_flat[:2*fft_size]))
    aux1 = fft(dat1_flat[0:2*fft_size]-np.mean(dat1_flat[:2*fft_size]))
    aux2 = fft(dat2_flat[0:2*fft_size]-np.mean(dat2_flat[:2*fft_size]))
    
    spect0[i,:] = 20*np.log10(np.abs(aux0[:fft_size])+1)
    #spect0[i,:] = (np.abs(aux0[:fft_size])+1)
    spect1[i,:] = 20*np.log10(np.abs(aux1[:fft_size])+1)
    spect2[i,:] = 20*np.log10(np.abs(aux2[:fft_size])+1)
    f.seek(byte_chunk-3*2*fft_size,1) ##1 is move respect currnt position

f.close()

ts = 1./(150.*10**6)
t_iters = ts*byte_chunk/12   #96/8 = numb of bytes per fpga cycle in the dram

t = np.arange(iters)*t_iters
frec = np.linspace(1200, 1800, fft_size, endpoint=False)
plt.pcolormesh(t,frec[::16], (spect0[:,::16].T))
#plt.show()

#start read in 1300-1700 to be in the gain band
start_ind = 7000
end_ind = 27000
#plt.pcolormesh(t,frec[start_ind:end_ind:16], (spect0[:,start_ind:end_ind:16]).T)
plt.show()


aux = spect2[:,::16].T
aux = ndimage.sobel(aux)
plt.pcolormesh(t,frec[::16], aux)
plt.show()


#ex spectrometer
#frec,t,Sxx = spectrogram(dat2_flat, 1200*10**6)
#plt.pcolormesh(t*10**6,frec/10**6,Sxx)
#plt.show()


