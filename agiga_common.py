#!/bin/env python
#==========================================================================
# (c) 2004  Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Aardvark Sample Code
# File    : aadetect.py
#--------------------------------------------------------------------------
# Auto-detection test routine
#--------------------------------------------------------------------------
# Redistribution and use of this file in source and binary forms, with
# or without modification, are permitted.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#==========================================================================

#==========================================================================
# IMPORTS
#==========================================================================
import sys
from aardvark_py import *
from agiga_config import *

gAardvark = 0

#==========================================================================
# MAIN PROGRAM
#==========================================================================
ext_st_str = {
    AA_I2C_STATUS_OK               : "AA_I2C_STATUS_OK",
    AA_I2C_STATUS_BUS_ERROR        : "AA_I2C_STATUS_BUS_ERROR",
    AA_I2C_STATUS_SLA_ACK          : "AA_I2C_STATUS_SLA_ACK",
    AA_I2C_STATUS_SLA_NACK         : "AA_I2C_STATUS_SLA_NACK",
    AA_I2C_STATUS_DATA_NACK        : "AA_I2C_STATUS_DATA_NACK",
    AA_I2C_STATUS_ARB_LOST         : "AA_I2C_STATUS_ARB_LOST",   
    AA_I2C_STATUS_BUS_LOCKED       : "AA_I2C_STATUS_BUS_LOCKED",
    AA_I2C_STATUS_LAST_DATA_ACK    : "AA_I2C_STATUS_LAST_DATA_ACK" }

def aga_i2c_ext_status_string(status):
    return ext_st_str[status]

def aga_open_aardvark():
    print "-----------------------------------"
    print "Detecting Aardvark adapters..."

    # Find all the attached devices
    (num, ports, unique_ids) = aa_find_devices_ext(16, 16)
    
    if num <= 0:
        print "No devices found. Exit"
        sys.exit();
    
    print "%d device(s) found." % num
    
    # Print the information on each device
    found_free_port = 0;
    for i in range(num):
        port      = ports[i]
        unique_id = unique_ids[i]
    
        # Determine if the device is in-use
        if (not(port & AA_PORT_NOT_FREE)):
            print "port [%d] is free" % port
            found_free_port = 1;
            break
    if(found_free_port == 0):
        print "No free port found. Exit."
        sys.exit()

    # Open the device
    global gAardvark
    gAardvark = aa_open(port)
    if (gAardvark <= 0):
        print "Unable to open Aardvark on port %d" % ports
        print "Error code = %d" % gAardvark
        sys.exit()
    
    aa_configure(gAardvark, AA_CONFIG_SPI_I2C)
    aa_target_power(gAardvark, AA_TARGET_POWER_NONE)

    print "Set I2C address to 0x%x" % AGA_I2C_SLAVE_ADDR

    aa_i2c_pullup(gAardvark, AGA_I2C_PULLUP)
    if (AGA_I2C_PULLUP == AA_I2C_PULLUP_NONE):
        print "Disable the I2C pull-up"
    else:
        print "Enable the I2C pull-up"

    # Set the bitrate
    bitrate = aa_i2c_bitrate(gAardvark, AGA_I2C_BITRATE)
    print "Bitrate set to %d kHz" % bitrate
    
    # Set the bus lock timeout
    bus_timeout = aa_i2c_bus_timeout(gAardvark, AGA_I2C_BUS_TIMEOUT)
    print "Bus lock timeout set to %d ms" % bus_timeout

    print "-----------------------------------"

    return gAardvark

def aga_close_aardvark(handle = gAardvark):
    aa_close(handle)

def aga_reg_write(reg, data):
    data_out = array('B', [reg, data])
    global gAardvark

    (ret, count) = aa_i2c_write_ext(gAardvark, AGA_I2C_SLAVE_ADDR, AA_I2C_NO_FLAGS, data_out)
    if(ret != AA_I2C_STATUS_OK):
        print "I2C[0x%02x] Write error: %s, %d written" % (AGA_I2C_SLAVE_ADDR, aga_i2c_ext_status_string(ret), count)
    return data 

#def aga_reg_read(reg):
#    data_out = array('B', [reg])
#    data_in = array_u08(1);
#    global gAardvark
#    aa_i2c_write(gAardvark, AGA_I2C_SLAVE_ADDR, AA_I2C_NO_STOP, data_out)
#    (ret, data_in, count) = aa_i2c_read(gAardvark, AGA_I2C_SLAVE_ADDR, AA_I2C_NO_FLAGS, data_in)
#    if(ret != AA_I2C_STATUS_OK):
#        print "I2C[0x%02x] Read error: %s, %d read" % (AGA_I2C_SLAVE_ADDR, aga_i2c_ext_status_string(ret), count)
#    return data_in[0];

