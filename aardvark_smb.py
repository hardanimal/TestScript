#########################################################################
#
#  SMBus validation module.
#  This file is used on computer for Aardvark tool.
#  
#  Usage (example):    >> python smb_validation.py 100 20
#
#########################################################################


#==========================================================================
# IMPORTS
#==========================================================================
import sys

from aardvark_py import *

ret_names = {
        0 : "A_OK",
       -1 : "A_UNABLE_TO_LOAD_LIBRARY",
       -2 : "A_UNABLE_TO_LOAD_DRIVER",
       -3 : "A_UNABLE_TO_LOAD_FUNCTION",
       -4 : "A_INCOMPATIBLE_LIBRARY",
       -5 : "A_INCOMPATIBLE_DEVICE" ,
       -6 : "A_COMMUNICATION_ERROR",
       -7 : "A_UNABLE_TO_OPEN",
       -8 : "A_UNABLE_TO_CLOSE",
       -9 : "A_INVALID_HANDLE",
      -10 : "A_CONFIG_ERROR",
     -100 : "A_I2C_NOT_AVAILABLE",
     -101 : "A_I2C_NOT_ENABLED",
     -102 : "A_I2C_READ_ERROR",
     -103 : "A_I2C_WRITE_ERROR",
     -104 : "A_I2C_SLAVE_BAD_CONFIG",
     -105 : "A_I2C_SLAVE_READ_ERROR",      
     -106 : "A_I2C_SLAVE_TIMEOUT",
     -107 : "A_I2C_DROPPED_EXCESS_BYTES",
     -108 : "A_I2C_BUS_ALREADY_FREE",
     -200 : "A_SPI_NOT_AVAILABLE",
     -201 : "A_SPI_NOT_ENABLED",
     -202 : "A_SPI_WRITE_ERROR",
     -203 : "A_SPI_SLAVE_READ_ERROR",
     -204 : "A_SPI_SLAVE_TIMEOUT",
     -205 : "A_SPI_DROPPED_EXCESS_BYTES",
     -400 : "A_GPIO_NOT_AVAILABLE",
     -500 : "A_I2C_MONITOR_NOT_AVAILABLE",
     -501 : "A_I2C_MONITOR_NOT_ENABLED",
     
    1 : "A_I2C_STATUS_BUS_ERROR",
    2 : "A_I2C_STATUS_SLA_ACK",
    3 : "A_I2C_STATUS_SLA_NACK",
    4 : "A_I2C_STATUS_DATA_NACK",
    5 : "A_I2C_STATUS_ARB_LOST",
    6 : "A_I2C_STATUS_BUS_LOCKED",
    7 : "A_I2C_STATUS_LAST_DATA_ACK",
}

class SmbException(BaseException):
    def __init__(self, rw_type, reg, ret_code):
        self.rw_type = rw_type
        if isinstance(ret_code, int):
            self.ret_code = ret_names[ret_code]
        else:
            self.ret_code = ret_code
        self.reg = reg
    def __str__(self):
        return repr('SMB Op Failed: Reg[0x%02X], Op[%s], ret[%s]' % (self.reg, self.rw_type, repr(self.ret_code)))

#==========================================================================
# CONSTANTS
#==========================================================================
BUS_TIMEOUT = 25  # ms
SLAVE_ADDRESS = 0x14

SMB_OK          =    0
SMB_FAIL        =    -31
SMB_TIMEOUT     =    -32
SMB_NACK        =    -33
SMB_R3_TIMEOUT  =    -34

#==========================================================================
# VARIABLE
#==========================================================================

aa_port = 0
aa_bitrate = 0
aa_slave_addr = 0
aa_handle = None
aa_enable_pullup = False

#==========================================================================
# FUNCTIONS
#==========================================================================


def smb_set_addr(addr):
    global aa_slave_addr
    aa_slave_addr = addr & 0xFF
    
def smb_set_bitrate(bitrate_khz):
    aa_i2c_bitrate(aa_handle, bitrate_khz)


#------------------------------------------------------ smb_write_reg()
def smb_write_reg(reg_addr, wdata):
    # Write data to SMBus register
    #
    # reg_addr: register address offset
    # wdata: data to be write to SMBus register
    
    data_out = array('B', [reg_addr, wdata])
    (ret, num_written) = aa_i2c_write_ext(aa_handle, aa_slave_addr, AA_I2C_NO_FLAGS, data_out)    
    if (ret != AA_I2C_STATUS_OK):
        aa_i2c_free_bus(aa_handle)
        raise SmbException('w', reg_addr, ret)
    if (num_written != 2):
        aa_i2c_free_bus(aa_handle)
        raise SmbException('w', reg_addr, 'num_written != 2')

    return ret



