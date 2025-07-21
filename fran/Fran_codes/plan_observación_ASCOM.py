# 1.- Import libraries
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.coordinates import SkyCoord, Galactocentric
from astropy.coordinates import SkyCoord
import astropy.coordinates as coord
import matplotlib.pyplot as plt
from astropy import units as u
from astropy.time import Time
from PyAstronomy import pyasl
from datetime import datetime
import win32com.client
import numpy as np
import ephem
import math
import time


# 2.- Select mount
tel = win32com.client.Dispatch("ASCOM.MeadeGeneric.Telescope")

# 3.- Define tracking point Galactic Center
GC = SkyCoord.from_name('Galactic Center')
now = Time.now()
calan_obs = EarthLocation(lat=-33.3961*u.deg, lon=-70.537*u.deg, height=867*u.m)
GCaltaz = GC.transform_to(AltAz(obstime=now,location=calan_obs))

# 4.- Position of center of the beam
A = GC.galactic.l.value # lon 0 360
D = GC.galactic.b.value # lat -90 90
RA   = GC.ra.hourangle  # entrega tupla
Dec  = GC.dec.deg

# 5.- Ellipse parameters 1200 [MHz]
a = 38.0
be = 8.0 
epsilon = 0.01 #0.01
ref = 10*u.deg
    
# 6.- Define ellipse on the tangent plane
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
    calan_obs = EarthLocation(lat=-33.3961*u.deg, lon=-70.537*u.deg, height=867*u.m)
    now = Time.now()
    altaz_frame = AltAz(obstime=now,location=calan_obs)
    eq_to_altaz = eq.transform_to(altaz_frame)

    Altitud = eq_to_altaz.alt
    Azimuth = eq_to_altaz.az
    tel.Connected = True
    
    # 7.- Define mount location
    tel.SiteLatitude  = -33.39
    tel.SiteLongitude = -70.53
    tel.SiteElevation = 867

    # 8.- Define Tracking
    if Altitud > ref:
        tel.Connected = True
        tel.Tracking = True
        tel.SlewToCoordinates(RA, GC.dec.deg)
        time.sleep(900)
    else:
        tel.Connected = True
        tel.Tracking = True
        Dec2 = Dec
        while Altitud < ref:
            Dec2 = Dec2 + 5
            tel.SlewToCoordinates(RA, Dec2)
            time.sleep(900)
        
        

   
            

 
