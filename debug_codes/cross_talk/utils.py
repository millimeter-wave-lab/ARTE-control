import corr
import numpy as np
import matplotlib.pyplot as plt
import calandigital as calan

def get_beam(roach):
    beam0 = calan.read_data(roach, 'beam0_0', awidth=10,dwidth=64,dtype='>Q')
    beam1 = calan.read_data(roach, 'beam0_1', awidth=10,dwidth=64,dtype='>Q')
    
    beam_0 = beam0[::2]
    beam_1 = beam0[1::2]
    beam_2 = beam1[::2]
    beam_3 = beam1[1::2]
    beam = np.vstack((beam_0,beam_1,beam_2,beam_3)).T.flatten()
    return beam
    
    
def get_quantize_beam(roach):
    beam0 = calan.read_data(roach, 'beam0_0', awidth=11,dwidth=32,dtype='>I')
    return beam0
    

def get_antennas(roach):
    brams = ['antenna_0', 'antenna_1', 'antenna_2', 'antenna_3']
    antennas = np.zeros([4,2048])
    for i,bram in zip(range(len(brams)),brams):
        ant0 = calan.read_data(roach, bram+'_0', awidth=10,dwidth=64,dtype='>Q')
        ant1 = calan.read_data(roach, bram+'_1', awidth=10,dwidth=64,dtype='>Q')
        ch0 = ant0[::2]
        ch1 = ant0[1::2]
        ch2 = ant1[::2]
        ch3 = ant1[1::2]
        antennas[i,:] = np.vstack((ch0,ch1,ch2,ch3)).T.flatten()
    return antennas
        

            
####
##some bitwise operations

def set_bit(data, bit_ind):
    """
    set the bit_ind but dont touch the others
    """
    data |= (1<<bit_ind)
    return data

def clear_bit(data, bit_ind):
    """
    clear the bit_ind but dont touch the others
    """
    data &= ~(1<<bit_ind)
    return data

def flip_bit(data, bit_ind):
    """
    change the bit_ind status
    """
    data ^= (1<<bit_ind)
    return data

def get_bit(data, bit_ind):
    bit = data & (1<<bit_ind)
    return bit


def write_bitfield(prev_state, word, bitfield):
    """ prev_state  :   the word previous word, over you are going to write
        word        :   the word you want to write into the bitfield
        bitfield    :   start and end of the bitfield
    """
    if((word<<bitfield[0])> 2**bitfield[1]):
        raise Exception('The word is grater than the bitfield')
    mask = (2**(bitfield[1]-bitfield[0])-1)<<bitfield[0]
    clean_state = prev_state & ~(mask)  ##check
    new_state = clean_state | (word<<bitfield[0])
    return new_state


