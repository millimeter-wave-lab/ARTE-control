# -- coding: utf-8 --
"""
Created on Tue Aug  8 09:33:27 2023

@author: rafael
"""

import numpy as np

TS=10
TP=290


c1dB=10
c1mag=10**(-c1dB/20)
c2dB=3
c2mag=10**(-c2dB/20)


t1mag=np.sqrt(1-c1mag**2)
t2mag=np.sqrt(1-c2mag**2)

L1dB=0
L1mag=10**(L1dB/10)
L2dB=0
L2mag=10**(L2dB/10)

Dphi=90


print('c1mag= '+ str(c1mag))
print('c2mag= '+ str(c2mag))
print('t1mag= '+ str(t1mag))
print('t2mag= '+ str(t2mag))

T01=(t1mag*2*1/L1mag*t2mag2+c1mag2*1/L2mag*c2mag*2)*TS

T02=(c1mag*2*1/L1mag*t2mag2+t1mag2*1/L2mag*c2mag*2)*TP

T03=((1-1/L1mag)t2mag2+(1-1/L2mag)*c2mag*2)*TP

print("\n")
print('T01= '+ str(T01))
print('T02= '+ str(T02))
print('T03= '+ str(T03))

##print("\n")
print("T_total= "+ str(T01+T02+T03))


abs_S21_2=(1-c1mag*2)(1-c2mag*2)/L1mag - 2*c1mag*c2mag/np.sqrt(L1mag*L2mag)*np.sqrt((1-c1mag2)(1-c2mag*2))*np.cos(Dphi*np.pi/180)+ c1mag2*c2mag*2/L2mag
print("\n")
print("abs_S21_2= "+ str(abs_S21_2))

Tia=abs_S21_2*TS+(1-abs_S21_2)*TP
print("Tia= "+ str(Tia))

DPR=(1-abs_S21_2)
print("DPR= "+ str(DPR))
