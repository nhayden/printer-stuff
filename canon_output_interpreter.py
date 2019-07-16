#!/usr/bin/env python3
import re
import sys


# print(sys.argv[0], "\n", sys.argv[1])
# subprocess.call(["sed 's/\x1B/\/g' "+sys.argv[1]], shell=True)
# print(os.listdir(sys.argv[1]))

# invoke from within printer-stuff directory:
# python3 canon_output_interpreter.py /cygdrive/c/Users/nhayden.SEANET/Documents/Output.prn

def twos_comp(val_str, nbytes=1):
    import sys
    val = int(val_str, 16)
    b = val.to_bytes(nbytes, byteorder=sys.byteorder, signed=False)
    return int.from_bytes(b, byteorder=sys.byteorder, signed=True)


def is_compressed(hex_val):
    tc = twos_comp(hex_val)
    return -127 <= tc <= -1


def is_uncompressed(hex_val):
    tc = twos_comp(hex_val)
    return 0 <= tc <= 127


# Calculates expanded length of raster bytestream based on Canon spec
def expanded_num_raster_bytes(rdata, verbose=False):
    total_data_length = 0
    while rdata:
        control_byte_decimal = abs(twos_comp(rdata[0])) + 1
        if is_compressed(rdata[0]):
            count = control_byte_decimal
            if verbose:
                s = "compressed num={} : {}".format(
                    count, (rdata[1] + " ") * count
                )
                print(s)
            rdata = rdata[2:]
            # print("comp rdata: {}".format(rdata))
            total_data_length += count
        elif is_uncompressed(rdata[0]):
            count = control_byte_decimal
            range_end_exclusive = control_byte_decimal + 1
            if verbose:
                s = "uncompressed num={} : {}".format(
                    count, " ".join(rdata[1:range_end_exclusive])
                )
                print(s)
            rdata = rdata[range_end_exclusive:]
            # print("uncomp rdata: {}".format(rdata))
            total_data_length += count
        else:
            if verbose:
                print("padding")
            rdata.pop(0)

    return total_data_length


# assumes first byte is command code
def split_bytes(s):
    return re.split(r"(\w\w)", s)[1::2]


# format (with alignment, etc) and output a given parameter
def output_param(param_idx, param_name, val, byte_str=None):
    num_and_name = "\t({:02d})".format(param_idx)
    num_and_name += "{} : ".format(param_name).rjust(39)
    num_and_name += "{} ".format(val)
    if byte_str is not None:
        num_and_name += "({})".format(byte_str)
    print(num_and_name)


with open(sys.argv[1], 'rb') as f:
    hexdata = f.read().hex()
    split_data = re.split(r"(\w\w)", hexdata)[1:]
    split_data = split_data[::2]  # skip empties

    command_codes = ['K', 'b', 'p', 'n', 'u', 'F', 'f', 'E', 'e', 'm', 's']
    command_codes_hex = [format(ord(x), "x") for x in command_codes]
    splits = []
    for i, v in enumerate(split_data):
        if v == '1b' and i < len(split_data) - 1 and split_data[i + 1] in command_codes_hex:
            splits.append(i)

    params = list()
    for x in range(len(splits)-1):  # all but last
        params.append(split_data[splits[x]:splits[x+1]])
    params.append(split_data[splits[len(splits)-1]:])

