#!/usr/bin/env python3

import subprocess, sys, re, os

#print(sys.argv[0], "\n", sys.argv[1])
#subprocess.call(["sed 's/\x1B/\/g' "+sys.argv[1]], shell=True)
#print(os.listdir(sys.argv[1]))

## invoke from within printer-stuff directory:
## python3 canon_output_interpreter.py /cygdrive/c/Users/nhayden.SEANET/Documents/Output.prn


## assumes first byte is command code
def split_bytes(s):
  return re.split("(\w\w)", s)[1::2]

with open (sys.argv[1], 'rb') as f:
	hexdata = f.read().hex()
	params = hexdata.split(r'1b')[1:]

for param in params:
	pcode = param[0:2]
	
	## Beginning of job
	if pcode == '4b':
		print("Beginning of job")
		init_code = split_bytes(param)[3]
		print("\tINIT: "+{"00": "Start to print", "01": "Start to register form",
		"03": "Start to overlay (Basic)","04": "Start to overlay (MASK)"}[init_code])
	
	## Set compression mode
	elif pcode == '62':
		print("Set compression mode")
		#print("\t"+param)
		print("\tCompression mode: ", end="")
		print({"00":"uncompressed data","01":"compressed data"}[split_bytes(param)[3]])
	
	## Set print parameters
	elif pcode == '70':
		print("Set print parameters")
		print("\t" + " ".join(split_bytes(param)[1:]))
		if len(split_bytes(param)[1:]) != 42:
			print("ERROR: INCORRECT NUMBER OF PRINT PARAMETERS")
	
	## Number of copies
	elif pcode == '6e':
		print("Number of copies")
		print(param)
		print("\tCopies: "+ " ".join(split_bytes(param)[3:5]))
	
	## Specify image transfer order
	elif pcode == '75':
		print("Specify image transfer order")
	
	## Execute raster skip
	elif pcode == '65':
		print("Execute raster skip")
	
	## Execute block skip
	elif pcode == '45':
		print("Execute block skip")
	
	## MYSTERY COMMAND (undocumented raster transfer)
	elif pcode == '66':
		print("MYSTERY COMMAND (undocumented raster transfer)")
	
	## Maintenance commands
	elif pcode == '6d':
		print("Maintenance commands")
	
	## Start printing
	elif pcode == '73':
		print("Start printing")
	
	## unknown command code
	else:
		print("UNRECOGNIZED COMMAND " + pcode)
	
