#!/usr/bin/env python3
"""
Computes the min/max FMCW beat frequency expected for a given range vs. sweep time and RF bandwidth

You might consider planning your sweep frequency and beat frequencies to land within the range of a PC sound card, say 200Hz - 24kHz
(I try to avoid 60,120,180Hz for powerline harmonics)

Refs:
1) D. G. Luck, Frequency Modulated Radar. New York: McGraw-Hill, 1949.
2) M. Hirsch. “A Low-Cost Approach to L-band FMCW Radar: Thru-Wall Microwatt Radar". Ottawa, Ontario: North American Radio Science Meeting, July 2007.
"""
from __future__ import division
from numpy import arange,exp,pi,sqrt,log10,asarray
from numpy.random import randn
from matplotlib.pyplot import subplots,draw,pause
#
from .estimation import snrest,psd
#
c = 299792458

def range2beat(range_m, tm, bw):
    """
    range_m: one-way range to target in meters
    bw: FMCW linear chirp bandwidth
    tm: time of sweep
    """
    return 2*asarray(range_m)*bw/(tm*c)

def beat2range(beats,tm,bw):
    """
    beats: beat frequencies from target returns
    bw: FMCW linear chirp bandwidth
    tm: time of sweep
    """
    return c * beat2time(beats,tm,bw) #distance estimate, meters

def beat2time(beats,tm,bw):
    return beats*tm / (2*bw) #two-way travel time, seconds


def bw2rangeres(bw):
    return c/(2*bw)

def simtone(tm,fs,SNR,Ftone,Nobs):
    t = arange(0,tm,1/fs) #time samples
    x = sqrt(2)*exp(1j*2*pi*Ftone*t) #noise-free signal

    nvar = 10**(-SNR/10.) #variance of noise
    noise = sqrt(nvar)*(randn(Nobs,x.size) + 1j*randn(Nobs,x.size))

    print('SNR measured {:.1f} dB'.format(snrest(x,noise[0,:])))

    y = x + noise #noisy observation

    return t,y

def plots(t,y,fs,Np):
#%% time domain movie
    fg,axs = subplots(1,2)

    ax = axs[0]
    hr = ax.plot(t[:Np],y[0,:Np])[0]
    ax.set_title('Noisy Sinusoid')
    ax.set_xlabel('time [sec]')
    ax.set_ylabel('amplitude')

    ax = axs[1]
    Pxx,fax = psd(y[0,:Np],fs)
    hp = ax.plot(fax,10*log10(Pxx))[0]
    ax.set_title('Noisy PSD')
    ax.set_xlabel('Frequency [Hz]')
    ax.set_ylabel('amplitude [dB]')

    for Y in y:
        hr.set_ydata(Y[:Np])

        Pxx,fax = psd(Y[:Np],fs)
        hp.set_ydata(10*log10(Pxx))

        draw(); pause(0.001)