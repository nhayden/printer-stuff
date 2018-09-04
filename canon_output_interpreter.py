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

def output_param(param_idx, param_name, val, byte_str=None):
	num_and_name = "\t({:02d})".format(param_idx) 
	num_and_name += "{} : ".format(param_name).rjust(39)
	num_and_name += "{} ".format(val)
	if byte_str is not None:
		num_and_name += "({})".format(byte_str)
	print(num_and_name)

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
		print('\tINIT: {} (hex: {})'.format(
			  {"00": "Start to print", "01": "Start to register form",
		       "03": "Start to overlay (Basic)","04": "Start to overlay (MASK)"}[init_code],
			   init_code))
	
	## Set compression mode
	elif pcode == '62':
		print("Set compression mode")
		compression_code = args[3]
		print("\tCompression mode: {} (hex: {})".format(
			{"00":"uncompressed data","01":"compressed data"}[compression_code],
			compression_code
		))
	
	## Set print parameters
	elif pcode == '70':
		print("Set print parameters")
		print("\t" + " ".join(args[1:]))
		if len(args[1:]) != 42:
			print("ERROR: INCORRECT NUMBER OF PRINT PARAMETERS")
		output_param(1, "Paper Form", {"00":"Label/Gap", "01":"Tag/Marker",
			"02":"Tag/No TOF", "03":"Label/Marker"}[args[3]], args[3])
		output_param(2, "data_type (fixed value)", args[4])
		output_param(3, "Paper length (dots)", int("".join(args[5:7]), 16), "".join(args[5:7]))
		output_param(4, "Paper width (dots)", int("".join(args[7:9]), 16), "".join(args[7:9]))
		output_param(5, "Top margin (dots)", int("".join(args[9:11]), 16), "".join(args[9:11]))
		output_param(6, "Print area length (dots)", int("".join(args[11:13]), 16), "".join(args[11:13]))
		output_param(7, "Left margin (dots)", int("".join(args[13:15]), 16), "".join(args[13:15]))
		output_param(8, "Print area width (dots)", int("".join(args[15:17]), 16), "".join(args[15:17]))
		output_param(9, "Gap length (dots)", int("".join(args[17:19]), 16), "".join(args[17:19]))
		output_param(10, "Mark length (dots)", int("".join(args[19:21]), 16), "".join(args[19:21]))
		output_param(11, "Media type number", {"01":"Matte label paper", "02":"Glossy label paper",
			"03":"Synthetic paper", "04":"Matte tag", "05":"Thin matte tag"}[args[23]], args[23])
		## External option/Color mode/Rotation
		output_param(12, "External option/Color mode/Rotation", args[24])
		print("\t\t\t{} : {}".format("180degree rotated".rjust(17), int(args[24], 16) & (1<<1) != 0))
		print("\t\t\t{} : {}".format("Color Mode".rjust(17), "Full color" if (int(args[24], 16) & (1<<3) == 0) else "Monochrome"))
		print("\t\t\t{} : {}".format("External option".rjust(17),
			"External option invalid" if (int(args[24], 16) & (1<<4) == 0) else "Auto cutter valid"))
		
		## Print speed
		output_param(13, "Print speed (mm/sec)",
			"Auto" if int(args[25], 16) == 0 else 10 * int(args[25], 16), args[25])
		
		## Feed interval
		output_param(14, "Feed interval (sec)",
			"Auto" if int(args[26], 16) == 0 else int(args[26], 16) / 10, args[26])
		
		## Reserved / unused block
		print("\t(15-19 reserved / unused)")
		
		## Registered form ID
		output_param(20, "Form ID", int("".join(args[31:33]), 16), "".join(args[31:33]))
		
		## Resolution parameters
		output_param(21, "Input horizontal resolution (dpi)", int("".join(args[33:35]), 16), "".join(args[33:35]))
		output_param(22, "Input vertical resolution (dpi)", int("".join(args[35:37]), 16), "".join(args[35:37]))
		output_param(23, "Output horizontal resolution (dpi)", int("".join(args[37:39]), 16), "".join(args[37:39]))
		output_param(24, "Output vertical resolution (dpi)", int("".join(args[39:41]), 16), "".join(args[39:41]))
		output_param(25, "Print area horiz. byte size (bytes)", int("".join(args[21:23]), 16), "".join(args[21:23]))
		
		print("\t(26-27 reserved / unused)")
	
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
	
	## Esc f (block image transfer) (undocumented raster transfer)
	elif pcode == '66':
		print("Esc f (block image transfer: undocumented raster transfer)")
		big_endian_xfer_size = int("".join(args[2:0:-1]), 16)
		print("\tNumber of bytes being sent: {} (little endian hex: {})".format(
			big_endian_xfer_size, " ".join(args[1:3])))
		if (big_endian_xfer_size + 3 != len(args)):
			print("ERROR: improper num bytes sent")
		
		print(" ".join(args))
	
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
		#print(args)
		
		## cut interval stuff
		print("\tCut interval: {} (hex: {})".format(
			int("".join(args[3:5]), 16), " ".join(args[3:5])), end="")
		print(" (No cut)") if args[3:5] == ['00', '00'] else print()
		
		## page vs job end
		print("\tPage|Job: {} (hex: {})".format(
			{"01": "page", "02": "job"}[args[5]], args[5]
		))
		
		## param1
		print("\tparam1 (hex): {}".format(args[6]))
	
	## unknown command code
	else:
		print("UNRECOGNIZED COMMAND " + pcode)
	
