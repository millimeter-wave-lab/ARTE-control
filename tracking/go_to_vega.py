import PyIndi
import time, datetime, math
import sys
import threading
import astropy.coordinates as coord
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
import astropy.coordinates as coord

class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
    def newDevice(self, d):
        pass
    def newProperty(self, p):
        pass
    def removeProperty(self, p):
        pass
    def newBLOB(self, bp):
        global blobEvent
        print("new BLOB ", bp.name)
        blobEvent.set()
        pass
    def newSwitch(self, svp):
        pass
    def newNumber(self, nvp):
        pass
    def newText(self, tvp):
        pass
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        pass
    def serverConnected(self):
        pass
    def serverDisconnected(self, code):
        pass

# connect the server
indiclient=IndiClient()
indiclient.setServer("localhost",7624)

if (not(indiclient.connectServer())):
    print("Connecting server "+indiclient.getHost()+":"+str(indiclient.getPort()))
    serverconnected=indiclient.connectServer()
    if(serverconnected):
        print('Server successfully connected')
    else:
        raise Exception('Cant connect to the server')

# connect the scope
telescope="LX200 Autostar"
device_telescope=None
telescope_connect=None

# get the telescope device
device_telescope=indiclient.getDevice(telescope)
while not(device_telescope):
    time.sleep(0.5)
    device_telescope=indiclient.getDevice(telescope)

# wait CONNECTION property be defined for telescope
telescope_connect=device_telescope.getSwitch("CONNECTION")
while not(telescope_connect):
    time.sleep(0.5)
    telescope_connect=device_telescope.getSwitch("CONNECTION")
# if the telescope device is not connected, we do connect it if not(device_telescope.isConnected()):
    # Property vectors are mapped to iterable Python objects
    # Hence we can access each element of the vector using Python indexing
    # each element of the "CONNECTION" vector is a ISwitch
    telescope_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
    telescope_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
    indiclient.sendNewSwitch(telescope_connect) # send this new value to the device

# Now let's make a goto to vega
# Beware that ra/dec are in decimal hours/degrees
# We want to set the ON_COORD_SET switch to engage tracking after goto
# device.getSwitch is a helper to retrieve a property vector
telescope_on_coord_set=device_telescope.getSwitch("ON_COORD_SET")
while not(telescope_on_coord_set):
    time.sleep(0.5)
    telescope_on_coord_set=device_telescope.getSwitch("ON_COORD_SET")
    #time.sleep(60)
# the order below is defined in the property vector, look at the standard Properties page
# or enumerate them in the Python shell when you're developing your program
telescope_on_coord_set[0].s=PyIndi.ISS_OFF  # TRACK
telescope_on_coord_set[1].s=PyIndi.ISS_ON # SLEW
telescope_on_coord_set[2].s=PyIndi.ISS_OFF # SYNC
indiclient.sendNewSwitch(telescope_on_coord_set)

'''
#This section allows to adjust the hour of the mount
#We ask for the actual hour in UCT time
t = Time.now()
print('time now', t)
#Then we ask for the time of the mount
utc_time = device_telescope.getText("TIME_UTC")
print('Device', utc_time[0].text)
print('Device', utc_time[1].text)
#We set the hour to be the UCT time from above
utc_time[0].text=str(t.value.year)+'-'+str(t.value.month).zfill(2)+'-'+str(t.value.day).zfill(2)+'T'+str(t.value.hour).zfill(2)+':'+str(t.value.minute).zfill(2)+':'+str(t.value.second).zfill(2)
utc_time[1].text='-3' #Summer time in Santiago, when is winter time is '-4'
#And we send it to the mount
indiclient.sendNewText(utc_time)
#Finally we ask again for the time of the mount to check that was successfully changed 
utc_time2 = device_telescope.getText("TIME_UTC")
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

# We set the desired coordinates
telescope_radec=device_telescope.getNumber("EQUATORIAL_EOD_COORD")
while not(telescope_radec):
    time.sleep(0.5)
    telescope_radec=device_telescope.getNumber("EQUATORIAL_EOD_COORD")
t = Time.now()
sun_pos = coord.get_sun(t)
RA_sun= sun_pos.ra.hour
print(RA_sun)
DEC_sun = sun_pos.dec.deg
print(DEC_sun)
sun={'ra': RA_sun, 'dec': DEC_sun }
telescope_radec[0].value=sun['ra']
telescope_radec[1].value=sun['dec']
#telescope_radec[0].value=15.3328
#telescope_radec[1].value=-16.396111
indiclient.sendNewNumber(telescope_radec)
print(telescope_radec[0].value, telescope_radec[1].value)
# and wait for the scope has finished moving
while (telescope_radec.getState()==PyIndi.IPS_BUSY):
    print("Scope Moving ", telescope_radec[0].value, telescope_radec[1].value)
    time.sleep(2)
    

RA_telescope, DEC_telescope, altitude_telescope, azimuth_telescope = get_current_coords(device_telescope)

print('Actual position','RA:',RA_telescope,'DEC:', DEC_telescope,'Altitude:', altitude_telescope.degree,'Azimuth:', azimuth_telescope.degree)

final_coordinates=device_telescope.getNumber("EQUATORIAL_EOD_COORD")
print(final_coordinates[0].value, final_coordinates[1].value)

