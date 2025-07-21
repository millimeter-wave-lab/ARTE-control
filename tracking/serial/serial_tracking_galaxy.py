import serial
import time
import astropy.coordinates as coord
from astropy.time import Time
import numpy as np
from astropy.coordinates import (SkyCoord, Distance, Galactic, 
                                 EarthLocation, AltAz,ICRS)
from astropy import units as u


#Code that moves the mount to a desired target.

# Configuration of the serial port
mount = serial.Serial('/dev/serial/by-id/usb-FTDI_FT231X_USB_UART_D30B0FM5-if00-port0', 9600, timeout=1)  # Replace COM3 for your serial device.

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


'''
def decimaltohourformat(ra_or_dec, true_if_ra_false_if_dec):
    #Converts ra in hours from decimal to time format
    hour=int(ra_or_dec)
    ra_or_dec_min=(ra_or_dec-hour)*60
    minute=abs(int(ra_or_dec_min))
    ra_or_dec_sec=(abs(ra_or_dec_min)-minute)*60
    second=abs(round(ra_or_dec_sec))
    if true_if_ra_false_if_dec == True:
        ra_or_dec_time=str(hour).zfill(2)+":"+str(minute).zfill(2)+":"+str(second).zfill(2)
    elif true_if_ra_false_if_dec==False:
        ra_or_dec_time=str(hour).zfill(2)+"*"+str(minute).zfill(2)+":"+str(second).zfill(2)
    return ra_or_dec_time

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
    # 5. Iterate through different galactic longitudes
    for l in np.linspace(0, 360, 360):  # Sweep galactic longitude from 0 to 360 degrees
        # Define the SkyCoord in Galactic coordinates (l, b)
        galactic_coord = SkyCoord(l=l*u.deg, b=galactic_latitude, frame='galactic')
        observation_time = Time.now()
        # 4. Define the AltAz frame using the observer's location and time
        calan_obs = EarthLocation(lat=-33.3961*u.deg, lon=-70.537*u.deg, height=867*u.m)
        altaz_frame = AltAz(obstime=observation_time, location=calan_obs)
        # 6. Convert the galactic coordinates to Alt-Az coordinates
        altaz_coord = galactic_coord.transform_to(altaz_frame)
        # 7. Check if the altitude is close to the desired altitude of 30 degrees
        if abs(altaz_coord.alt.deg - desired_altitude) < 0.5:
            Azimuths.append(altaz_coord.az.deg)
            # 8. If altitude is approximately 30 degrees, return the corresponding azimuth
    return Azimuths

def choose_azimuths(Azimuths, az_milky):
    dif_with_milky=[]
    for i in range(len(Azimuths)):
        dif_az=abs(abs(Azimuths[i])-abs(az_milky))
        dif_with_milky.append(dif_az)
    index_min=np.argmin(dif_with_milky)
    return Azimuths[index_min]

def movemount(target_ra, target_dec):
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

def lowerelevationthanmilky(limit_angle, az_milky):
    print("Entro a lowerthanmilky")
    limit_altitude=limit_angle*u.deg
    alt=limit_altitude
    Azimuths=find_azimuth_at_altitude(limit_angle)
    print(Azimuths)
    if Azimuths==[]:
        print("Azimuth vacio")
        alt_zenith= 90*u.deg
        az_zenith= az_milky*u.deg
        ra_zenith, dec_zenith= give_alt_az_coords_in_equatorial(alt_zenith, az_zenith)
        target_ra_zenith = decimaltohourformat(ra_zenith, True)
        target_dec_zenith = decimaltohourformat(dec_zenith, False)
        print(target_ra_zenith, target_dec_zenith)
        movemount(target_ra_zenith, target_dec_zenith)
    elif len(Azimuths)==1:
        print("Solo un azimuth")
        az=Azimuths[0]
        ra2,dec2=give_alt_az_coords_in_equatorial(alt, az*u.deg)
        target_ra_plane = decimaltohourformat(ra2, True)
        target_dec_plane = decimaltohourformat(dec2, False)
        print(target_ra_plane, target_dec_plane)
        movemount(target_ra_plane, target_dec_plane)
    else:
        print("Dos azimiths")
        az=choose_azimuths(Azimuths, az_milky)    
        ra2,dec2=give_alt_az_coords_in_equatorial(alt, az*u.deg)
        target_ra_plane = decimaltohourformat(ra2, True)
        target_dec_plane = decimaltohourformat(dec2, False)
        print(target_ra_plane, target_dec_plane)
        movemount(target_ra_plane, target_dec_plane)

# Set coordinates of the target (center of the galaxy)
GC = SkyCoord.from_name('Galactic Center')
A = GC.galactic.l.value # lon 0 360
D = GC.galactic.b.value # lat -90 90
ra_hr   = GC.ra.hour
dec_deg  = GC.dec.deg 

#Sirio
#ra_hr=6.7708
#dec_deg=-16.751667


target_ra_milky = decimaltohourformat(ra_hr, True) #HH:MM:SS
target_dec_milky = decimaltohourformat(dec_deg, False) #DD:MM:SS

print("Target_ra", target_ra_milky)
print("Target_dec", target_dec_milky)


alt_milky, az_milky = get_altz_coords(ra_hr, dec_deg)
limit_angle=30

if alt_milky > limit_angle:
    movemount(target_ra_milky, target_dec_milky)
    time.sleep(60)
else:
    lowerelevationthanmilky(limit_angle, az_milky)
    time.sleep(60)

print("Sale del primer if")
while(True):
    alt_milky, az_milky = get_altz_coords(ra_hr, dec_deg)
    if alt_milky >= limit_angle: 
        get_selected_ra = send_command(f":Gr")
        print("Selected ra", get_selected_ra)
        get_selected_dec = send_command(f":Gd")
        print("Selected dec", get_selected_dec)
        print(get_selected_ra[:5],target_ra_milky[:5])
        if get_selected_ra[:5]==target_ra_milky[:5]:
            time.sleep(300)
        else:
            movemount(target_ra_milky, target_dec_milky)
            time.sleep(300)
    else:
        lowerelevationthanmilky(limit_angle, az_milky)
        time.sleep(300)
     
   
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


