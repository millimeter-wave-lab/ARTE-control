# imports
import time, datetime, math
import PyIndi
from astropy import units as u
from astropy.coordinates import SkyCoord

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

######## End server and device connection ########
#####################################

# Now let's make a goto to  MW_centre
# Beware that ra/dec are in decimal hours/degrees
 #AR 17 45 40.04
 #Dec -29° 00 28.1
 ra_deg = 15*(17+45./60+40.04/3600)
 dec_deg = -29-28.1/360
 MW_centre = {'ra': ( ra_deg * 24.0)/360.0, 'dec': - dec_deg }

# We want to set the ON_COORD_SET switch to engage tracking after goto
# device.getSwitch is a helper to retrieve a property vector
telescope_on_coord_set = device_telescope.getSwitch("ON_COORD_SET")
while not(telescope_on_coord_set):
    time.sleep(0.5)
    telescope_on_coord_set = device_telescope.getSwitch("ON_COORD_SET")

# the order below is defined in the property vector, look at the standard Properties page
# or enumerate them in the Python shell when you're developing your program
telescope_on_coord_set[0].s = PyIndi.ISS_ON  # TRACK we want track de MW
telescope_on_coord_set[1].s = PyIndi.ISS_OFF # SLEW
telescope_on_coord_set[2].s = PyIndi.ISS_OFF # SYNC
indiclient.sendNewSwitch(telescope_on_coord_set)
# We set the desired coordinates

telescope_radec =  device_telescope.getNumber("EQUATORIAL_EOD_COORD")
while not(telescope_radec):
    time.sleep(0.5)
    telescope_radec = device_telescope.getNumber("EQUATORIAL_EOD_COORD")
telescope_radec[0].value = MW_centre['ra']
telescope_radec[1].value = MW_centre['dec']
indiclient.sendNewNumber(telescope_radec)
# and wait for the scope has finished moving
while (telescope_radec.s==PyIndi.IPS_BUSY):
    print("Scope Moving ", telescope_radec[0].value, telescope_radec[1].value)
    time.sleep(2)



while (altitud>15):
################end  edition #######



######################################
######################################
'''
# Now let's make a goto to vega
# Beware that ra/dec are in decimal hours/degrees
ra 18 h 36 m 56.3364 s
dec +38°47′01.291″
vega={'ra': (279.23473479 * 24.0)/360.0, 'dec': +38.78368896 }

# We want to set the ON_COORD_SET switch to engage tracking after goto
# device.getSwitch is a helper to retrieve a property vector
telescope_on_coord_set=device_telescope.getSwitch("ON_COORD_SET")
while not(telescope_on_coord_set):
    time.sleep(0.5)
    telescope_on_coord_set=device_telescope.getSwitch("ON_COORD_SET")
# the order below is defined in the property vector, look at the standard Properties page
# or enumerate them in the Python shell when you're developing your program
telescope_on_coord_set[0].s=PyIndi.ISS_ON  # TRACK
telescope_on_coord_set[1].s=PyIndi.ISS_OFF # SLEW
telescope_on_coord_set[2].s=PyIndi.ISS_OFF # SYNC
indiclient.sendNewSwitch(telescope_on_coord_set)
# We set the desired coordinates




telescope_radec=device_telescope.getNumber("EQUATORIAL_EOD_COORD")
while not(telescope_radec):
    time.sleep(0.5)
    telescope_radec=device_telescope.getNumber("EQUATORIAL_EOD_COORD")
telescope_radec[0].value=vega['ra']
telescope_radec[1].value=vega['dec']
indiclient.sendNewNumber(telescope_radec)
# and wait for the scope has finished moving
while (telescope_radec.s==PyIndi.IPS_BUSY):
    print("Scope Moving ", telescope_radec[0].value, telescope_radec[1].value)
    time.sleep(2)



###################################################
###################################################
################# OTRO
 # Now let's make a goto to the target
    # Beware that ra/dec are in decimal hours/degrees
    target={'ra': (float(RA) * 24.0)/360.0, 'dec': float(DEC) }

    # We want to set the ON_COORD_SET switch to engage tracking after goto
    # device.getSwitch is a helper to retrieve a property vector
    telescope_on_coord_set=device_telescope.getSwitch("ON_COORD_SET")
    while not(telescope_on_coord_set):
        time.sleep(0.5)
        telescope_on_coord_set=device_telescope.getSwitch("ON_COORD_SET")
    # the order below is defined in the property vector, look at the standard Properties page
    # or enumerate them in the Python shell when you're developing your program
    if not sync:
        telescope_on_coord_set[0].s=PyIndi.ISS_ON  # TRACK
        telescope_on_coord_set[1].s=PyIndi.ISS_OFF # SLEW
        telescope_on_coord_set[2].s=PyIndi.ISS_OFF # SYNC
    else:
        telescope_on_coord_set[0].s=PyIndi.ISS_OFF  # TRACK
        telescope_on_coord_set[1].s=PyIndi.ISS_OFF # SLEW
        telescope_on_coord_set[2].s=PyIndi.ISS_ON # SYNC
    indiclient.sendNewSwitch(telescope_on_coord_set)
    # We set the desired coordinates
    telescope_radec=device_telescope.getNumber("EQUATORIAL_EOD_COORD")
    while not(telescope_radec):
        time.sleep(0.5)
        telescope_radec=device_telescope.getNumber("EQUATORIAL_EOD_COORD")
    telescope_radec[0].value=target['ra']
    telescope_radec[1].value=target['dec']
    indiclient.sendNewNumber(telescope_radec)
    # and wait for the scope has finished moving (if not syncing)
    if not sync:
        while (telescope_radec.s==PyIndi.IPS_BUSY):
            print(f"Scope Moving: RA {Angle(telescope_radec[0].value*u.hour).to_string(unit=u.hour)}, DEC {Angle(telescope_radec[1].value*u.deg).to_string(unit=u.degree)}\r", end="")
            time.sleep(0.25)
        print(f"Scope Moving: RA {Angle(telescope_radec[0].value*u.hour).to_string(unit=u.hour)}, DEC {Angle(telescope_radec[1].value*u.deg).to_string(unit=u.degree)}")
    else:
        print(f"Scope Synced: RA {Angle(telescope_radec[0].value*u.hour).to_string(unit=u.hour)}, DEC {Angle(telescope_radec[1].value*u.deg).to_string(unit=u.degree)}")
    return

######################################
######################################
'''













####### set here some properties for track ######

tel_on_coord_set = device.getSwitch("ON_COORD_SET")

##set the parameters
tel_on_coord_set[0].s=PyIndi.ISS_ON  # TRACK
tel_on_coord_set[1].s=PyIndi.ISS_OFF # SLEW
tel_on_coord_set[2].s=PyIndi.ISS_OFF # SYNC
indiclient.sendNewSwitch(tel_on_coord_set)

##get coordinates
radec=device.getNumber("EQUATORIAL_EOD_COORD")
print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))



####### add here tracker code ######















radec[0].value = radec[0].value - 10.01
radec[1].value = radec[1].value -3
indiclient.sendNewNumber(radec)

print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))
