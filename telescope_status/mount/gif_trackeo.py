# 1.- Import libraries
import numpy as np
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord
import astropy.coordinates as coord
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.coordinates import SkyCoord, Galactocentric
import matplotlib.pyplot as plt
import datetime
from astropy.time import TimeDelta
from PyAstronomy import pyasl
from datetime import datetime
import ephem
import math
import time
import imageio
#import win32com.client

# 2.- Select mount
#tel = win32com.client.Dispatch("ASCOM.MeadeGeneric.Telescope")

# 3.- Define mount location
#tel.SiteLatitude  = -33.39
#tel.SiteLongitude = -70.53
#tel.SiteElevation = 867

# 4.- Define tracking point Galactic Center
GC = SkyCoord.from_name('Galactic Center')
calan_obs = EarthLocation(lat=-33.3961*u.deg, lon=-70.537*u.deg, height=867*u.m)

# 5.- Position of center of the beam
A = -50
D = 0
#round(GC.galactic.b.value)*-1 # lat -90 90
#RA   = GC.ra.hourangle  # entrega tupla
#Dec  = GC.dec.deg
# 6.- Ellipse parameters 1200 [MHz]
a = 38.0
be = 8.0 
epsilon = 1 #0.01
ref = 5




t1 = Time('2022-03-08 00:00:00') # tiempo que uso como inicio de 24h 
dt2 = TimeDelta(3600.0, format='sec') # intervalo de 1h
vtimes = [t1,t1+dt2,t1+2*dt2,t1+3*dt2,t1+4*dt2,t1+5*dt2,t1+6*dt2,t1+7*dt2,t1+8*dt2,t1+9*dt2,t1+10*dt2,t1+11*dt2,t1+12*dt2,t1+13*dt2,t1+14*dt2,t1+15*dt2,t1+16*dt2,t1+17*dt2,t1+18*dt2,t1+19*dt2,t1+20*dt2,t1+21*dt2,t1+22*dt2,t1+23*dt2]

vec_l = np.arange(0.0, 360.0,1.8)
vec_b = np.zeros(200)

i = 0 # contador de 24h
j = 0 # contador para imgs gif

im = []

for i in range(len(vtimes)): # 24 iteraciones
    
    t = vtimes[i] # hora de 1 en 1
    i = i+1

    V_Alt =[]
    V_Az =[]

    V_Alt_data =[]
    V_Az_data = []
    

    # 7.- Define ellipse on the tangent plane
    anxi = np.arange(A-a, A+a, epsilon)
    aneta = be * np.sqrt(1 - (anxi-A)**2 / a**2)

    angle_xi =  np.concatenate((anxi, anxi))
    angle_eta = D + np.concatenate((-aneta, aneta))

    XI = np.tan(angle_xi / 180.0 * np.pi)   #rad   gal
    ETA = np.tan(angle_eta / 180.0 * np.pi) #rad   gal

    # 8.- Conversion standard coord (xi,eta) to Horizontal coord (Az,Alt)
    for xi, eta in zip(XI, ETA):
        alpha = np.arctan( xi /( np.cos(D/ 180.0 * np.pi) - eta * np.sin(D/ 180.0 * np.pi)) ) + A/ 180.0 * np.pi #rad gal
        delta = np.arctan(eta * (np.cos(D/ 180.0 * np.pi) + np.sin(D/ 180.0 * np.pi) ) * np.sin(alpha - A/ 180.0 * np.pi) / xi) #rad gal

        alpha_deg = alpha*180/np.pi
        delta_deg = delta*180/np.pi

        gal = SkyCoord(l = alpha_deg*u.deg, b = delta_deg*u.deg, frame ='galactic')# transformación coord estandar a galácticas

        V_Alt.append((gal.fk5.transform_to(AltAz(obstime=t,location=calan_obs))).alt) # transformación galacticas a horizontales alt
        V_Az.append((gal.fk5.transform_to(AltAz(obstime=t,location=calan_obs))).az) # transformación galacticas a horizontales az

    #tel.Connected = True
    #tel.Tracking = True
    #tel.SlewToCoordinates(RA, Dec)
    #time.sleep(3600)

    for d in range(len(V_Alt)): # recorro vector de alturas para posicionar en orden las coord horizontales
        V_Alt_data.append(V_Alt[d].value)
        V_Az_data.append(V_Az[d].value)

    gal_coord = SkyCoord(vec_l,vec_b, frame = "galactic", unit = "deg")
    cg_altaz = gal_coord.transform_to(AltAz(obstime = t,location=calan_obs))

    j = j+1

    # ploteo altitud vs acimut
    plt.scatter(cg_altaz.az, cg_altaz.alt,label= "GP -"+str(t),lw = 2, s = 2)
    plt.scatter(V_Az_data, V_Alt_data, label='Beam -'+str(t),lw = 2, s = 2)
    plt.legend(loc='upper right')
    plt.xlim(0,360)
    plt.ylim(-90, 90)
    plt.xlabel('Azimuth [deg]')
    plt.ylabel('Altitude [deg]')
    plt.grid()
    plt.savefig(str(j)+'.png')
    im.append(str(j)+'.png')

    plt.close()

    print(i)
    print(A,D)
    print(min(V_Alt_data))
    
## empiezo edición
    if i == 11 :
        A = 0
        D = 0
        #lon = str(A)
        #lat = str(D)
        #ga = ephem.Galactic(lon,lat)
        #eq = ephem.Equatorial(ga)
        #RA = eq.ra
        #Dec = eq.dec
        #print(RA,Dec)
        print(A,D)
    if i == 22 :
        A = -40
        D = -15
        #lon = str(A)
        #lat = str(D)
        #ga = ephem.Galactic(lon,lat)
        #eq = ephem.Equatorial(ga)
        #RA = eq.ra
        #Dec = eq.dec
        print(A,D)
    else:
        continue
  
## fin edición



# Build GIF
with imageio.get_writer('mod_print.gif', mode='I') as writer:
    for filename in im :
        image = imageio.imread(filename)
        writer.append_data(image)


'''
            ## empiezo edición
            if i == 11 :
                A = 0
                D = 0
                lon = str(A)
                lat = str(D)
                ga = ephem.Galactic(lon,lat)
                eq = ephem.Equatorial(ga)
                RA = eq.ra
                Dec = eq.dec
                print(RA,Dec)
                #tel.Connected = True
                #tel.Tracking = True
                #tel.SlewToCoordinates(RA, Dec)
                #time.sleep(3600)
                
            if i == 22 :
                A = -40
                D = -15
                lon = str(A)
                lat = str(D)
                ga = ephem.Galactic(lon,lat)
                eq = ephem.Equatorial(ga)
                RA = eq.ra
                Dec = eq.dec
                print(RA,Dec)
                #tel.Connected = True
                #tel.Tracking = True
                #tel.SlewToCoordinates(RA, Dec)
                #time.sleep(3600)
            else:
                lon = str(A)
                lat = str(D)
                ga = ephem.Galactic(lon,lat)
                eq = ephem.Equatorial(ga)
                RA = eq.ra
                Dec = eq.dec
                print(RA,Dec)
                #tel.Connected = True
                #tel.Tracking = True
                #tel.SlewToCoordinates(RA, Dec)
                #time.sleep(3600)
  
            ## fin edición
'''
