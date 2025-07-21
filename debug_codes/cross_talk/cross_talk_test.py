import numpy as np
import calandigital as calan
import sys, time, corr
##sys.path.append('../../codes')
import control, utils
from utils import*
import calandigital as calan
from calandigital.instruments import generator
from calandigital.instruments.rigol_dp832 import rigol_dp832


roach_ip = '192.168.0.168'
genname = 'TCPIP::192.168.0.33::INSTR'
bw = 600
channels = 100
gen_power = -75


####
roach = corr.katcp_wrapper.FpgaClient(roach_ip)

gen_info = {'type':'visa', 'connection':genname, 'def_freq':1000, 'def_power':gen_power}
gen = generator.create_generator(gen_info)

freq = np.linspace(1200,1800, channels, endpoint=False)
freq = freq[1:-1]


gen_pow = float(gen.instr.query('pow?'))
if(gen_pow != gen_power):
    raise Exception('Carefull the power is not set correctly')
else:
    gen.turn_output_on()

powers = np.zeros((4, channels, len(freq)))
data = np.zeros((4, len(freq)))

for i in range(len(freq)):
    print(i)
    gen.set_freq_mhz(freq[i])
    time.sleep(0.5)
    antennas = utils.get_antennas(roach)
    powers[:,:,i] = antennas
    data[:,i] = antennas[:,i+1]
    
gen.turn_output_off()

np.savez('arte_cross_talkv4.npz',
        powers=powers,
        data = data)


