
import numpy as np
import matplotlib.pyplot as plt

DMs = [45,90,135,180,225,270,315,360,405,450,495]
freqs = [1200,1800]

def frb_curve(DM, f1, f2, n_samp=8192):
    """
     inputs:
        DM in pc*cm**3
        f1, f2 in mhz
     outputs:
        f in MHz
        t in seconds 
    """
    ##wrong!!! the t must be linear!
    ti = 4.149*10**3*DM*f1**(-2)
    tf = 4.149*10**3*DM*f2**(-2)
    t = np.linspace(ti,tf,n_samp)
    f = np.sqrt(4.149*10**3*DM/t)
    #t = 4.149*10**3*DM*f**(-2)
    return [t-t[-1],f]


#calculate the period for each DM
#periods = np.zeros(len(DMs))
for i in range(len(DMs)-1,-1,-1):
    t,f = frb_curve(DMs[i],freqs[0], freqs[1])
    #periods[i] = t[0]
    plt.plot(t,f, label = 'DM'+str(DMs[i]))
    plt.legend()

plt.grid()
plt.xlabel('Time s')
plt.ylabel('Frequency MHz')
plt.ylim(1200,1800)
plt.xlim(0,0.8)
plt.title('Dispersion measure [pc cm^-3]')
