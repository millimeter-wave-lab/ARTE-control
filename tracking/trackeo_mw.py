import os
import glob
import importlib

import time, datetime, math
import PyIndi
import numpy as np
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz


import src.logging
importlib.reload(src.logging)
from src.logging import *

import src.coords
importlib.reload(src.coords)
from src.coords import *

# loggin directory
directory = 'tracking_logs'

# absolute lap
min_abs_lap = 0 * u.deg
max_abs_lap = 360 * u.deg

# indi parameters
INDI_SERVER_HOST="localhost"
INDI_SERVER_PORT=7624
TELESCOPE_DEVICE="LX200 Autostar"#"EQMod Mount"

# client definition
indiclient = PyIndi.BaseClient()
indiclient.setServer(INDI_SERVER_HOST, INDI_SERVER_PORT)
indiclient.watchDevice(TELESCOPE_DEVICE)
device=None

# server connection 
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


# ON_COORD_SET initial setup
telescope_on_coord_set = device.getSwitch("ON_COORD_SET")
while not(telescope_on_coord_set):
    time.sleep(0.5)
    telescope_on_coord_set = device.getSwitch("ON_COORD_SET")

#GC initial values
ref = 0*u.deg
Altitud, Azimuth, MW_centre, MW_offset = get_GC_coords()

#Get last absolute_lap
if directory_exists(directory):
    last_filename = sorted(os.listdir(directory))
else:
    os.mkdir(directory)
    last_filename = sorted(os.listdir(directory))

first_iteration = False

if len(last_filename) == 0:
    print('no first file created... skipping')
    absolute_lap = 0* u.deg
    first_iteration = True

    current_ra, current_dec, current_alt, current_az = get_current_coords(device)
    latest = generate_tracking_log_line(current_ra, current_dec, current_alt, current_az, absolute_lap)
    write_log(directory, get_log_file_name(directory), latest)
    

else: 
    if load_last_line_from_log(os.path.join(directory,last_filename[-1])) == None:
        print('no last line recorded... please make sure everything is ok')
        absolute_lap = 0* u.deg

        current_ra, current_dec, current_alt, current_az = get_current_coords(device)
        latest = generate_tracking_log_line(current_ra, current_dec, current_alt, current_az, absolute_lap)
        write_log(directory, get_log_file_name(directory), latest)
    else:
        absolute_lap = load_last_line_from_log(os.path.join(directory,last_filename[-1]))[-1]

        if check_abs_lap(absolute_lap, min_abs_lap, max_abs_lap) == -1:
            reset_abs_lap(device, absolute_lap)

while(device.isConnected()):

    Altitud, Azimuth, MW_centre, MW_offset = get_GC_coords()

    if Altitud > ref:
        print('MW observable')
    
        ##### CHECKS ABSOLUTE LAP
        if check_abs_lap(absolute_lap, min_abs_lap, max_abs_lap) == -1:
            print('absolute lap overlap\n')
            reset_abs_lap(device, absolute_lap)
    
        ##### MOVING
        
        Altitud, Azimuth, MW_centre, MW_offset = get_GC_coords()
        
        print(f'GC coords:\nRA: {MW_centre["ra"]}\nDEC: {MW_centre["dec"]}\nAlt: {Altitud}\nAz:{Azimuth}\n\nSending coords...')

        telescope_on_coord_set[0].s = PyIndi.ISS_ON  # TRACK we want track de MW
        telescope_on_coord_set[1].s = PyIndi.ISS_OFF # SLEW
        telescope_on_coord_set[2].s = PyIndi.ISS_OFF # SYNC
        indiclient.sendNewSwitch(telescope_on_coord_set)
        
        telescope_radec = device.getNumber("EQUATORIAL_EOD_COORD")

        telescope_radec = device.getNumber("EQUATORIAL_EOD_COORD")
        telescope_radec[0].value = MW_centre['ra']
        telescope_radec[1].value = MW_centre['dec']
        indiclient.sendNewNumber(telescope_radec)
        print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(telescope_radec[0].value, telescope_radec[1].value))
        # and wait for the scope has finished moving


        while not(telescope_radec):
            time.sleep(0.5)
            telescope_radec = device.getNumber("EQUATORIAL_EOD_COORD")
            telescope_radec[0].value = MW_centre['ra']
            telescope_radec[1].value = MW_centre['dec']
            indiclient.sendNewNumber(telescope_radec)
            print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(telescope_radec[0].value, telescope_radec[1].value))
            # and wait for the scope has finished moving
        while (telescope_radec.getState()==PyIndi.IPS_BUSY):
            print("Scope Moving ", telescope_radec[0].value, telescope_radec[1].value)
            time.sleep(1)
        
        ##### LOGGING
        print('logging...')
        prev_date, prev_ra, prev_dec, prev_alt, prev_az, prev_abs_lap = load_last_line_from_log(os.path.join(directory,get_log_filenames(directory)[-1]))
        current_ra, current_dec, current_alt, current_az = get_current_coords(device)
        
        absolute_lap = absolute_lap + current_az - prev_az
        
        latest = generate_tracking_log_line(current_ra, current_dec, current_alt, current_az, absolute_lap)
        write_log(directory, get_log_file_name(directory), latest)
        time.sleep(3)
    
    if not(Altitud > ref):
        print(Altitud.to_value(u.deg))
           # the order below is defined in the property vector, look at the standard Properties page
        telescope_on_coord_set[0].s = PyIndi.ISS_OFF  # TRACK
        telescope_on_coord_set[1].s = PyIndi.ISS_ON   # SLEW we want to slew to a coordinate and stop upon receiving coordinates.
        telescope_on_coord_set[2].s = PyIndi.ISS_OFF # SYNC
        indiclient.sendNewSwitch(telescope_on_coord_set)

        # We set the desired coordinates
        telescope_radec =  device.getNumber("EQUATORIAL_EOD_COORD")
        while not(telescope_radec):
            time.sleep(0.5)
            telescope_radec = device.getNumber("EQUATORIAL_EOD_COORD")
            telescope_radec[0].value = MW_offset['ra']
            telescope_radec[1].value = MW_offset['dec']
            indiclient.sendNewNumber(telescope_radec)
            print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(telescope_radec[0].value, telescope_radec[1].value))
        # and wait for the scope has finished moving
        while (telescope_radec.getState()==PyIndi.IPS_BUSY):
            print("Scope Moving ", telescope_radec[0].value, telescope_radec[1].value)
            time.sleep(2)
        
print('device disconnected')
    