for param in params:
    pcode = param[1]
    args = param[1:]
    # print("args length: {}".format(len(args)))

    # Beginning of job
    if pcode == '4b':
        print("Beginning of job")
        init_code = args[3]
        print('\tINIT: {} (hex: {})'.format(
            {"00": "Start to print", "01": "Start to register form",
             "03": "Start to overlay (Basic)", "04": "Start to overlay (MASK)"}[init_code],
            init_code))

    # Set compression mode
    elif pcode == '62':
        print("Set compression mode")
        compression_code = args[3]
        print("\tCompression mode: {} (hex: {})".format(
            {"00": "uncompressed data", "01": "compressed data"}[compression_code],
            compression_code
        ))

    # Set print parameters
    elif pcode == '70':
        print("Set print parameters")
        print("\t" + " ".join(args[1:]))
        if len(args[1:]) != 42:
            print("ERROR: INCORRECT NUMBER OF PRINT PARAMETERS")
        output_param(1, "Paper Form", {"00": "Label/Gap", "01": "Tag/Marker",
                                       "02": "Tag/No TOF", "03": "Label/Marker"}[args[3]], args[3])
        output_param(2, "data_type (fixed value)", args[4])
        output_param(3, "Paper length (dots)", int("".join(args[5:7]), 16), "".join(args[5:7]))
        output_param(4, "Paper width (dots)", int("".join(args[7:9]), 16), "".join(args[7:9]))
        output_param(5, "Top margin (dots)", int("".join(args[9:11]), 16), "".join(args[9:11]))
        output_param(6, "Print area length (dots)", int("".join(args[11:13]), 16), "".join(args[11:13]))
        output_param(7, "Left margin (dots)", int("".join(args[13:15]), 16), "".join(args[13:15]))
        output_param(8, "Print area width (dots)", int("".join(args[15:17]), 16), "".join(args[15:17]))
        output_param(9, "Gap length (dots)", int("".join(args[17:19]), 16), "".join(args[17:19]))
        output_param(10, "Mark length (dots)", int("".join(args[19:21]), 16), "".join(args[19:21]))
        output_param(11, "Media type number", {"01": "Matte label paper", "02": "Glossy label paper",
                                               "03": "Synthetic paper", "04": "Matte tag", "05": "Thin matte tag"}[
            args[23]], args[23])
        # External option/Color mode/Rotation
        output_param(12, "External option/Color mode/Rotation", args[24])
        print("\t\t\t{} : {}".format("180degree rotated".rjust(17), int(args[24], 16) & (1 << 1) != 0))
        print("\t\t\t{} : {}".format("Color Mode".rjust(17),
                                     "Full color" if (int(args[24], 16) & (1 << 3) == 0) else "Monochrome"))
        print("\t\t\t{} : {}".format("External option".rjust(17),
                                     "External option invalid" if (
                                             int(args[24], 16) & (1 << 4) == 0) else "Auto cutter valid"))

        ## Print speed
        output_param(13, "Print speed (mm/sec)",
                     "Auto" if int(args[25], 16) == 0 else 10 * int(args[25], 16), args[25])

        ## Feed interval
        output_param(14, "Feed interval (sec)",
                     "Auto" if int(args[26], 16) == 0 else int(args[26], 16) / 10, args[26])

        ## Reserved / unused block
        print("\t(15-19 reserved / unused)")

        ## Registered form ID
        output_param(20, "Form ID", int("".join(args[32:30:-1]), 16), "".join(args[32:30:-1]))

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
        # print(" ".join(split_bytes(param)))
        print("\tTransfer order: {} {} {} {} ({} {} {} {})".format(
            chr(int(args[3], 16)), chr(int(args[4], 16)), chr(int(args[5], 16)), chr(int(args[6], 16)),
            args[3], args[4], args[5], args[6]
        ))
        print("\tOther transfer data (masks, etc in hex): {} {} {} {}".format(
            args[7], args[8], args[9], args[10]
        ))
        print("\tRaster count (bytes per transfer): {} (hex: {})".format(
            int("".join(args[11:15]), 16), " ".join(args[11:15])
        ))

    ## Execute raster skip
    elif pcode == '65':
        print("Execute raster skip")
        # print(" ".join(args))
        print("\tRaster skip: {} (hex: {})".format(
            int("".join(args[3:5]), 16), " ".join(args[3:5])
        ))

    ## Execute block skip
    elif pcode == '45':
        print("Execute block skip")
        # print(" ".join(args))
        print("\tBlock skip: {} (hex: {})".format(
            int("".join(args[3:5]), 16), " ".join(args[3:5])
        ))

    ## Esc F (block image transfer) (preferred over `Esc f`)
    elif pcode == '46':
        print("Esc F (preferred block image transfer)")
        big_endian_xfer_size = int("".join(args[4:0:-1]), 16)
        print("\tNumber of bytes being sent: {} (little endian hex: {})".format(
            big_endian_xfer_size, " ".join(args[1:5])))
        if big_endian_xfer_size + 7 != len(args):
            print("ERROR: improper num bytes sent; expected: {}, got: {}".format(big_endian_xfer_size + 7, len(args)))

        last_data_index = len(args[7:])-1
        last_index_to_print = min(last_data_index, 501)
        print("last index to print: {}".format(last_index_to_print))
        print(" ".join(args[7:last_index_to_print]))

        raster_stream = args[7:]
        expanded_raster_byte_length = expanded_num_raster_bytes(raster_stream)
        print("\tExpanded length in bytes: {}".format(expanded_raster_byte_length))
        print(" ".join(raster_stream[:100]))

    ## Esc f (block image transfer) (undocumented raster transfer)
    elif pcode == '66':
        print("Esc f (block image transfer: undocumented raster transfer)")
        big_endian_xfer_size = int("".join(args[2:0:-1]), 16)
        print("\tNumber of bytes being sent: {} (little endian hex: {})".format(
            big_endian_xfer_size, " ".join(args[1:3])))
        if big_endian_xfer_size + 3 != len(args):
            print("ERROR: improper num bytes sent; expected: {}, got: {}".format(big_endian_xfer_size + 3, len(args)))

        last_data_index = len(args[3:]) - 1
        last_index_to_print = min(last_data_index, 501)
        print("last index to print: {}".format(last_index_to_print))
        print(" ".join(args[3:last_index_to_print]))

        raster_stream = args[3:]
        expanded_raster_byte_length = expanded_num_raster_bytes(raster_stream)
        print("\tExpanded length in bytes: {}".format(expanded_raster_byte_length))
        print(" ".join(raster_stream[:100]))

    ## Maintenance commands
    elif pcode == '6d':
        print("Maintenance commands")
        # print(" ".join(args))
        # print("{}".format(args[:7]))
        if args[:7] != ['6d', '01', '00', '77', '05', '03', 'c4']:
            print("\tUNDOCUMENTED MAINTENANCE COMMANDS")
        else:
            print("\tReceived correct parameters for dotcount maint. cmds")

    ## Start printing
    elif pcode == '73':
        print("Start print / end of job/page")
        # print(args)

        ## cut interval stuff
        print("\tCut interval: {} (hex: {})".format(
            int("".join(args[3:5]), 16), " ".join(args[3:5])), end="")
        print(" (No interval cut)") if args[3:5] == ['00', '00'] else print()

        ## page vs job end
        print("\tPage|Job: {} (hex: {})".format(
            {"01": "page", "02": "job"}[args[5]], args[5]
        ))

        ## param1
        print("\tparam1 (hex): {}".format(args[6]))

    ## unknown command code
    else:
        print("UNRECOGNIZED COMMAND " + pcode)
