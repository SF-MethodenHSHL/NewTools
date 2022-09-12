# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 13:16:24 2022

@author: WiPoLabor
"""

import sys
print("Name of program:", sys.argv[0])
print("Number of elements:", len(sys.argv))
print("List of Arguments:", str(sys.argv))
print("Number of elements excluding the name of the program:", (len(sys.argv)-1))
