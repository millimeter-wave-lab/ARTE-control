# imports
import time, datetime, math
import PyIndi
import astropy.coordinates as coord
from astropy.time import Time
import numpy as np

## test parameters
refresh_time = 2    ##minutes
test_time = 3       ##hrs
iters = test_time*60//refresh_time
data = np.zeros(5)

filename = "logger_sun_pos_version_06MAYOv2"
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

## TIME_LST
# lst_time = device.getNumber("TIME_LST")
# lst_time[0].value

#from datetime import datetime
#datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#utc = datetime.utcnow()
#utc_str = utc.strftime('%Y-%m-%d %H:%M:%S')
#lst = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
######################################################
## TIME_UTC ##########################################
### for set the time
#lst_time = datetime.datetime(y, mth, d, h, m, s, 0, None)
#utc = lst_time - datetime.timedelta(0,0,0,0,0,offset)
#logger.info("Setting time to "+utc.isoformat()+ " "+str(offset))

#utc_time = device.getText("TIME_UTC")
#utc8601 = utc_time[0].text


#utc = datetime.utcnow()
#utc = datetime.datetime.strptime(utc8601, "%Y-%m-%dT%H:%M:%S")
#offset = int(float(utc_time[1].text))
#indiclient.sendNewText(utc)

#while not(utc_time) or type(utc_time)!=PyIndi.ITextVectorProperty:
   # time.sleep(0.2)
#offset = -4
utc_time = device.getText("TIME_UTC")
utc_time[0].text
#= utc.isoformat()
utc_time[1].text

print(utc_time[0].text)
print(utc_time[1].text)
#= str(offset)
indiclient.sendNewText(utc_time)


'''
### for get the time
utc8601 = utc_time[0].text
if utc_time[1].text:
    offset=int(utc_time[1].text)
else:
    offset=0

# could use dateutil.parser.parse
utc = datetime.datetime.strptime(utc8601, "%Y-%m-%dT%H:%M:%S")
utc = utc+datetime.timedelta(0,0,0,0,0,offset)

if offset < 0:
    offset = 256-offset
'''

######################################################
####### Sun parameters #######
for i in range(iters):

    t = Time.now()
    sun_pos = coord.get_sun(t)
    RA= sun_pos.ra.hour
    DEC = sun_pos.dec.deg

    # Now let's make a goto to the sun
    # Beware that ra/dec are in decimal hours/degrees
    sun = {'ra': RA, 'dec': DEC }
    ##save the data
    data[0] = time.time()
    data[1] = RA
    data[2] = DEC

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
    radec[0].value = sun['ra']
    radec[1].value = sun['dec']
    indiclient.sendNewNumber(radec)
    print("Current position for track :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))
    #im = []
    while not(radec):
        time.sleep(0.5)
        radec = device.getNumber("EQUATORIAL_EOD_COORD")
    radec[0].value = sun['ra']
    radec[1].value = sun['dec']
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

    with open(filename, 'ab') as f:
        f.write(b'\r\n')
        np.savetxt(f, [data], delimiter=',')

time.sleep(5)
#try to disconnect to the server
print("Disconnecting server "+indiclient.getHost()+":"+str(indiclient.getPort()))
serverconnected=indiclient.disconnectServer()
