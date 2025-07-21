import calandigital as calan
import numpy as np
import utils, corr, yaml, time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from calandigital.instruments import generator
import control

genname = 'TCPIP::10.17.89.229::INSTR'
gen_power = -25
gen_info = {'type':'visa', 'connection':genname, 'def_freq':1000, 'def_power':gen_power}
gen = generator.create_generator(gen_info)
freq_rp=[(341 / 2048.0 * 600 + 1200), (683 / 2048.0 * 600 + 1200),(1024 / 2048.0 * 600 + 1200), (1365 / 2048.0 * 600 + 1200), (1707 / 2048.0 * 600 + 1200)]


def plot_beam(_fpga, _freq=[1200, 1800]):
    global fpga, data, freq
    fpga = _fpga
    y_lim = (-90,0)

    data = []
    axes = []
    freq = np.linspace(_freq[0], _freq[1], 2048, endpoint=0)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_ylim(y_lim)
    ax.set_xlim(freq[0], freq[-1])
    ax.grid()
    ax.set_title('Beam')
    data, = ax.plot([],[],lw=2)
    anim = FuncAnimation(fig, animate, interval=50, blit=True)
    plt.show()

def animate(i):
    dat = utils.get_beam(fpga)
    spec = 10*np.log10(dat+1)-111.119
    data.set_data(freq, spec)
    return data,

def save_data(variable, N, freq):
    dat_array = np.zeros((2048, N))
    spec_array = np.zeros((2048, N))
    for i in range(N):
        dat_array[:, i] = utils.get_beam(fpga)
        spec_array[:, i] = 10*np.log10(dat_array[:, i]+1)-111.119
        print(i)
    np.savetxt('dat' + str(variable) + str(freq) + '.csv', dat_array, delimiter = ',')
    np.savetxt('spec' + str(variable) + str(freq) + '.csv', spec_array, delimiter = ',')


if __name__ == '__main__':
    f = open('configuration.yml', 'r')
    config = yaml.load(f, Loader=yaml.loader.SafeLoader)
    f.close()
    roach = corr.katcp_wrapper.FpgaClient(config['roach_ip'])
    for i in range(5):
        print(freq_rp[i])
        gen.set_freq_mhz(freq_rp[i])
        time.sleep(1)
        plot_beam(roach)
        angle=120
        freqname=i
        N = 1000
        save_data(angle, N, freqname)
    

