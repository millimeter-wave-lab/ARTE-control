# imports
import time, datetime, math
import PyIndi
import astropy.coordinates as coord
from astropy.time import Time
import numpy as np
from astropy.coordinates import (SkyCoord, Distance, Galactic, 
                                 EarthLocation, AltAz,ICRS)
from astropy import units as u

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
    altaz = AltAz(alt=alt, az=az, obstime=now, location=calan_obs)
    coord = SkyCoord(altaz)
    icrs = coord.transform_to('icrs')
    ra=icrs.ra.hour
    dec=icrs.dec.deg
    return ra, dec
'''
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
az=270*u.deg
alt=0*u.deg
ra, dec = give_alt_az_coords_in_equatorial(alt,az)
dec_lat= -33.3961
start_time = time.perf_counter()
radec[0].value = ra
radec[1].value = dec
indiclient.sendNewNumber(radec)
print("Position to track :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))
while (radec.getState()==PyIndi.IPS_BUSY):
    print(radec.getState())
    print("Scope Moving ", radec[0].value, radec[1].value)
    time.sleep(2)
    A=device.getNumber("EQUATORIAL_EOD_COORD")
    print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(A[0].value, A[1].value))
ra_dev, dec_dev, alt_dev, az_dev= get_current_coords(device)
print('Given ra', ra_dev, 'Given dec', dec_dev)
print('Elevation', alt_dev, 'Azimuth', az_dev)

'''

Declinations=np.linspace(0,180,181)
for i in range(len(Declinations)):
    start_time = time.perf_counter()
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
    declination=Declinations[i]
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    elapsed_time = elapsed_time/3600
    radec[0].value = radec[0].value+elapsed_time
    radec[1].value = radec[1].value-declination
    indiclient.sendNewNumber(radec)
    print("Position to track :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))
    while (radec.getState()==PyIndi.IPS_BUSY):
        print(radec.getState())
        print("Scope Moving ", radec[0].value, radec[1].value)
        time.sleep(2)
        A=device.getNumber("EQUATORIAL_EOD_COORD")
        print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(A[0].value, A[1].value))
    ra_dev, dec_dev, alt_dev, az_dev= get_current_coords(device)
    print('Given ra', ra_dev, 'Given dec', dec_dev)
    print('Elevation', alt_dev, 'Azimuth', az_dev)
    time.sleep(5)


time.sleep(5)
#try to disconnect to the server
print("Disconnecting server "+indiclient.getHost()+":"+str(indiclient.getPort()))
serverconnected=indiclient.disconnectServer()
