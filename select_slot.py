#!/bin/env python

from __future__ import division, with_statement, print_function
from aardvark_py import *


# Step 1. detect aardvark
def detect_aardvark():

    print("Detecting Aardvark adapters...")

    # Find all the attached devices
    (num, ports, unique_ids) = aa_find_devices_ext(16, 16)

    if num == 1:
        print("%d device(s) found:" % num)

        # Print the information on each device
        for i in range(num):
            port      = ports[i]
            unique_id = unique_ids[i]

            # Determine if the device is in-use
            inuse = "(avail)"
            if (port & AA_PORT_NOT_FREE):
                inuse = "(in-use)"
                port  = port & ~AA_PORT_NOT_FREE

            # Display device port number, in-use status, and serial number
            print("    port = %d   %s  (%04d-%06d)" %
                  (port, inuse, unique_id // 1000000, unique_id % 1000000))
        
        return port

    else:
        print("No devices found.")
        return -1


if __name__ == "__main__":

    ret = detect_aardvark()
    if (ret < 0):
        sys.exit()
    
    handle = aa_open(ret)
    if (handle <= 0):
        print("Unable to open Aardvark device on port %d" % ret)
        print("Error code = %d" % handle)
        sys.exit()
        
    # Ensure that the I2C subsystem is enabled
    print("Setting to I2C mode")
    aa_configure(handle,  AA_CONFIG_SPI_I2C)
        
    # Enable the I2C bus pullup resistors (2.2k resistors).
    # This command is only effective on v2.0 hardware or greater.
    # The pullup resistors on the v1.02 hardware are enabled by default.
    aa_i2c_pullup(handle, AA_I2C_PULLUP_BOTH)

    # Power the EEPROM using the Aardvark adapter's power supply.
    # This command is only effective on v2.0 hardware or greater.
    # The power pins on the v1.02 hardware are not enabled by default.
    aa_target_power(handle, AA_TARGET_POWER_BOTH)

    # Set the bitrate
    bitrate = aa_i2c_bitrate(handle, 400)
    print("Bitrate set to %d kHz" % bitrate)

    # Set the bus lock timeout
    bus_timeout = aa_i2c_bus_timeout(handle, 150)
    print("Bus lock timeout set to %d ms" % bus_timeout)
    
    # Input slot number
    print("Please input the slot number: 0-MainBoard, 1-Slot1, 2-Slot2, 3-Slot3, 4-Slot4")
    line = input()
    slot=int(line)

    if True:
        # Perform the operation
        if (slot == 0):
            print("MUX to MainBoard")
            data_out = array('B', [0x00])
        elif (slot == 1):
            print("MUX to SLOT1")
            data_out = array('B', [0x01])
        elif (slot == 2):
            print("MUX to SLOT2")
            data_out = array('B', [0x02])
        elif (slot == 3):
            print("MUX to SLOT3")
            data_out = array('B', [0x04])
        elif (slot == 4):
            print("MUX to SLOT4")
            data_out = array('B', [0x08])
        else:
            print("UNSUPPORT SLOT, MUX to MainBoard")
            data_out = array('B', [0x00])
            
        aa_i2c_write(handle, 0x70, AA_I2C_NO_FLAGS, data_out)
        aa_sleep_ms(10)
        
    # Close the device
    aa_close(handle)
