# imports
import time, datetime, math
import PyIndi
import numpy as np
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz

# indi parameters
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

######## End server and device connection ########
#####################################



# We want to set the ON_COORD_SET switch to engage tracking after goto
# device.getSwitch is a helper to retrieve a property vector
telescope_on_coord_set = device.getSwitch("ON_COORD_SET")
while not(telescope_on_coord_set):
    time.sleep(0.5)
    telescope_on_coord_set = device.getSwitch("ON_COORD_SET")

####### Milky Way parameters #######
# Now let's make a goto to  MW_centre
# Beware that ra/dec are in decimal hours/degrees
GC = SkyCoord.from_name('Galactic Center')
A = GC.galactic.l.value # lon 0 360
D = GC.galactic.b.value # lat -90 90
ra_deg   = GC.ra.deg
dec_deg  = GC.dec.deg
MW_centre = {'ra': ( ra_deg * 24.0)/360.0, 'dec': - dec_deg }

dec_deg2  = GC.dec.deg + 5
MW_offset = {'ra': ( ra_deg * 24.0)/360.0, 'dec': - dec_deg2 }

###### ellipse parameters 1.5 GHz #######
a = 73.0/2
be = 26.0/2
epsilon = 0.01 #0.01
ref = 30*u.deg

# define ellipse on the tangent plane
# ellipse with center coordinates (A,D)
# (A,D) galactic longitude and latitude
anxi = np.arange(A-a, A+a, epsilon)
aneta = be * np.sqrt(1 - (anxi-A)**2 / a**2)

angle_xi =  np.concatenate((anxi, anxi))
angle_eta = D + np.concatenate((-aneta, aneta))

XI = np.tan(angle_xi / 180.0 * np.pi)   #rad gal
ETA = np.tan(angle_eta / 180.0 * np.pi) #rad gal

for xi, eta in zip(XI, ETA):

    alpha = np.arctan( xi /( np.cos(D/ 180.0 * np.pi) - eta * np.sin(D/ 180.0 * np.pi)) ) + A/ 180.0 * np.pi
    delta = np.arctan((eta * np.cos(D/ 180.0 * np.pi) + np.sin(D/ 180.0 * np.pi)) * np.sin(alpha - A/ 180.0 * np.pi) / xi)

    alpha_d = math.degrees(alpha) #deg gal
    delta_d = math.degrees(delta) #deg gal

    gal = SkyCoord(l = alpha_d*u.deg, b = delta_d*u.deg, frame ='galactic')
    eq = gal.fk5
    calan_obs = EarthLocation(lat=-33.3961*u.deg, lon=-70.537*u.deg, height=867*u.m) #GEOGRAPHIC_COORD

    now = Time.now()
    altaz_frame = AltAz(obstime=now,location=calan_obs)
    eq_to_altaz = eq.transform_to(altaz_frame)

    Altitud = eq_to_altaz.alt
    Azimuth = eq_to_altaz.az




#TELESCOPE_ABORT_MOTION
#TELESCOPE_TRACK_RATE
#TELESCOPE_SLEW_RATE
#TELESCOPE_PARK should be the zenit
#################### Define Tracking ##################

    while(Altitud > ref):

        # the order below is defined in the property vector, look at the standard Properties page
        telescope_on_coord_set[0].s = PyIndi.ISS_ON  # TRACK we want track de MW
        telescope_on_coord_set[1].s = PyIndi.ISS_OFF # SLEW
        telescope_on_coord_set[2].s = PyIndi.ISS_OFF # SYNC
        indiclient.sendNewSwitch(telescope_on_coord_set)

        # We set the desired coordinates
        telescope_radec =  device.getNumber("EQUATORIAL_EOD_COORD")
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
            time.sleep(2)
    while not(Altitud > ref):

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


############################
################end  edition #######

time.sleep(5)
#try to disconnect to the server
print("Disconnecting server "+indiclient.getHost()+":"+str(indiclient.getPort()))
serverconnected=indiclient.disconnectServer()



