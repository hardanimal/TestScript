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
import struct

from aardvark_py import *
from com_utility import *

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
aa_slave_addr = 0x14
aa_handle = 32

#==========================================================================
# FUNCTIONS
#==========================================================================

def iic_send_upgrade_package66(reg_addr, package_buf):
    global aa_slave_addr
    global aa_handle
    
    data_out = array('B', [reg_addr])
    data_out = data_out + package_buf

    #print "handle:%d, slaveaddr:%d" % (aa_handle, aa_slave_addr)
    (ret, num_written) = aa_i2c_write_ext(aa_handle, aa_slave_addr, AA_I2C_NO_FLAGS, data_out)
    #print "ret = %d, num = %d" % (ret, num_written)
    
    if (ret != AA_I2C_STATUS_OK):
        aa_i2c_free_bus(aa_handle)
        return ret
    
    if (num_written != 67):
        return AA_I2C_WRITE_ERROR


    return ret

#------------------------------------------------------ smb_write_reg()
def smb_write_reg(reg_addr, wdata):
    # Write data to SMBus register
    #
    # slave_addr: slave_addr
    # reg_addr: register address offset
    # wdata: data to be write to SMBus register
    
    global aa_slave_addr
    global aa_handle
    
    data_out = array('B', [reg_addr, wdata])

    #print "handle:%d, slaveaddr:%d" % (aa_handle, aa_slave_addr)
    (ret, num_written) = aa_i2c_write_ext(aa_handle, aa_slave_addr, AA_I2C_NO_FLAGS, data_out)
    #print "ret = %d, num = %d" % (ret, num_written)
    
    if (ret != AA_I2C_STATUS_OK):
        aa_i2c_free_bus(aa_handle)
        return ret
    
    if (num_written != 2):
        return AA_I2C_WRITE_ERROR


    return ret



#------------------------------------------------------ smb_read_reg()
def smb_read_reg(reg_addr):
    # Read data From SMBus register
    #
    # slave_addr: slave_addr
    # reg_addr: register address offset

    global aa_slave_addr
    global aa_handle
    
    flag_read_finish = 0
    data_out = array('B', [reg_addr])


    # write register address
    (ret, num_written) = aa_i2c_write_ext(aa_handle, aa_slave_addr, AA_I2C_NO_STOP, data_out)  #AA_I2C_NO_STOP AA_I2C_NO_FLAGS
    if (ret != AA_I2C_STATUS_OK):
        aa_i2c_free_bus(aa_handle)
        return (ret, 0xFF)
    if (num_written != 1):
        return (AA_I2C_WRITE_ERROR, 0xFF)

    # read register data
    (ret, rdata, num_read)= aa_i2c_read_ext(aa_handle, aa_slave_addr, AA_I2C_NO_FLAGS, 1)
    if (ret == AA_I2C_STATUS_BUS_LOCKED):
        aa_i2c_free_bus(aa_handle)
        print "[ERR] timeout, reg_addr=%d" % reg_addr
        return (ret, 0xFF)
    else:
        flag_read_finish = 1



    if (flag_read_finish != 0): # finish read
        if (num_read != 1):
            print "num_read = ", num_read, ", expect: 1"
            return (AA_I2C_READ_ERROR, 0xFF)
        else:
            if (ret != AA_OK):
                return (ret, 0xFF)
            else:
                return (ret, rdata[0])
    else: # not finish read
        return (ret, 0xFF)
    






def smb_write_block(regaddr, length, wbuf):
    global aa_slave_addr
    global aa_handle
    
    data_out = array('B', [regaddr, length])
    data_out = data_out + wbuf
    (ret, num_written) = aa_i2c_write_ext(aa_handle, aa_slave_addr, AA_I2C_NO_FLAGS, data_out)

    if (ret != 0):
        aa_i2c_free_bus(aa_handle)
        return ret
    

    return ret


def smb_write_cmd(list_cmd):
    global aa_slave_addr
    global aa_handle
    
    data_out = array('B', list_cmd)
    (ret, num_written) = aa_i2c_write_ext(aa_handle, aa_slave_addr, AA_I2C_NO_FLAGS, data_out)
    if (ret != 0):
        aa_i2c_free_bus(aa_handle)
        print "[ERR] write cmd, ret=", ret, num_written
        return ret
    
    return ret



