# imports
import time, datetime, math
import PyIndi
import astropy.coordinates as coord
from astropy.time import Time
import numpy as np
from astropy.coordinates import (SkyCoord, Distance, Galactic, 
                                 EarthLocation, AltAz,ICRS)
from astropy import units as u

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

## test parameters
refresh_time = 2 ##minutes
test_time = 3       ##hrs
#iters = test_time*60//refresh_time
iters=1#70000
data = np.zeros(5)

filename = "logger_pos_09_07"
##create log file
f = open(filename, 'w')
f.close()

# parameters
INDI_SERVER_HOST="localhost"
INDI_SERVER_PORT=7624
TELESCOPE_DEVICE="LX200 Autostar"#"EQMod Mount"

# client definition
indiclient = PyIndi.BaseClient()
indiclient.setServer(INDI_SERVER_HOST, INDI_SERVER_PORT)
indiclient.watchDevice(TELESCOPE_DEVICE)
device=None

#try to connect to the server
print("Connecting server "+indiclient.getHost()+":"+str(indiclient.getPort()))
serverconnected=indiclient.connectServer()
if(serverconnected):
    print('Server successfully connected')
else:
    raise Exception('Cant connect to the server')

#try to connect to the de device
device = indiclient.getDevice(TELESCOPE_DEVICE)
if not(device):
    device=indiclient.getDevice(TELESCOPE_DEVICE)
    while not(device):
        print("Trying to get device "+TELESCOPE_DEVICE)
        time.sleep(0.5)
        device=indiclient.getDevice(TELESCOPE_DEVICE)
print("Got device "+TELESCOPE_DEVICE)

if not(device.isConnected()):
    device_connect=device.getSwitch("CONNECTION")
    while not(device_connect):
        print("Trying to connect device "+TELESCOPE_DEVICE)
        time.sleep(0.5)
        device_connect=device.getSwitch("CONNECTION")
if not(device.isConnected()):
    device_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
    device_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
    indiclient.sendNewSwitch(device_connect)
if(device.isConnected()):
    print('Device successfully connected')
time.sleep(0.5)

if(not device.isConnected()):
    indiclient.disconnectServer()
    server_proc.terminate()
    raise Exception('Cant connect to the mount!')
######################################################

## GEOGRAPHIC_COORD
geographic_pos = device.getNumber("GEOGRAPHIC_COORD")
geographic_pos[0].value   # LAT Site latitude (-90 to +90), degrees +N
geographic_pos[1].value   # LONG Site longitude (0 to 360), degrees +E
geographic_pos[2].value   # ELEV Site elevation, meters
indiclient.sendNewNumber(geographic_pos)

'''
t = Time.now()
print('time now', t)
utc_time = device.getText("TIME_UTC")
print('Device', utc_time[0].text)
utc_time[0].text=str(t.value.year)+'-'+str(t.value.month).zfill(2)+'-'+str(t.value.day).zfill(2)+'T'+str(t.value.hour).zfill(2)+':'+str(t.value.minute).zfill(2)+':'+str(t.value.second).zfill(2)
#= utc.isoformat()
utc_time[1].text

print('Device', utc_time[0].text)
print('Device', utc_time[1].text)
#= str(offset)
indiclient.sendNewText(utc_time)

utc_time2 = device.getText("TIME_UTC")
print('Device', utc_time2[0].text)
print('Device', utc_time2[1].text)
'''

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

