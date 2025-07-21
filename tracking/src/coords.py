from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
import astropy.coordinates as coord

import numpy as np
import math
import importlib

import logging
importlib.reload(logging)
from logging import *

directory = 'tracking_logs'

def get_current_coords(device):
    radec =  device.getNumber("EQUATORIAL_EOD_COORD")
    
    ra = radec[0].value
    dec = radec[1].value
    
    radec = SkyCoord(ra=ra*u.hour, dec=dec*u.deg, frame='icrs')
    ##### SOLO FALTA TRANSFORMAR ESTO A ALTAZ

    calan_obs = EarthLocation(lat=-33.3961*u.deg, lon=-70.537*u.deg, height=867*u.m) #GEOGRAPHIC_COORD

    now = Time.now()
    altaz_frame = AltAz(obstime=now,location=calan_obs)

    altaz = radec.transform_to(altaz_frame)
    
    alt = altaz.alt
    az = altaz.az

    return ra * u.hour, dec * u.deg, alt, az

def check_abs_lap(absolute_lap, min_abs_lap, max_abs_lap):
    if type(absolute_lap) != float:
        return "no record"
    if absolute_lap < min_abs_lap or absolute_lap > max_abs_lap:
        print('absolute lap out of bounds... resetting to 0')
        return -1
    else:
        return 0
    
def reset_abs_lap(device, absolute_lap):
    #park ... 
    
    absolute_lap = 0 * u.deg
    ra, dec, alt, az = get_current_coords(device) 
    latest = generate_tracking_log_line(ra, dec, alt, az, absolute_lap)
    write_log(directory, get_log_file_name(directory), latest)
    
    print('absolute lap reset to 0... antenna parked')
    
def get_GC_coords():
    
    GC = SkyCoord.from_name('Galactic Center')
    A = GC.galactic.l.value # lon 0 360
    D = GC.galactic.b.value # lat -90 90
    ra_hr   = GC.ra.hour
    dec_deg  = GC.dec.deg
    MW_centre = {'ra': ra_hr, 'dec': dec_deg }

    dec_deg2  = GC.dec.deg + 5
    MW_offset = {'ra': dec_deg2, 'dec': dec_deg2 }
    
    ##### SUN TEST

    t = Time.now()
    sun_pos = coord.get_sun(t)
    RA= sun_pos.ra.hour
    DEC = sun_pos.dec.deg

    #MW_centre = {'ra': RA, 'dec': DEC}

    ############################
    a = 73.0/2
    be = 26.0/2
    epsilon = 0.01 #0.01

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
        
        return Altitud, Azimuth, MW_centre, MW_offset