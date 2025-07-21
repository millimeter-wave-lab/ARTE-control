import serial
import time

#Code that moves the mount to a desired target.

# Configuration of the serial port
mount = serial.Serial('/dev/serial/by-id/usb-FTDI_FT231X_USB_UART_D30AZJ2Y-if00-port0', 9600, timeout=1)  # Replace COM3 for your serial device.

def send_command(command):
    """Sends the command and returns the response"""
    mount.write((command + '#').encode()) #Includes the final symbol # that needs to be in every command.
    time.sleep(0.1)
    response = mount.readline().decode('latin-1').strip()
    return response

#We get parameters from the mount
get_localtime_response = send_command(f":GL")
print('Local Time',get_localtime_response)

get_currentdate_response = send_command(f":GC")
print('Current Date', get_currentdate_response)

get_utcoffset_response = send_command(f":GG")
print('UTC Offset', get_utcoffset_response)

get_siderealtime_response = send_command(f":GS")
print('Sidereal Time', get_siderealtime_response)

get_currentlatitude_response = send_command(f":Gt")
print('Current Latitude', get_currentlatitude_response)

get_currentlongitude_response = send_command(f":Gg")
print('Current Longitude', get_currentlongitude_response)

get_currentra_response = send_command(f":Gr")
print('Current Right Ascension', get_currentra_response)

get_currentdeclination_response = send_command(f":Gd")
print('Current Declination', get_currentdeclination_response)

#Set correct local time, current date, utc offset, sidereal time, current latitude and current longitude in case is necessary
'''
added_to_utc = "-3.0"
addedtoutc_response = send_command(f":SG{added_to_utc}") #0 Invalid, 1 Valid

print(addedtoutc_response)

get_utcoffset_response = send_command(f":GG")
print('UTC Offset', get_utcoffset_response)

latitude = "-33*23#"
latitude_response = send_command(f":St{latitude}") #0 Invalid, 1 Valid
print(latitude_response)
get_currentlatitude_response = send_command(f":Gt")
print('Current Latitude', get_currentlatitude_response)

longitude = "-70*32"
longitude_response = send_command(f":Sg{longitude}") #0 Invalid, 1 Valid
print(longitude_response)
get_currentlongitude_response = send_command(f":Gg")
print('Current Longitude', get_currentlongitude_response)


#local_sideral = "00:43:40"
#localsideral_response = send_command(f":SS{local_sideral}") #0 Invalid, 1 Valid
get_siderealtime_response = send_command(f":GS")
print('Sidereal Time', get_siderealtime_response)



# Set coordinates of the target (center of the galaxy)
#target_ra = "17:45:40" #HH:MM:SS
#target_dec = "-29*00:22" #DD:MM:SS

# Set coordinates of the target
target_ra = "14:31:21" #HH:MM:SS
target_dec = "-83*46:42" #DD:MM:SS

# Sends the coordinates to the mount
ra_response = send_command(f":Sr{target_ra}") #1 Valid, 0 Invalid
dec_response = send_command(f":Sd{target_dec}") #1 Dec Accepted, 0 Dec invalid

if ra_response == "1" and dec_response == "1":
    print("Coordinates loaded correctly")

    # Initiate GOTO
    move_status = send_command(":MS")

    if move_status == "0":
        print("The mount is moving to the target ...")
    elif move_status == "1":
        print("Target reached.")
    else:
        print("Error: Coordinates out of range.")
else:
    print("Error loading coordinates.")

time.sleep(30)
'''
# Close connection
mount.close()


'''
Usefull commands

SET ALTITUDE
alt_response = send_command(f":Sa{target_alt}") #0 Object within slew range, 1 Object out od slew range
target_alt="DD*MM’SS#"

SET AZIMUTH
az_response = send_command(f":Sz{target_az}") #0 Invalid, 1 Valid
target_az="DDD*MM#"

SLEW TO TARGET ALT AND AZ
move_status = send_command(":MA")

SET LATITUDE
latitude_response = send_command(f":St{latitude}") #0 Invalid, 1 Valid
latitude = "DD*MM#"

SET LONGITUDE
longitude_response = send_command(f":Sg{longitude}") #0 Invalid, 1 Valid
longitude = "DDD*MM"

SET LOCAL SIDERAL TIME
localsideral_response = send_command(f":SS{local_sideral}") #0 Invalid, 1 Valid
local_sideral = "HH:MM:SS"

SET LOCAL TIME
locaLtime_response = send_command(f":SL{local_time}") #0 Invalid, 1 Valid
local_time = "HH:MM:SS"

SET ADDED TIME TO UTC
addedtoutc_response = send_command(f":SG{added_to_utc}") #0 Invalid, 1 Valid
added_to_utc = "HH.H"

SET MINIMUM OBJECT ELEVATION LIMIT
elevationlimit_response = send_command(f":Sh{elevation_limit}") #0 Invalid, 1 Valid
elevation_limit = "DD#"




:GA# Get Telescope Altitude
Returns: sDD*MM# or sDD*MM’SS#
The current scope altitude. The returned format depending on the current precision setting.

:Ga# Get Local Telescope Time In 12 Hour Format
Returns: HH:MM:SS#
The time in 12 format

:GC# Get current date.
Returns: MM/DD/YY#
The current local calendar date for the telescope.

:Gc# Get Calendar Format
Returns: 12# or 24#
Depending on the current telescope format setting.

:GD# Get Telescope Declination.
Returns: sDD*MM# or sDD*MM’SS#
Depending upon the current precision setting for the telescope.

:Gd# Get Currently Selected Object/Target Declination
Returns: sDD*MM# or sDD*MM’SS#
Depending upon the current precision setting for the telescope

:GG# Get UTC offset time
Returns: sHH# or sHH.H#
The number of decimal hours to add to local time to convert it to UTC. If the number is a whole number the
sHH# form is returned, otherwise the longer form is return. On Autostar and LX200GPS, the daylight savings
setting in effect is factored into returned value.

:Gg# Get Current Site Longitude
Returns: sDDD*MM#
The current site Longitude. East Longitudes are expressed as negative

:GL# Get Local Time in 24 hour format
Returns: HH:MM:SS#
The Local Time in 24-hour Format

:Gr# Get current/target object RA
Returns: HH:MM.T# or HH:MM:SS
Depending upon which precision is set for the telescope

:GR# Get Telescope RA
Returns: HH:MM.T# or HH:MM:SS#
Depending which precision is set for the telescope

:GS# Get the Sidereal Time
Returns: HH:MM:SS#
The Sidereal Time as an ASCII Sexidecimal value in 24 hour format

:Gt# Get Current Site Latitdue
Returns: sDD*MM#
The latitude of the current site. Positive inplies North latitude

:GZ# Get telescope azimuth
Returns: DDD*MM#T or DDD*MM’SS#
The current telescope Azimuth depending on the selected precision.


H – Time Format Command
:H# Toggle Between 24 and 12 hour time format
Returns: Nothing
'''