def plotFFT(show = True, save = False, span = 4096):

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
        lim2 = lim1 + span
        for j in range(3):
            ax[j].plot(np.arange(span), data_final_re_correctOrder[j, lim1:lim2], \
            lw = 3, ls = '-', c = 'purple')
            ax[j].plot(np.arange(span), data_final_im_correctOrder[j, lim1:lim2], \
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
            ax[j].plot(np.arange(span), FFTsdB[j, :], \
            linewidth = 2, ls = '-')
            ax[j].set_ylim(-70, 0)
            ax[j].grid(True, ls = '--')
        plt.show()

        if save == True:
            for j in range(3):
                np.savetxt('FFT_re_adc' + str(j) + '.csv', \
                data_final_re_correctOrder[j, lim1:lim2], delimiter = ',')
                np.savetxt('FFT_im_adc' + str(j) + '.csv', \
                data_final_im_correctOrder[j, lim1:lim2], delimiter = ',')

    return data_final_re, data_final_im

def get_current_coords(device):
    radec = device.getNumber("EQUATORIAL_EOD_COORD")
    ra = radec[0].value
    dec = radec[1].value
    radec = SkyCoord(ra=ra*u.hour, dec=dec*u.deg, frame='icrs')
    # Calan GEOGRAPHIC_COORD
    calan_obs = EarthLocation(lat=-33.3961*u.deg, lon=-70.537*u.deg, height=867*u.m)
    now = Time.now()
    altaz_frame = AltAz(obstime=now,location=calan_obs)
    altaz = radec.transform_to(altaz_frame)
    alt = altaz.alt
    az = altaz.az
    return ra * u.hour, dec * u.deg, alt.deg, az.deg

def get_altz_coords(ra, dec):
    radec = SkyCoord(ra=ra*u.hour, dec=dec*u.deg, frame='icrs')
    # Calan GEOGRAPHIC_COORD
    calan_obs = EarthLocation(lat=-33.3961*u.deg, lon=-70.537*u.deg, height=867*u.m)
    now = Time.now()
    altaz_frame = AltAz(obstime=now,location=calan_obs)
    altaz = radec.transform_to(altaz_frame)
    alt = altaz.alt
    az = altaz.az
    return alt, az

def give_alt_az_coords_in_equatorial(alt, az):
    calan_obs = EarthLocation(lat=-33.3961*u.deg, lon=-70.537*u.deg, height=867*u.m)
    now = Time.now()
    print(now)
    altaz = AltAz(alt=alt, az=az, obstime=now, location=calan_obs)
    coord = SkyCoord(altaz)
    icrs = coord.transform_to('icrs')
    ra=icrs.ra.hour
    dec=icrs.dec.deg
    return ra, dec

ip = '10.17.89.228'
bof = 'doa_offline.bof.gz'
fpga = corr.katcp_wrapper.FpgaClient(ip)
time.sleep(1)

fpga.upload_program_bof('doa_offline.bof.gz', port = 3000)

Altitudes=np.concatenate((np.linspace(0,90,4),np.linspace(90,0,4)))

N = 10
save_real = np.zeros((N, len(Altitudes), 3, 4096))
save_imag = np.zeros((N, len(Altitudes), 3, 4096))
######################################################
####### Milky way #######
for i in range(len(Altitudes)):
    print('iters',i)
    # We want to set the ON_COORD_SET switch to engage tracking after goto
    # device.getSwitch is a helper to retrieve a property vector
    tel_on_coord_set = device.getSwitch("ON_COORD_SET")
    while not(tel_on_coord_set):
        time.sleep(0.5)
        tel_on_coord_set = device.getSwitch("ON_COORD_SET")
    # the order below is defined in the property vector, look at the standard Properties page
    # or enumerate them in the Python shell when you're developing your program
    tel_on_coord_set[0].s=PyIndi.ISS_ON  # TRACK
    tel_on_coord_set[1].s=PyIndi.ISS_OFF # SLEW
    tel_on_coord_set[2].s=PyIndi.ISS_OFF # SYNC
    indiclient.sendNewSwitch(tel_on_coord_set)
    # We set the desired coordinates
    radec = device.getNumber("EQUATORIAL_EOD_COORD")
    print("Current position from device :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))
    while not(radec):
        time.sleep(0.5)
        radec = device.getNumber("EQUATORIAL_EOD_COORD")
    alt=Altitudes[i]*u.deg
    if i<(len(Altitudes)/2):
        az=180*u.deg
    else:
        az=0*u.deg
    ra, dec = give_alt_az_coords_in_equatorial(alt,az)
    radec[0].value = ra
    radec[1].value = dec
    indiclient.sendNewNumber(radec)
    print("Position to track :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))
    # and wait for the scope has finished moving
    data[3] = radec[0].value
    data[4] = radec[1].value
    #print(data)
    while (radec.getState()==PyIndi.IPS_BUSY):
        print(radec.getState())
        print("Scope Moving ", radec[0].value, radec[1].value)
        time.sleep(2)
        A=device.getNumber("EQUATORIAL_EOD_COORD")
        print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(A[0].value, A[1].value))
    ra_dev, dec_dev, alt_dev, az_dev= get_current_coords(device)
    print('Given ra', ra_dev, 'Given dec', dec_dev)
    print('Elevation', alt_dev, 'Azimuth', az_dev)
    for j in range(N):
        save_real[j, i, :, :], save_imag[j, i, :, :] = plotFFT(show = False)
    print(save_real)
    with open(filename, 'ab') as f:
        f.write(b'\r\n')
        np.savetxt(f, [data], delimiter=',')
    time.sleep(5)

for j in range(3):
    for i in range(len(Altitudes)):
        np.savetxt('FFT_re_adc' + str(j) + '_altitude' + str(i) + '.csv', \
        save_real[:, i, j, :].T, delimiter = ',')
        np.savetxt('FFT_im_adc' + str(j) + '_altitude' + str(i) + '.csv', \
        save_imag[:, i, j, :].T, delimiter = ',')
time.sleep(5)
#try to disconnect to the server
print("Disconnecting server "+indiclient.getHost()+":"+str(indiclient.getPort()))
serverconnected=indiclient.disconnectServer()
