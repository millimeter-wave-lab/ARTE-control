# imports
import time, datetime, math
import PyIndi
import astropy.coordinates as coord
from astropy.time import Time
import numpy as np

# parameters
INDI_SERVER_HOST="localhost"
INDI_SERVER_PORT=7624
TELESCOPE_DEVICE="LX200 Autostar"#"EQMod Mount"

refresh_time = 2    ##minutes
test_time = 1       ##hrs
iters = test_time*60//refresh_time



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
        device_connect = device.getSwitch("CONNECTION")
if not(device.isConnected()):
    device_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
    device_connect[1].s = PyIndi.ISS_OFF # the "DISCONNECT" switch
    indiclient.sendNewSwitch(device_connect)
if(device.isConnected()):
    print('Device successfully connected')
time.sleep(0.5)

if(not device.isConnected()):
    indiclient.disconnectServer()
    server_proc.terminate()
    raise Exception('Cant connect to the mount!')

################################################
#x = device.getSwitch('TELESCOPE_SLEW_RATE')
#x.getState()
"""
x[0].s=PyIndi.ISS_OFF # SLEW_GUIDE
x[1].s=PyIndi.ISS_OFF # SLEW_CENTERING
x[2].s=PyIndi.ISS_OFF # SLEW_FIND
x[3].s=PyIndi.ISS_ON # SLEW_MAX
indiclient.sendNewSwitch(x)

d = device.getSwitch('TELESCOPE_PARK')
d[0].s=PyIndi.ISS_ON # PARK
d[1].s=PyIndi.ISS_OFF # UNPARK
indiclient.sendNewSwitch(d)

tel_motion_ns = device.getSwitch('TELESCOPE_MOTION_NS')
tel_motion_ns[0].s=PyIndi.ISS_ON # MOTION_NORTH
tel_motion_ns[1].s=PyIndi.ISS_OFF # MOTION_SOUTH
indiclient.sendNewSwitch(tel_motion_ns)

tel_motion_we = device.getSwitch('TELESCOPE_MOTION_WE')
tel_motion_we[0].s=PyIndi.ISS_OFF # MOTION_WEST
tel_motion_we[1].s=PyIndi.ISS_ON # MOTION_EAST
indiclient.sendNewSwitch(tel_motion_we)

"""
##################################################
## GEOGRAPHIC_COORD
geographic_pos = device.getNumber("GEOGRAPHIC_COORD")
geographic_pos[0].value  # LAT Site latitude (-90 to +90), degrees +N
geographic_pos[1].value  # LONG Site longitude (0 to 360), degrees +E
geographic_pos[2].value  # ELEV Site elevation, meters
#indiclient.sendNewNumber(geographic_pos)

tel_on_coord_set = device.getSwitch("ON_COORD_SET")
device_abort = device.getSwitch("TELESCOPE_ABORT_MOTION")
#device_abort[0].s=PyIndi.ISS_ON  # ABORT MOTION

##set the parameters
tel_on_coord_set[0].s=PyIndi.ISS_OFF  # TRACK
tel_on_coord_set[1].s=PyIndi.ISS_ON # SLEW
tel_on_coord_set[2].s=PyIndi.ISS_OFF # SYNC
indiclient.sendNewSwitch(tel_on_coord_set)

##get coordinates
radec=device.getNumber("EQUATORIAL_EOD_COORD")
print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))

#for i in range(iters):
    
'''
tel_motion_we = device.getSwitch('TELESCOPE_MOTION_WE')
tel_motion_we[0].s=PyIndi.ISS_ON # MOTION_WEST
tel_motion_we[1].s=PyIndi.ISS_OFF # MOTION_EAST
indiclient.sendNewSwitch(tel_motion_we)
'''
while(True):
    tel_motion_ns = device.getSwitch('TELESCOPE_MOTION_NS')
    tel_motion_ns[0].s=PyIndi.ISS_ON # MOTION_NORTH
    tel_motion_ns[1].s=PyIndi.ISS_OFF # MOTION_SOUTH
    indiclient.sendNewSwitch(tel_motion_ns)
    radec=device.getNumber("EQUATORIAL_EOD_COORD")
    print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))

#device_abort[0].s=PyIndi.ISS_ON  # ABORT MOTION
#indiclient.sendNewSwitch(device_abort)

'''
######################################################
## TIME_LST
lst_time = device.getNumber("TIME_LST")
lst_time[0].value
local_t = datetime.datetime.now()
lst_time[0].setValue = local_t
indiclient.sendNewNumber(lst_time)

## TIME_UTC
utc_time = device.getText("TIME_UTC")
#utc_time[0].value
t = datetime.now().isoformat()
utc_time = t
indiclient.sendNewNumber(utc_time)
#utc_time[0].setValue = t
######################################################

###################################################################
#### Test to slew to the sun ####
t = Time.now()
sun_pos = coord.get_sun(t)
RA= sun_pos.ra.hour
DEC = sun_pos.dec.deg

# Now let's make a goto to the sun
# Beware that ra/dec are in decimal hours/degrees
sun = {'ra': RA, 'dec': DEC }
radec[0].value = sun['ra']
radec[1].value = sun['dec']
indiclient.sendNewNumber(radec)
print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))
#### End test to slew to the sun ####
###########################################################################



radec[0].value = radec[0].value 
radec[1].value = radec[1].value - 5
#time.sleep(0.5)
indiclient.sendNewNumber(radec)
radec=device.getNumber("EQUATORIAL_EOD_COORD")
print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))
time.sleep(5)
radec[0].value = radec[0].value 
radec[1].value = radec[1].value + 5
#time.sleep(0.5)
indiclient.sendNewNumber(radec)
radec=device.getNumber("EQUATORIAL_EOD_COORD")
print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))
###########################################################################
'''

time.sleep(5)
#try to disconnect to the server
print("Disconnecting server "+indiclient.getHost()+":"+str(indiclient.getPort()))
serverconnected=indiclient.disconnectServer()