def smb_read_cmd(read_len):
    global aa_slave_addr
    global aa_handle
    
    (ret, rlist, num_read)= aa_i2c_read_ext(aa_handle, aa_slave_addr, AA_I2C_NO_FLAGS, read_len)
    if (ret == AA_I2C_STATUS_BUS_LOCKED):
        aa_i2c_free_bus(aa_handle)
        print "[ERR] read cmd", ret
        return (ret, rlist)
    
    return 0, rlist


def smb_wait_Reg_busy():
    i = 0
    for i in range(10):
        (ret, rdata) = smb_read_reg(1)
        if (ret != 0):
            return ret
        
        if (rdata == 0x00): # not busy 
            break
        
        smb_sleep_ms(5)
    
    if (i < 9):
        return 0
    else:
        print "<E> SMB REG Busy timeout"
        return SMB_R3_TIMEOUT

def enable_power_control_on_pin9():
    global aa_handle

    ret = aa_gpio_direction(aa_handle, AA_GPIO_SS)
    if(ret == AA_OK):
        print "Power Ctrl on Pin9(SS) is enabled"
    else:
        print "Failed to enable power control: error: %d" % ret

def power_on():
    global aa_handle

    ret = aa_gpio_set(aa_handle, AA_GPIO_SS)
    if(ret != AA_OK):
        print "Power on failed: error code: %d" % (ret)
        
def power_off():
    global aa_handle

    ret = aa_gpio_set(aa_handle, 0)
    if(ret != AA_OK):
        print "Power off failed: error code: %d" % (ret)
       



#------------------------------------------------------ smb_init()
def smb_init():
    
    global aa_port
    global aa_bitrate
    global aa_slave_addr
    global aa_handle
    
    if (len(sys.argv) != 3):
        print("usage: smb_validation BITRATE SLAVE_ADDRESS")
        sys.exit()
    
    aa_port = int(0)
    aa_bitrate = int(sys.argv[1]) 
    aa_slave_addr = int(sys.argv[2])

    print "++++++++++++++++++++++++++++++++"
    print "       <SMBus Validation>"
    print "--------------------------------"
    print "BITRATE = ",  aa_bitrate
    print "SLAVE_ADDRESS = ",  aa_slave_addr
    print "++++++++++++++++++++++++++++++++"
    

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

    print "aa_handle = %d" % aa_handle
    
    # Ensure that the I2C subsystem is enabled
    #aa_configure(aa_handle,  AA_CONFIG_SPI_I2C)
    aa_configure(aa_handle, AA_CONFIG_GPIO_I2C);

    #aa_i2c_pullup(aa_handle, AA_I2C_PULLUP_BOTH)

    aa_target_power(aa_handle, AA_TARGET_POWER_NONE)

    # Set the bitrate
    aa_bitrate = aa_i2c_bitrate(aa_handle, aa_bitrate)
    print "Bitrate set to %d kHz" % aa_bitrate

    # Set the bus lock timeout
    bus_timeout = aa_i2c_bus_timeout(aa_handle, BUS_TIMEOUT)
    print "Bus lock timeout set to %d ms" % bus_timeout
    
    aa_i2c_free_bus(aa_handle)
    
#------------------------------------------------------ smb_exit()
def smb_exit():
    aa_close(aa_handle)
    sys.exit()


def smb_sleep_ms(mscount):
    return aa_sleep_ms(mscount)


#------------------------------------------------------ display_main_menu()
def display_main_menu(menulist):
    while 1:
        menu_item = 0xFF
        print "==============================================================="
        print "                     [Menu of Test SMB]"
        print "---------------------------------------------------------------"
        for i in range(len(menulist)):
            print i, " --- ", menulist[i][0]

        option_input = raw_input("please select option: ")
        menu_item = int(option_input)
        if (menu_item > len(menulist)):
            print "input error! (0--%d)" % len(menulist)
            continue
        
        if (len(menulist[menu_item]) >= 3):
            menulist[menu_item][1](menulist[menu_item][2])
        else:
            menulist[menu_item][1]()

        

#==========================================================================
# MAIN PROGRAM
#==========================================================================
if __name__=="__main__":   # main function
    pass
    #main_menu = (["Enable",                          enable_power_control_on_pin9],
    #        ["Power On",                        power_on],
    #        ["Power Off",                       power_off],
    #        )
    #smb_init()
    #display_main_menu(main_menu);


    
