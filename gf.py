# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 14:48:57 2022

@author: WiPoLabor
"""
from contextlib import ExitStack
import csv
import sys
import time
import getopt

from random import random as rand

from pylsl import StreamInfo, StreamOutlet, local_clock

from bbt import Signal, Device, SensorType, ImpedanceLevel

def config_signals(device):
    signals = device.get_signals()            
    for s in signals:
        s.set_mode(0)
    singal = signals[0]
    singal.set_mode(1)
    
def try_to(condition, action, tries, message=None):
        t = 0
        while (not condition() and t < tries):
            t += 1
            if message:
                print("{} ({}/{})".format(message, t, tries))
            action()
        return condition()
    
def create_outlet(device):
    srate = device.get_frequency()
    name = 'Ring'
    type = 'EEG'
    #signal = device.get_signals()
    n_channels = device.get_signals() #device.get_signals()
    print (srate)    

    info = StreamInfo(name, type, n_channels, srate, 'float32')

    # next make an outlet
    outlet = StreamOutlet(info)

    return outlet    

if __name__ == "__main__":

    print ("Start")      
    #if (len(sys.argv) <= 1):  
     #   print("Usage: " + sys.argv[0] + " <device name> [time (s) default = 10]")
      #  exit(0)
        
    #name = sys.argv[1]
    name = "BBT-FBR-AAB071"
    #name = "BBT-E08-AAB055"
    length = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    with Device.create_bluetooth_device(name) as device:
        if not try_to(device.is_connected, device.connect, 10, "Connecting to {}".format(name)):
            print("unable to connect")
            exit(1)
        print ("Connected")

        print(f"Recording {length} seconds of data into csv files from device {name}")


        config_signals(device)
        
        signals = device.get_signals()
        for x in range(len(signals)):
            print( signals[x])
        a = signals[0]
        print (a.channels())
        #print (signals[1])
        #print (signals[2])
        #print (signals[3])
        #print (signals[4])

        if not try_to(lambda: not device.is_connected(), device.disconnect, 10):
            print("unable to disconnect")
            exit(1)        
        print ("Connected") 
        print ("Ende")  