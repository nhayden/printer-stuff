#!/usr/bin/env python3

import subprocess, sys, re, os

#print(sys.argv[0], "\n", sys.argv[1])
#subprocess.call(["sed 's/\x1B/\/g' "+sys.argv[1]], shell=True)
#print(os.listdir(sys.argv[1]))

## invoke from within printer-stuff directory:
## python3 canon_output_interpreter.py /cygdrive/c/Users/nhayden.SEANET/Documents/Output.prn

with open (sys.argv[1], 'rb') as f:
	hexdata = f.read().hex()
	params = hexdata.split(r'1b')[1:]

for param in params:
	pcode = param[0:2]
	if pcode == '4b':
		print("Beginning of job")
	elif pcode == '62':
		print("Set compression mode")
	elif pcode == '70':
		print("Set print parameters")
	elif pcode == '6e':
		print("Number of copies")
	elif pcode == '75':
		print("Specify image transfer order")
	elif pcode == '65':
		print("Execute raster skip")
	elif pcode == '45':
		print("Execute block skip")
	elif pcode == '66':
		print("MYSTERY COMMAND")
	elif pcode == '6d':
		print("Maintenance commands")
	elif pcode == '73':
		print("Start printing")
	else:
		print("UNRECOGNIZED COMMAND " + pcode)
	
