#!/usr/bin/env python3

import subprocess, sys, re

#print(sys.argv[0], "\n", sys.argv[1])

#subprocess.call(["sed 's/\x1B/\/g' "+sys.argv[1]], shell=True)

with open (sys.argv[1], 'rb') as f:
	hexdata = f.read().hex()
	params = hexdata.split(r'1b')[1:]

for param in params:
	print("some param\n", param, "\n")
	
