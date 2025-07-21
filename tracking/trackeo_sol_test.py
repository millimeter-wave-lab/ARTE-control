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
'''
geographic_pos = device.getNumber("GEOGRAPHIC_COORD")
geographic_pos[0].value   # LAT Site latitude (-90 to +90), degrees +N
geographic_pos[1].value   # LONG Site longitude (0 to 360), degrees +E
geographic_pos[2].value   # ELEV Site elevation, meters
indiclient.sendNewNumber(geographic_pos)

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
    return ra * u.hour, dec * u.deg, alt, az

def get_altz_coords(ra, dec):
    radec = SkyCoord(ra=ra*u.hour, dec=dec*u.deg, frame='icrs')
    # Calan GEOGRAPHIC_COORD
    calan_obs = EarthLocation(lat=-33.3961*u.deg, lon=-70.537*u.deg, height=867*u.m)
    now = Time.now()
    altaz_frame = AltAz(obstime=now,location=calan_obs)
    altaz = radec.transform_to(altaz_frame)
    alt = altaz.alt.deg
    az = altaz.az.deg
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

def find_azimuth_at_altitude(desired_altitude):
    """Find the azimuth where the altitude is 30 degrees and galactic latitude b = 0."""
    galactic_latitude = 0 * u.deg  # Galactic latitude b = 0 (galactic equator)
    Azimuths=[]
    # 3. Get the current time
    

    # 5. Iterate through different galactic longitudes
    for l in np.linspace(0, 360, 100):  # Sweep galactic longitude from 0 to 360 degrees
        # Define the SkyCoord in Galactic coordinates (l, b)
        galactic_coord = SkyCoord(l=l*u.deg, b=galactic_latitude, frame='galactic')
        observation_time = Time.now()
        # 4. Define the AltAz frame using the observer's location and time
        calan_obs = EarthLocation(lat=-33.3961*u.deg, lon=-70.537*u.deg, height=867*u.m)
        altaz_frame = AltAz(obstime=
observation_time, location=calan_obs)
        # 6. Convert the galactic coordinates to Alt-Az coordinates
        altaz_coord = galactic_coord.transform_to(altaz_frame)
        
        # 7. Check if the altitude is close to the desired altitude of 30 degrees
        if abs(altaz_coord.alt.deg - desired_altitude) < 0.1:
            Azimuths.append(altaz_coord.az.deg)
            # 8. If altitude is approximately 30 degrees, return the corresponding azimuth
    return Azimuths

def choose_azimuths(Azimuths, az_milky):
    if abs(Azimuths[0]-az_milky) <= abs(Azimuths[1]-az_milky):
        return Azimuths[0]
    else:
        return Azimuths[1]

######################################################
####### Milky way #######
for i in range(iters):
    print('iters',i)

    GC = SkyCoord.from_name('Galactic Center')
    A = GC.galactic.l.value # lon 0 360
    D = GC.galactic.b.value # lat -90 90
    ra_hr   = GC.ra.hour
    dec_deg  = GC.dec.deg
    #ra_hr= 6.45
    #dec_deg= -52.8
    
    MW_centre = {'ra': ra_hr, 'dec': dec_deg }

    '''
    t = Time.now()
    print('time_now',t)
    sun_pos = coord.get_sun(t)
    RA= sun_pos.ra.hour
    DEC = sun_pos.dec.deg
    print("Current position for track :\n"+"RA: {:.4f} DEC: {:.4f}".format(RA, DEC))
    # Now let's make a goto to the sun
    # Beware that ra/dec are in decimal hours/degrees
    sun = {'ra': RA, 'dec': DEC }
    ##save the data
    data[0] = time.time()
    data[1] = RA
    data[2] = DEC
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
    # radec = device.getNumber("TARGET_EOD_COORD")
    print("Current position from device :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))
    #print("Current position for track :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))
    #im = []
    while not(radec):
        time.sleep(0.5)
        radec = device.getNumber("EQUATORIAL_EOD_COORD")
    radec[0].value = MW_centre['ra']
    radec[1].value = MW_centre['dec']
    #radec[0].value = 9.3
    #radec[1].value = -50.1
    indiclient.sendNewNumber(radec)
    print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))
    # and wait for the scope has finished moving
    data[3] = radec[0].value
    data[4] = radec[1].value
    #print(data)
    while (radec.getState()==PyIndi.IPS_BUSY):
        print(radec.getState())
        print("Scope Moving ", radec[0].value, radec[1].value)
        time.sleep(2)
        A=device.getNumber("EQUATORIAL_EOD_COORD")
        print("Current positioA :\n"+"RA: {:.4f} DEC: {:.4f}".format(A[0].value, A[1].value))
    ra, dec, alt, az= get_current_coords(device)
    print('Given ra', ra, 'Given dec', dec)
    print('Elevation', alt.deg, 'Azimuth', az.deg)

    with open(filename, 'ab') as f:
        f.write(b'\r\n')
        np.savetxt(f, [data], delimiter=',')

    ra2,dec2=give_alt_az_coords_in_equatorial(alt, az)
    print('Primeros',alt,az)
    print('Transformed ra', ra2,'Transformed dec', dec2)
    limit_angle=90
    limit_altitude=limit_angle*u.deg
    while(True):
        alt_milky, az_milky = get_altz_coords(MW_centre['ra'], MW_centre['dec'])
        if alt_milky < limit_angle:
            alt=limit_altitude
            Azimuths=find_azimuth_at_altitude(limit_angle)
            if Azimuths==[]:
                #Put here the command for the moment where all the galactic plane is at lower elevation than the limit altitude.
                alt_zenith= 90*u.deg
                az_zenith= az_milky*u.deg
                ra_zenith, dec_zenith= give_alt_az_coords_in_equatorial(alt_zenith, az_zenith)
                radec_new = device.getNumber("EQUATORIAL_EOD_COORD")
                radec_new[0].value = ra_zenith
                radec_new[1].value = dec_zenith
                indiclient.sendNewNumber(radec_new)
                while (radec_new.getState()==PyIndi.IPS_BUSY):
                    print(radec_new.getState())
                    print("Scope Moving ", radec_new[0].value, radec_new[1].value)
                    time.sleep(2)
                time.sleep(60)
            else:
                az=choose_azimuths(Azimuths, az_milky)    
                print('Segundos',alt,az)
                ra2,dec2=give_alt_az_coords_in_equatorial(alt, az*u.deg)
                print('Transformed ra', ra2,'Transformed dec', dec2)
                radec_new = device.getNumber("EQUATORIAL_EOD_COORD")
                radec_new[0].value = ra2
                radec_new[1].value = dec2
                indiclient.sendNewNumber(radec_new)
                while (radec_new.getState()==PyIndi.IPS_BUSY):
                    print(radec_new.getState())
                    print("Scope Moving ", radec_new[0].value, radec_new[1].value)
                    time.sleep(2)
                time.sleep(60)
        if alt_milky >= limit_angle:
            time.sleep(60)
            print('Waiting')

time.sleep(5)
#try to disconnect to the server
print("Disconnecting server "+indiclient.getHost()+":"+str(indiclient.getPort()))
serverconnected=indiclient.disconnectServer()
