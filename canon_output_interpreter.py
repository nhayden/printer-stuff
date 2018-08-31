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
	args = split_bytes(param)
	
	## Beginning of job
	if pcode == '4b':
		print("Beginning of job")
		init_code = args[3]
		print('\tINIT: {} ({})'.format(
			  {"00": "Start to print", "01": "Start to register form",
		       "03": "Start to overlay (Basic)","04": "Start to overlay (MASK)"}[init_code],
			   init_code))
	
	## Set compression mode
	elif pcode == '62':
		print("Set compression mode")
		compression_code = args[3]
		print("\tCompression mode: {} ({})".format(
			{"00":"uncompressed data","01":"compressed data"}[compression_code],
			compression_code
		))
	
	## Set print parameters
	elif pcode == '70':
		print("Set print parameters")
		print("\t" + " ".join(args[1:]))
		if len(args[1:]) != 42:
			print("ERROR: INCORRECT NUMBER OF PRINT PARAMETERS")
	
	## Number of copies
	elif pcode == '6e':
		print("Number of copies")
		hex_num_copies = args[3:5]
		print("\tCopies (in hex): {}".format(" ".join(hex_num_copies)))
	
	## Specify image transfer order
	elif pcode == '75':
		print("Specify image transfer order")
		#print(" ".join(split_bytes(param)))
		print("\tTransfer order: {} {} {} {} ({} {} {} {})".format(
			chr(int(args[3], 16)), chr(int(args[4], 16)), chr(int(args[5], 16)), chr(int(args[6], 16)),
			args[3], args[4], args[5], args[6]
		))
		print("\tOther transfer data (masks, etc in hex): {} {} {} {}".format(
			args[7], args[8], args[9], args[10]
		))
		print("\tRaster count: {} (hex: {})".format(
			int("".join(args[11:15]), 16), " ".join(args[11:15])
		))
		
	## Execute raster skip
	elif pcode == '65':
		print("Execute raster skip")
		#print(" ".join(args))
		print("\tRaster skip: {} (hex: {})".format(
			int("".join(args[3:5]), 16), " ".join(args[3:5])
		))
	
	## Execute block skip
	elif pcode == '45':
		print("Execute block skip")
		#print(" ".join(args))
		print("\tBlock skip: {} (hex: {})".format(
			int("".join(args[3:5]), 16), " ".join(args[3:5])
		))
	
	## MYSTERY COMMAND (undocumented raster transfer)
	elif pcode == '66':
		print("MYSTERY COMMAND (undocumented raster transfer)")
	
	## Maintenance commands
	elif pcode == '6d':
		print("Maintenance commands")
		#print(" ".join(args))
		#print("{}".format(args[:7]))
		if args[:7] != ['6d', '01', '00', '77', '05', '03', 'c4']:
			print("\tUNDOCUMENTED MAINTENANCE COMMANDS")
		else:
			print("\tReceived correct parameters for dotcount maint. cmds")
	
	## Start printing
	elif pcode == '73':
		print("Start print / end of job/page")
		print(args)
	
	## unknown command code
	else:
		print("UNRECOGNIZED COMMAND " + pcode)
	
