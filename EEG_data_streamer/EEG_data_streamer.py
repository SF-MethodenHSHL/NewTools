# -*- coding: utf-8 -*-
"""
Created on Sun Aug  6 10:28:11 2023

@author: manamana
"""

''' This script connects with connected Bitbrain devices and streams Data through LSL'''


import sys
import time
import os
from sys import exit
from pylsl import StreamInfo, StreamOutlet, local_clock
import tkinter as tk
from tkinter import Entry, Label, Button, StringVar
import threading



main_path = os.path.dirname(os.path.join(__file__))
sys.path.append(main_path)


from bbt import Signal, Device, SensorType, ImpedanceLevel

#global vars
device = None
recording_active = False

def start_streaming_thread():
    start_button.grid_forget()  # Hide the button
    status_var.set("Connecting...")
    threading.Thread(target=run_script).start()




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
        s.set_mode(1)


def create_lsl_outlet(device, dev_name, dev_type):
    srate = device.get_frequency()

    active_signals = [s for s in device.get_signals() if s.mode() != 0 and s.type() == "EEG" ]
    n_channels = sum([s.channels() for s in active_signals])
    
    sync = device.synchronize()
    tof = str((sync[0])/1e6)
    offset = str((sync[1])/1e6)
    # List of channel positions
    channel_positions = ["AF7", "Fp1", "Fp2", "AF8", "PO7", "O1", "O2", "PO8"]
    # Create an info object
    info = StreamInfo(dev_name, dev_type, n_channels, srate, 'float32')
    
    # Create a StreamOutlet
    info.desc().append_child_value("manufacturer", "LSLBbtAmp")
    info.desc().append_child_value("Time_of_flight", f"{tof} ms")
    info.desc().append_child_value("Offset", f"{offset} ms")
    chns = info.desc().append_child("channels")
    
    for signal in active_signals:
        for chan_idx in range(signal.channels()):
            ch = chns.append_child("channel")
            if chan_idx < len(channel_positions):
                label = channel_positions[chan_idx]
                ch.append_child_value("label", label)
            ch.append_child_value("unit", "au")
            ch.append_child_value("type", signal.type())  # Append the signal type for this channel
    
    lsl_outlet = StreamOutlet(info)
    return lsl_outlet




import numpy as np

def record_one(device, lsl_outlet, signals, first_read=True):
    sequence, battery, flags, data = device.read()
    ts = local_clock() # Use local_clock from pylsl
    data = np.array(data)  # Convert 'data' list to a NumPy array
    data_offset = 0
    for s in signals:
        n_values = s.channels() * s.samples()
        signal_data_slice = data[data_offset:data_offset + n_values] / 1e6
        
        for i in range(s.samples()):  
            if first_read and i == 0:
                first_read = False
                continue
            
            lsl_outlet.push_sample(signal_data_slice[i::s.samples()], ts)
            
        data_offset += n_values
        for channel in range(0, 8):
            channel_imp = device.get_eeg_impedance(channel)
            impedance_labels[channel].set(f"Channel {channel} Impedance: {channel_imp}")
            if channel_imp == ImpedanceLevel.GOOD:
               impedance_boxes[channel].config(bg='green') 
            if channel_imp == ImpedanceLevel.SATURATED:
               impedance_boxes[channel].config(bg='orange')         
            if channel_imp == ImpedanceLevel.BAD:
               impedance_boxes[channel].config(bg='red') 
            if channel_imp == ImpedanceLevel.FAIR:
               impedance_boxes[channel].config(bg='yellow') 

 

def record_data(device, length, lsl_outlet):
    global recording_active

    active_signals = [s for s in device.get_signals() if s.mode() != 0 and s.type() == "EEG"]
    device.start()
    f = int(device.get_frequency())

    for i in range(length * f):
        # If the recording_active flag is set to False, stop the loop and the device
        if not recording_active:
            break

        # If i is 0, skip the first sample
        record_one(device, lsl_outlet, active_signals, i == 1)

    device.stop()
    #print ("Stopped: ", not device.is_running())



def run_script():
    global device
    global recording_active
    # Enter the name of the connected device here (serial number)  
    name = device_name_entry.get()
    length_str = length_entry.get()  # Get the value from the Entry widget
    try:
        length = int(length_str)
    except ValueError:
        status_var.set("Invalid length entered. Using default 600 seconds.")
        length = 600


    with Device.create_bluetooth_device(name) as device:
        #initial_signal(device)
        if not try_to(device.is_connected, device.connect, 10, "Connecting to {}".format(name)):
            status_var.set("Unable to connect.")
            start_button.grid(row=3, columnspan=2, pady=20)
            return
        status_var.set("Connected")
        
        status_var.set(f"Streaming {length} seconds of data to LSL from device {name}")
        # Activate signals
        config_signals(device)
        # Create an LSL outlet
        lsl_outlet = create_lsl_outlet(device, name, "EEG")
        # Record the data
        recording_active = True
        record_data(device, length, lsl_outlet)
        recording_active = False
        # Delete the outlet when done
        del lsl_outlet
        
        # Disconnect
        if not try_to(lambda: not device.is_connected(), device.disconnect, 10):
            status_var.set("Unable to disconnect.")
            return
        status_var.set("Disconnected")
        start_button.grid(row=3, columnspan=2, pady=20)  # Show the button again
        
        
def disconnect_device():
    global recording_active
    recording_active = False
    time.sleep(2)
    if device and device.is_connected():
        if not try_to(lambda: not device.is_connected(), device.disconnect, 10):
            print("Unable to disconnect")
            exit(1)        
        print("Disconnected")
        start_button.grid(row=3, columnspan=2, pady=20)
        


# GUI
root = tk.Tk()
root.title("EEG Data Streamer")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(padx=10, pady=10)

# Device Name input
Label(frame, text="Enter Device Name:").grid(row=0, column=0, sticky="w", pady=5)
device_name_entry = Entry(frame)
device_name_entry.grid(row=0, column=1, pady=5)
device_name_entry.insert(0, "BBT-E08-AAB055")  # Default value

# Length input
Label(frame, text="Enter Streaming Length (seconds):").grid(row=1, column=0, sticky="w", pady=5)
length_entry = Entry(frame)
length_entry.grid(row=1, column=1, pady=5)
length_entry.insert(0, "600")  # Default value


# Button to run the script
start_button = Button(frame, text="Start Streaming", command=start_streaming_thread)
start_button.grid(row=3, columnspan=2, pady=20)

# Disconnect button

disconnect_button = tk.Button(root, text="Disconnect", command=disconnect_device)
disconnect_button.pack()

# List to store the impedance labels for each channel
impedance_labels = []
impedance_boxes = []

for channel in range(8):
    imp_var = StringVar()
    imp_var.set(f"Channel {channel} Impedance: -")
    lbl = Label(frame, textvariable=imp_var)
    lbl.grid(row=5+channel, column=0, sticky="w", pady=2)
    impedance_labels.append(imp_var)
    
    # Create a Canvas widget for the visual indicator
    canvas = tk.Canvas(frame, width=15, height=15, bg='white')  # Default color is white
    canvas.grid(row=5+channel, column=2, sticky="w", pady=2)
    impedance_boxes.append(canvas)


# Label to display status
status_var = StringVar()
status_var.set("Ready to stream...")
status_label = Label(frame, textvariable=status_var)
status_label.grid(row=2, columnspan=2, pady=5)

root.mainloop()
