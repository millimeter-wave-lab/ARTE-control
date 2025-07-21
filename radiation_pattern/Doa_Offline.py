# Tamanho de la FFT: 2048 canales utiles (4096 en total).

import numpy as np # Tratamiento de matrices.
import matplotlib.pyplot as plt # Figuras.
import matplotlib # Definicion de tipo de datos (dtype) en animate.
import struct # Interpretacion de datos.
import corr # Comunicacion con fpga.
import time # Pausas.
import matplotlib.animation as animation # Despliegue de datos en tiempo real.
from numpy import linalg as la # Algebra lineal.
import sys, select, os # Para salir de while True y para crear carpetas.
from matplotlib import cm # Para poner mapa de color en el marker
import pyvisa # Para Comunicacion con equipos en la etapa de calibracion.

#-------------------------------------------------------------------------------
# Conexion a instrumentos.

def inst_connect_rf(device = 'RS', power = -50, freq_MHz = 1500, on = 1):

    rm = pyvisa.ResourceManager("@py")
    if device == 'RS':
        rf_psg = rm.get_instrument('TCPIP::192.168.100.102::INSTR')
    else:
        rf_psg = rm.get_instrument('TCPIP::192.168.100.105::INSTR')

    pow_lev = power
    frequencyRF = freq_MHz * 1e6

    rf_psg.write('POW %f dBm' % pow_lev)
    rf_psg.write('FREQ %f Hz' % frequencyRF)

    if on == 1:
        rf_psg.write('OUTP on')
    else:
        rf_psg.write('OUTP off')

################################################################################
# Definicion de funciones relacionadas con la FPGA y el modelo digital.
################################################################################

#-------------------------------------------------------------------------------
# Para escribir los valores calculados en python en las brams.
# Especificamente, transforma de float a fixed.

def float2fixed(data, nbits, binpt, signed = True):
    nbytes = int(np.ceil(nbits / 8))
    dtype = '>i' + str(nbytes) if signed else '>u' + str(nbytes)
    fixedpointData = (2 ** binpt * data).astype(dtype)
    return fixedpointData

#-------------------------------------------------------------------------------
# Plot de FFTs.

def plotFFT(show = True, save = False):

    fpga.write_int('writeFFTs', 0)
    time.sleep(0.05)
    fpga.write_int('writeFFTs', 1)
    time.sleep(0.05)

    data_final_re = np.zeros((3, 4096))
    data_final_im = np.zeros((3, 4096))

    data_final_re_correctOrder = np.zeros((3, 4096))
    data_final_im_correctOrder = np.zeros((3, 4096))

    list1 = ['o_ch0', 'o_ch1', 'o_ch2', 'o_ch3']
    list2 = ['x_ch0', 'x_ch1', 'x_ch2', 'x_ch3']
    list3 = ['y_ch0', 'y_ch1', 'y_ch2', 'y_ch3']

    list = [list1, list2, list3]

    for i in range(3):

        data_re = ''; data_im = ''

        for j in range(4):

            data = fpga.read('brams_fft_' + list[i][j], 1024 * 4)

            for k in range(1024):

                data_re += data[4 * k + 0]
                data_re += data[4 * k + 1]
                data_im += data[4 * k + 2]
                data_im += data[4 * k + 3]

        data_final_re[i, :] = struct.unpack('>4096h', data_re)
        data_final_im[i, :] = struct.unpack('>4096h', data_im)

    for i in range(3):

        for j in range(4096):

            if data_final_re[i, j] > 2 ** (16 - 1) - 1:
                data_final_re[i, j] -= 2 ** 16
            if data_final_im[i, j] > 2 ** (16 - 1) - 1:
                data_final_im[i, j] -= 2 ** 16

        for j in range(1024):

            data_final_re_correctOrder[i, 4 * j] = data_final_re[i, j]
            data_final_re_correctOrder[i, 4 * j + 1] = data_final_re[i, j + 1024]
            data_final_re_correctOrder[i, 4 * j + 2] = data_final_re[i, j + 1024 * 2]
            data_final_re_correctOrder[i, 4 * j + 3] = data_final_re[i, j + 1024 * 3]

            data_final_im_correctOrder[i, 4 * j] = data_final_im[i, j]
            data_final_im_correctOrder[i, 4 * j + 1] = data_final_im[i, j + 1024]
            data_final_im_correctOrder[i, 4 * j + 2] = data_final_im[i, j + 1024 * 2]
            data_final_im_correctOrder[i, 4 * j + 3] = data_final_im[i, j + 1024 * 3]

    if show == True:
        fig, ax = plt.subplots(1, 3, figsize = (16, 6.5))
        lines = ['-', '--', '-.']
        markers = ['D', 'o', 's']
        lim1 = 0
        lim2 = 4096
        for j in range(3):
            ax[j].plot(np.arange(4096), data_final_re_correctOrder[j, lim1:lim2], \
            lw = 3, ls = '-', c = 'purple')
            ax[j].plot(np.arange(4096), data_final_im_correctOrder[j, lim1:lim2], \
            lw = 3, ls = '-', c = 'magenta')
            ax[j].grid(True, ls = '--')
        plt.show()

        FFTsdB = np.zeros((3, 4096))
        maxFFTs = np.zeros(3)
        for j in range(3):
            FFTsdB[j, :] = 10 * np.log10(data_final_re_correctOrder[j, :] ** 2 + \
            data_final_im_correctOrder[j, :] ** 2 + 10 ** -10)
            maxFFTs[j] = np.max(FFTsdB[j, :])
        FFTsdB -= max(maxFFTs)

        fig, ax = plt.subplots(1, 3, figsize = (16, 6.5))
        for j in range(3):
            ax[j].plot(np.arange(4096), FFTsdB[j, lim1:lim2], \
            linewidth = 2, ls = '-')
            ax[j].set_ylim(-70, 0)
            ax[j].grid(True, ls = '--')
        plt.show()

        if save == True:
            for j in range(3):
                np.savetxt('FFT_re_adc' + str(j) + '.csv', \
                data_final_re_correctOrder[j, :], delimiter = ',')
                np.savetxt('FFT_im_adc' + str(j) + '.csv', \
                data_final_im_correctOrder[j, :], delimiter = ',')

    return data_final_re_correctOrder, data_final_im_correctOrder

################################################################################
# Ejecucion de los dos procesos de forma paralela.
################################################################################

def _main():

    go = 1
    variable = 0

    plotFFT(show = True)

    if go:

        N = 100
        save_real = np.zeros((N, 3, 4096))
        save_imag = np.zeros((N, 3, 4096))
        for j in range(N):
            print(j)
            save_real[j, :, :], save_imag[j, :, :] = plotFFT(show = False)
        #
        for j in range(3):
            np.savetxt('FFT_re_adc' + str(j) + 'Angle' + str(variable) + '.csv', \
            save_real[:, j, :].T, delimiter = ',')
            np.savetxt('FFT_im_adc' + str(j) + 'Angle' + str(variable) + '.csv', \
            save_imag[:, j, :].T, delimiter = ',')

if __name__ == '__main__':

    ############################################################################
    # Programa principal.
    ############################################################################

    ip = '10.17.89.228'
    bof = 'doa_offline.bof.gz'
    fpga = corr.katcp_wrapper.FpgaClient(ip)
    time.sleep(1)

    fpga.upload_program_bof('doa_offline2.bof.gz', port = 3000)

   #############################################################################

    _main()