#------------------------------------------------------ smb_read_reg()
def smb_read_reg(reg_addr):
    # Read data From SMBus register
    #
    # slave_addr: slave_addr
    # reg_addr: register address offset

    data_out = array('B', [reg_addr])

    # write register address
    (ret, num_written) = aa_i2c_write_ext(aa_handle, aa_slave_addr, AA_I2C_NO_STOP, data_out)  #AA_I2C_NO_STOP AA_I2C_NO_FLAGS
    if (ret != AA_I2C_STATUS_OK):
        aa_i2c_free_bus(aa_handle)
        raise SmbException('w', reg_addr, ret)
    if (num_written != 1):
        aa_i2c_free_bus(aa_handle)
        raise SmbException('w', reg_addr, 'num_written != 1')

    # read register data
    (ret, rdata, num_read)= aa_i2c_read_ext(aa_handle, aa_slave_addr, AA_I2C_NO_FLAGS, 1)
    if (ret != AA_I2C_STATUS_OK):
        aa_i2c_free_bus(aa_handle)
        raise SmbException('r', reg_addr, ret)
    if (num_read != 1):
        aa_i2c_free_bus(aa_handle)
        raise SmbException('r', reg_addr, 'num_read != 1')
    
    return ret, rdata[0]


def write(reg_addr, d0, *args):
    
    data_out = array('B', [reg_addr, d0] + list(args))
    
    (ret, num_written) = aa_i2c_write_ext(aa_handle, aa_slave_addr, AA_I2C_NO_FLAGS, data_out)    
    if (ret != AA_I2C_STATUS_OK):
        aa_i2c_free_bus(aa_handle)
        raise SmbException('w', reg_addr, ret)
    out_len = len(data_out)
    if (num_written != out_len):
        aa_i2c_free_bus(aa_handle)
        raise SmbException('w', reg_addr, 'num_written != %d' % out_len)

    return ret

def read(reg_addr, read_num=1):
    
    data_out = array('B', [reg_addr])
    (ret, num_written) = aa_i2c_write_ext(aa_handle, aa_slave_addr, AA_I2C_NO_STOP, data_out)    
    if (ret != AA_I2C_STATUS_OK):
        aa_i2c_free_bus(aa_handle)
        raise SmbException('w', reg_addr, ret)
    out_len = len(data_out)
    if (num_written != out_len):
        aa_i2c_free_bus(aa_handle)
        raise SmbException('w', reg_addr, 'num_written != %d' % out_len)
    
    (ret, rdata, num_read)= aa_i2c_read_ext(aa_handle, aa_slave_addr, AA_I2C_NO_FLAGS, read_num)
    if (ret != AA_I2C_STATUS_OK):
        aa_i2c_free_bus(aa_handle)
        raise SmbException('r', reg_addr, ret)
    if (num_read != read_num):
        aa_i2c_free_bus(aa_handle)
        raise SmbException('r', reg_addr, 'num_read != read_num')

    return tuple(rdata)


def smb_init(aa_port, bitrate, aa_addr, enable_pullup):
    
    global aa_slave_addr
    global aa_handle
    global aa_bitrate
    global aa_enable_pullup
    
    aa_slave_addr = aa_addr
    aa_bitrate = bitrate
    
    if aa_handle is not None:
        smb_exit()
    

    (port_num, ports) = aa_find_devices(1)
    if port_num > 0:
        aa_port = ports[0]
        print "%d device found: port = %d" % (port_num, aa_port)
    else:
        print "no device found"
        sys.exit()

    aa_handle = aa_open(aa_port)
    if (aa_handle <= 0):
        print "Unable to open Aardvark device on port %d" % aa_port
        print "Error code = %d" % aa_handle
        sys.exit()
    
    # Ensure that the I2C subsystem is enabled
    aa_configure(aa_handle,  AA_CONFIG_SPI_I2C)

    aa_enable_pullup = enable_pullup
    if aa_enable_pullup == True:   
        aa_i2c_pullup(aa_handle, AA_I2C_PULLUP_BOTH)
    else:
        aa_i2c_pullup(aa_handle, AA_I2C_PULLUP_NONE)
        
    aa_target_power(aa_handle, AA_TARGET_POWER_NONE)

    # Set the bitrate
    aa_i2c_bitrate(aa_handle, aa_bitrate)
    
    # Set the bus lock timeout
    aa_i2c_bus_timeout(aa_handle, BUS_TIMEOUT)
    
    aa_i2c_free_bus(aa_handle)
    
def smb_exit():
    aa_close(aa_handle)

def smb_reinit(**kwargs):
    ''' 
    Supported parameter: port, slave_addr, bitrate, enable_pullup
    '''
    smb_exit()
    
    global aa_port
    global aa_slave_addr
    global aa_handle
    global aa_bitrate
    global aa_enable_pullup
    
    if 'slave_addr' in kwargs:
        aa_slave_addr = kwargs['slave_addr']
    if 'bitrate' in kwargs:
        aa_bitrate = kwargs['bitrate']
    if 'enable_pullup' in kwargs:
        aa_enable_pullup = kwargs['enable_pullup']
    
    if 'port' in kwargs:
        aa_port = kwargs['port']
    
    smb_init(aa_port, aa_bitrate, aa_slave_addr, aa_enable_pullup)
    


#==========================================================================
# MAIN PROGRAM
#==========================================================================
if __name__=="__main__":   # main function
    pass
    
