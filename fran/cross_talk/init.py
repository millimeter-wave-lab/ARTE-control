import numpy as np
import calandigital as calan
import corr, time
import argparse 
import control

parser = argparse.ArgumentParser(
    description="Plot spectra from an spectrometer model in ROACH.")
parser.add_argument("-i", "--ip", dest="ip", default=None,
    help="ROACH IP address.")
parser.add_argument("-b", "--bof", dest="boffile", 
    help="Boffile to load into the FPGA.")
parser.add_argument('-g', '--gain', dest='gain', type=float, default=1)

if __name__ == '__main__':
    args = parser.parse_args()
    roach = corr.katcp_wrapper.FpgaClient(args.ip)
    roach.upload_program_bof(args.boffile, 3000)
    time.sleep(1)
    roach_control = control.roach_control(roach)

    roach_control.set_snap_trigger()
    roach_control.initialize_10gbe()
    roach_control.reset_accumulators()
     
    gain = calan.float2fixed(np.array(args.gain), 32, 16)
    roach.write_int('gain', gain)
    
