#########################################################################
#
#  SMBus validation module.
#  This file is used on computer for AMD board Linux system.
#  
#  Usage (example):    >> python smb_validation.py 100 20
#
#########################################################################


#==========================================================================
# IMPORTS
#==========================================================================
import sys
import struct

from com_utility import *
import amdSMBLib



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

smb_slave_addr = 0x14



#==========================================================================
# FUNCTIONS
#==========================================================================

#------------------------------------------------------ smb_write_reg()
def smb_write_reg(reg_addr, wdata):
    return amdSMBLib.amd_smb_write_reg(reg_addr, wdata)








#------------------------------------------------------ smb_read_reg()
def smb_read_reg(reg_addr):
    return amdSMBLib.amd_smb_read_reg(reg_addr)
    
    
    

def smb_write_block(regaddr, length, wbuf):
    return amdSMBLib.amd_smb_write_block(regaddr, length, wbuf)
    
    
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
        

#------------------------------------------------------ smb_init()
def smb_init():
    global smb_slave_addr

    if (len(sys.argv) != 2):
        print("usage: smb_validation SLAVE_ADDRESS")
        sys.exit()
    
    if (amdSMBLib.amd_smb_init() != SMB_OK):
        print("fail to init SMB on AMD board")
        sys.exit()
	
    smb_slave_addr = int(sys.argv[1])

    print "++++++++++++++++++++++++++++++++"
    print "       <SMBus Validation>"
    print "--------------------------------"
    print "SLAVE_ADDRESS = ",  smb_slave_addr
    print "++++++++++++++++++++++++++++++++"
    amdSMBLib.amd_smb_set_slave_address(smb_slave_addr)







    
#------------------------------------------------------ smb_exit()
def smb_exit():
    if (amdSMBLib.amd_smb_close() != SMB_OK):
        print("fail to close SMB on AMD board")
    sys.exit()


	
	
	
	
	
#------------------------------------------------------ smb_sleep_ms()
def smb_sleep_ms(mscount):
    return amdSMBLib.amd_smb_sleep_ms(mscount)







#------------------------------------------------------ smb_download_image_66()
UPGRADE_ABORT = 0x1 << 7
UPGRADE_INPRG = 0x1 << 3
UPGRADE_TXERR = 0x1 << 2
UPGRADE_READY = 0x1 << 1
UPGRADE_PMODE = 0x1 << 0




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
    #smb_init()
    #display_main_menu(main_menu)
    #smb_exit()
	pass
else:
    print "<smb_amd.py was included>"


    
