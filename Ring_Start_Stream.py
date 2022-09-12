# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 09:46:21 2022

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


def try_to(condition, action, tries, message=None):
        t = 0
        while (not condition() and t < tries):
            t += 1
            if message:
                print("{} ({}/{})".format(message, t, tries))
            action()
        return condition()


def config_signals(device):
    signals = device.get_signals()            
    for s in signals:
        s.set_mode(0)
    signal = signals[0]
    signal.set_mode(1)

def csv_filename(signal_number, signal_type):
    return f"signal_{signal_number}({signal_type}).csv"


def record_one(device, signals, outlet):
    sequence, battery, flags, data = device.read()
    ts = time.time_ns()
    common_data = [ts, sequence, battery, flags]
    data_offset = 0
    for  s in  signals:   
        n_values = s.channels()#*s.samples()        
        
        signal_data_slice = data[data_offset:data_offset + n_values]
        print(data)
        outlet.push_sample(signal_data_slice)
            #for i in range(s.samples()):            
            #csv.writerow(common_data + signal_data_slice[i::s.samples()])
        data_offset += n_values


def record_data(device, length, outlet1, outlet2, outlet3):
    #create the csv files    
    with ExitStack() as stack:
        active_signals = [s for s in device.get_signals() if s.mode() != 0]
        #open csv files
        #files = [stack.enter_context(open(csv_filename(i, s.type()), 'w', newline='')) for i,s in enumerate(active_signals)]

        #write headers
        #writers = [csv.writer(f) for f in files]
        #for (s, w) in zip(active_signals, writers):
        #    common_header = ["timestamp", "sequence", "battery", "flags"]
        #    channels_header = [ f"channel_{i}" for i in range(s.channels())]
        #    w.writerow(common_header + channels_header)

        #record data
        device.start()
        #f = int(device.get_frequency())        
        #for i in range(length * f):
        while True:    
            record_one(device,  active_signals, outlet1, )           
            record_one(device,  active_signals, outlet2, )            
            record_one(device,  active_signals, outlet3, )
            
            time.sleep(0.01)
        device.stop()
    print ("Stopped: ", not device.is_running())
    
def create_outlet(device):
    srate = device.get_frequency()
    name = 'Ring'
    type = 'EEG'
    signals = device.get_signals()
    signal = signals[0]
    n_channels = signal.channels()# #device.get_signals()
    print(n_channels)
    print (srate)    

    info = StreamInfo(name, type, n_channels, srate, 'float32')

    # next make an outlet
    outlet = StreamOutlet(info)

    return outlet

def create_outlet2(device):
    srate = device.get_frequency()
    name = 'Ring1'
    type = 'EEG'
    signals = device.get_signals()
    signal = signals[1]
    n_channels = signal.channels()# #device.get_signals()
    print(n_channels)
    print (srate)    

    info = StreamInfo(name, type, n_channels, srate, 'float32')

    # next make an outlet
    outlet = StreamOutlet(info)

    return outlet

def create_outlet3(device):
    srate = device.get_frequency()
    name = 'Ring2'
    type = 'EEG'
    signals = device.get_signals()
    signal = signals[2]
    n_channels = signal.channels()# #device.get_signals()
    print(n_channels)
    print (srate)    

    info = StreamInfo(name, type, n_channels, srate, 'float32')

    # next make an outlet
    outlet = StreamOutlet(info)

    return outlet


if __name__ == "__main__":

    #if (len(sys.argv) <= 1):  
     #   print("Usage: " + sys.argv[0] + " <device name> [time (s) default = 10]")
      #  exit(0)
        
    #name = sys.argv[1]
    name = "BBT-FBR-AAB071"
    #name = "BBT-E08-AAB055"
    length = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    with Device.create_bluetooth_device(name) as device:
        if not try_to(device.is_connected, device.connect, 10, "Connecting to {}".format(name)):
            print("unable to connect")
            exit(1)
        print ("Connected")

        print(f"Recording data from device {name}")

        config_signals(device)
        lsl_outlet1 = create_outlet(device)
        lsl_outlet2 = create_outlet2(device)
        lsl_outlet3 = create_outlet3(device)
        record_data(device, length, lsl_outlet1, lsl_outlet2,lsl_outlet3)
  
    
 #if not try_to(lambda: not device.is_connected(), device.disconnect, 10):
 #    print("unable to disconnect")
 #    exit(1)        
 #print ("Connected")           
  