def aga_reg_read(reg):
    data_out = array('B', [reg])
    data_in  = array_u08(1);
    global gAardvark
    (ret, written, indata, read) = aa_i2c_write_read( \
            gAardvark, AGA_I2C_SLAVE_ADDR, AA_I2C_NO_FLAGS, data_out, data_in)
    if(ret != AA_I2C_STATUS_OK):
        if((ret & 0xff) != AA_I2C_STATUS_OK):
            print "I2C[0x%02x] Write error: %s, %d written" % \
                    (AGA_I2C_SLAVE_ADDR, aga_i2c_ext_status_string(ret), written)
        elif (((ret >> 8) & 0xff) != AA_I2C_STATUS_OK):
            print "I2C[0x%02x] Read error: %s, %d read" % \
                    (AGA_I2C_SLAVE_ADDR, aga_i2c_ext_status_string(ret), read)
    return data_in[0]



def w(reg, data):
    return aga_reg_write(reg, data)

def r(reg):
    data = aga_reg_read(reg)
    print "REG=0x%02X" % data
    return data

def array_to_int(data_in):
    val = 0;
    len = data_in.buffer_info()[1]
    size = min(len, 4)
    for i in range (size):
        val |= (data_in[i] << ((size - i - 1) * 8))
    return val

def aga_cmd_return_parse(data_in, ret_type='str'):
    """ return (ret_str, ret_data, ret_raw) """
    ret_raw = ""
    for d in data_in:
        ret_raw += ('{0:02X} '.format(d))
    if(ret_type == 'hex'):
        ret_data = array_to_int(data_in)
        ret_str = ret_raw
    elif (ret_type == 'int'):
        ret_data = array_to_int(data_in)
        ret_str = str(ret_data)
    elif (ret_type == 'str'):
        ret_data = 0
        ret_str = data_in.tostring()
    else:
        ret_data = 0
        ret_str = ''
        print "Error: Unknow type: %s" % ret_type

    return ret_str, ret_data, ret_raw.rstrip()

def aga_i2c_command(cmd, ret_bytes, ret_type='str'):
    """return (ret, ret_str, ret_data, ret_raw_str)
    ret_type: 'hex' 'int' 'str
    """
    global gAardvark
    ret = AA_I2C_STATUS_OK

    if(len(cmd) > 0):
        data_out = array('B');
        data_out.fromlist(cmd);

        if (ret_bytes == 0):
            flag = AA_I2C_NO_FLAGS
        else:
            flag = AA_I2C_NO_STOP

        (ret, count) = aa_i2c_write_ext(gAardvark, AGA_I2C_SLAVE_ADDR, flag, data_out)
        if(ret != AA_I2C_STATUS_OK):
            print "I2C[0x%02x] Write error: %s, %d written" % (AGA_I2C_SLAVE_ADDR, aga_i2c_ext_status_string(ret), count)
            return (ret, '', 0, '')

    if(ret_bytes > 0):
        data_in = array('B', '\0'*ret_bytes)
        (ret, data_in, count) = aa_i2c_read_ext(gAardvark, AGA_I2C_SLAVE_ADDR, AA_I2C_NO_FLAGS, data_in)
        if(ret != AA_I2C_STATUS_OK):
            print "I2C[0x%02x] Read error: %s, %d read" % (AGA_I2C_SLAVE_ADDR, aga_i2c_ext_status_string(ret), count)
            return (ret, '', 0, '')

        (ret_str, ret_data, ret_raw_str) = aga_cmd_return_parse(data_in, ret_type) 
    else:
        ret_str = ''
        ret_data = 0
        ret_raw_str = ''

    return ret, ret_str, ret_data, ret_raw_str


def aga_open():
    aga_open_aardvark()

def aga_close():
    aga_close_aardvark()


if __name__ == "__main__":
    (ret_str, ret_data, ret_raw) = aga_cmd_return_parse(array('B',[0x00, 0x07]), 'hex')
    print "ret_str : %s" % ret_str
    print "ret_data: %d" % ret_data
    print "ret_datas: %s" % str(ret_data)
    print "ret_raw : %s" % ret_raw
    print ""

    (ret_str, ret_data, ret_raw) = aga_cmd_return_parse(array('B',[0x04, 0x4c]), 'int')
    print "ret_str : %s" % ret_str
    print "ret_data: %d" % ret_data
    print "ret_datas: %s" % str(ret_data)
    print "ret_raw : %s" % ret_raw
    print ""

    (ret_str, ret_data, ret_raw) = aga_cmd_return_parse(array('B',[0x4d, 0x61, 0x64, 0x61, 0x67, 0x61, 0x73, 0x63]))
    print "ret_str : %s" % ret_str
    print "ret_data: %d" % ret_data
    print "ret_datas: %s" % str(ret_data)
    print "ret_raw : %s" % ret_raw
    print ""
