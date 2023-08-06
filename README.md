# EEG_data_streamer
 This is a tool to stream data from a bitbrain EEG device to LSL
 It can be run eighter via the code (requires python version 3.10) or as a standalone executable.

# Usage
 The tool connects to an bitbrain EEG device of the specified name (serial number) and streams data of the specified lenght via LSL.
 The device first has to be paired via bluetooth with the computer it is used on. The tool was created for and tested only with the Bitbrain "Air".

# Features
 Impedance levels of the EEG-channels are displayed in real time.
 Lenght of streaming can be specified ahead of streaming
 Streaming can be stopped manually.

# Complementary tools
 For recording the LSL stream use Lab recorder: https://github.com/labstreaminglayer/App-LabRecorder
 
