# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 10:20:50 2022

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
if __name__ == "__main__":

    #if (len(sys.argv) <= 1):  
     #   print("Usage: " + sys.argv[0] + " <device name> [time (s) default = 10]")
      #  exit(0)
        
    #name = sys.argv[1]
    name = "BBT-FBR-AAB071"
    #name = "BBT-E08-AAB055"
    length = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    with Device.create_bluetooth_device(name) as device:
        
        print ("Connected")

        print(f"Recording {length} seconds of data into csv files from device {name}")

    
    
        device.stop()