import sys
sys.path.append( "..//")
sys.path.append( ".//")


import os

from smb_aardvark import *

VPD_SRC_DEVICE = 1
VPD_SRC_FILE   = 2


LOCK = 1
UNLOCK = 2

tint = 1
tstr = "abc"


#==========================================    User Define, based on Project
BAORD_TYPE = "Garnet"
dump_file_name = "eeprom.dump"

EEPROM_REG_ADDRL = 0
EEPROM_REG_ADDRH = 1
EEPROM_REG_RWDATA = 2

LOCK_REG = 0x40
reg_list = [0x03, 0x04, 0x05, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A]
#            string                  type          length   start_address
vpd_list = (
            ["ModelNumber ",    type(tstr),     16,     0x000],
            ["ES_FWREV0   ",    type(tint),     1,      0x010],
            ["ES_FWREV1   ",    type(tint),     1,      0x011],
            ["ES_HWREV    ",    type(tint),     1,      0x012],
            ["CapPartNum  ",    type(tstr),     12,     0x020],
            ["SerialNum   ",    type(tstr),     8,      0x030],
            ["PCBVersion  ",    type(tstr),     2,      0x040],
            ["ManufacDate ",    type(tstr),     4,      0x042],
            ["ManufacName ",    type(tstr),     2,      0x046],
            ["CINIT       ",    type(tint),     1,      0x050],            
            ["MINTEMP     ",    type(tint),     1,      0x060],
            ["MAXTEMP     ",    type(tint),     1,      0x061],
            ["LastCAP     ",    type(tint),     1,      0x100],
            ["MINCAP      ",    type(tint),     1,      0x101],
            ["MAXCAP      ",    type(tint),     1,      0x102],
            ["MINVCAP     ",    type(tint),     1,      0x103],
	          ["MAXVCAP     ",    type(tint),     1,      0x104],  
            ["MCAPINT     ",    type(tint),     1,      0x105],
            ["ES_RUNTIME0 ",    type(tint),     1,      0x200],
            ["ES_RUNTIME1 ",    type(tint),     1,      0x201],
            ["T_LASTPF    ",    type(tint),     4,      0x202],
            ["PWRCYCS     ",    type(tint),     2,      0x206],
	          ["RUNLOG_IDX  ",    type(tint),     2,      0x300],
            )
#==========================================    User Define, based on Project

read_file_h = 0
file_string= ""

#write eeprom byte
def write_ee_byte(addr, wdata):
    ret = smb_write_reg(EEPROM_REG_ADDRL, addr & 0xFF)
    ret |= smb_write_reg(EEPROM_REG_ADDRH, (addr >> 8) & 0xFF)
    ret |= smb_write_reg(EEPROM_REG_RWDATA, wdata & 0xFF)
    
    if (ret != 0):
        print "<E>write_ee_byte 1"
    
    return ret
    
#read single_byte eeprom 
def read_ee_byte(addr):
    ret = smb_write_reg(EEPROM_REG_ADDRL, addr & 0xFF)
    ret |= smb_write_reg(EEPROM_REG_ADDRH, (addr >> 8) & 0xFF)
    if (ret != 0):
        print "<E>read_ee_byte 1"
        return (ret, 0)
    
    (ret, rdata) = smb_read_reg(EEPROM_REG_RWDATA)
    
    if (ret != 0):
        print "<E>read_ee_byte 2"
    
    return (ret, rdata)

#Quick read eeprom content
def quick_show_eeprom(addr, len):
    print ""
    
    if (addr%16!=0):
        fg = addr%16
        fl = 16 - fg
        print "0x%03X\t"%(addr - fg),
        for i in range(fg):
            print "  ",
    
    for i in range(len):
        if ((i+addr)%16 == 0):
            print ""
            print "0x%03X\t"%(i+addr),
        ret, rdata = read_ee_byte(i+addr)
        print "%02X"%rdata,
    
    print ""
    return ret


def file_read_byte(addr):
    global read_file_h
    read_file_h.seek(addr)
    ret, rdata = binary_read_byte(read_file_h)
    if ret != 0:
        print "<E> read byte fail 1"
        return ret, 0
    return ret, rdata

#find analyze file
def find_analyze_file():
    global file_string
    (ret, img_file) = file_selection("analyze files", ".ebf", ".//")
    file_string = img_file
    return ret

#analyze VPD information
def analyze_VPD(src):
    global read_file_h
    
    print "\n--------------------"
    print BAORD_TYPE, "VPD Analyze"
    print "--------------------"

    if (VPD_SRC_FILE == src):
        read_func = file_read_byte
        ret = find_analyze_file()
        if ret != 0:
            return ret
        try:
            read_file_h = open(file_string, 'rb')
        except:
            print "[ERR] Unable to open file '" + file_string + "'"
            return ret
    elif (VPD_SRC_DEVICE == src):
        read_func = read_ee_byte

    for item in vpd_list:
        print item[0], "--",
        
        if (item[1] == type(tint)):
            idata = 0
            for i in reversed(range(item[2])):
                (ret, rdata) = read_func(item[3] + i)
                if ret != 0:
                    return ret
                idata = (idata << 8) + rdata
            print idata, hex(idata),
        
        if (item[1] == type(tstr)):
            gstring = ""
            for i in range(item[2]):
                (ret, rdata) = read_func(item[3] + i)
                if ret != 0:
                    return ret
                cdata = struct.pack("B", rdata)
                print cdata,
        print ""
    if (VPD_SRC_FILE == src):
        read_file_h.close()

#Show the run log
def print_runlog():
    print "\n--------------------"
    print BAORD_TYPE, "Run LOG"
    print "--------------------"

    logidx = 0
    for i in reversed(range(2)):
        (ret, rdata) = read_ee_byte(0x2b4+i)
        if ret !=0:
            return ret
        logidx = (logidx<<8) + rdata
    print logidx
        
    for i in range(0x200):
        gstring = ""
        (ret, rdata) = read_ee_byte(0x0+i)
        if ret != 0:
            return ret
        cdata = struct.pack("B", rdata)
        print cdata,
        
    print '-------\n'
    
    for i in range(330):
        gstring = ""
        (ret, rdata) = read_ee_byte(0x2b6+i)
        if ret != 0:
            return ret
        cdata = struct.pack("B", rdata)
        #cdata = str(rdata)
        print cdata,
        
    print ""
        
#analyze VPD information
def show_GTG():
    print "\n--------------------"
    print BAORD_TYPE, "register Analyze"
    print "--------------------"

    (ret, rdata) = smb_read_reg(0x20)
    if (ret != 0):
        print "[ERR] read error! <%d>" % ret
    else:
        print "HWREADY: %x" % (rdata)   
    (ret, rdata) = smb_read_reg(0x21)
    if (ret != 0):
        print "[ERR] read error! <%d>" % ret
    else:
        print "GTG: %x" % (rdata) 

    (ret, rdata) = smb_read_reg(0x22)
    if (ret != 0):
        print "[ERR] read error! <%d>" % ret
    else:
        print "GTG_WARN: %x" % (rdata)  

    (ret, rdata) = smb_read_reg(0x23)
    if (ret != 0):
        print "[ERR] read error! <%d>" % ret
    else:
        print "PGEM_STATUS: %x" % (rdata)                 

    (ret, rdata) = smb_read_reg(0x24)
    if (ret != 0):
        print "[ERR] read error! <%d>" % ret
    else:
        print "ES_TEMP0: %d" % (rdata)
    
    
    (ret, rdata) = smb_read_reg(0x25)
    if (ret != 0):
        print "[ERR] read error! <%d>" % ret
    else:
        print "ES_TEMP1: %d" % (rdata)   
        
    (ret, rdata) = smb_read_reg(0x26)
    if (ret != 0):
        print "[ERR] read error! <%d>" % ret
    else:
        print "VIN: %d" % (rdata)         

    (ret, rdata) = smb_read_reg(0x27)
    if (ret != 0):
        print "[ERR] read error! <%d>" % ret
    else:
        print "VCap: %d" % (rdata)  

    (ret, rdata) = smb_read_reg(0x28)
    if (ret != 0):
        print "[ERR] read error! <%d>" % ret
    else:
        print "Charge Time: %d" % (rdata)  

    (ret, rdata) = smb_read_reg(0x29)
    if (ret != 0):
        print "[ERR] read error! <%d>" % ret
    else:
        print "POR_Volt: %d" % (rdata)  

    (ret, rdata) = smb_read_reg(0x2a)
    if (ret != 0):
        print "[ERR] read error! <%d>" % ret
    else:
        print "TChg_Volt: %d" % (rdata)
          
#export the eeprom to file
def dump_eeprom_to_file():
    try:
        dump_file = open(dump_file_name, 'wb')
    except:
        print "[ERR] Unable to create file '" + dump_file_name + "'"
        return
    for i in range(1024):
        (ret, rdata) = read_ee_byte(i)
        if ret != 0:
            return ret
        binary_write_byte(dump_file, rdata)
        if (i % 50 == 0):
            print ".",
    dump_file.close()
    print "over"
    
#import the file to eeprom
def update_whole_eeprom():
    global read_file_h
    ret = find_analyze_file()
    if ret != 0:
        return ret
    try:
        read_file_h = open(file_string, 'rb')
    except:
        print "[ERR] Unable to open file '" + file_string + "'"
        return ret
    
    read_file_h.seek(0)
    for i in range(1024):
        ret, rdata = binary_read_byte(read_file_h)
        if ret != 0:
            return ret
        ret = write_ee_byte(i, rdata)
        if ret != 0:
            return ret
        if (i % 50 == 0):
            print ".",
    
    print "over"
    read_file_h.close()
    return ret



def eeprom_exit():
    smb_exit()

#read eeprom 
def show_eeprom():
    start_addr = input("input start address: ")
    len = input("input length: ")
    quick_show_eeprom(start_addr, len)

#cmd write ee byte
def cmd_write_ee():
    addr = input("input EEPROM address: ")
    wdata = input("input write data: ")
    ret = write_ee_byte(addr, wdata)
    if ret == 0:
        print "[",hex(wdata),"] --> (", hex(addr), ")"
        print "[",(wdata),"] --> (", (addr), ")"

#cmd read ee byte
def cmd_read_ee():
    addr = input("input EEPROM address: ")
    ret, rdata = read_ee_byte(addr)
    if ret == 0:
        print "[",hex(rdata),"] <-- (", hex(addr), ")"
        print "[",(rdata),"] <-- (", (addr), ")"

#lock and unlock write the second 512byte
def lock_unlock_rw(lock):
    if (lock == LOCK):
        smb_write_reg(LOCK_REG, 0)
    elif (lock == UNLOCK):
        smb_write_reg(LOCK_REG, 0x45)



#read or write register 
def smb_custom_command():
    while 1:
        print "------------"
        print "0 - quit to main menu"
        print "1 - write one register"
        print "2 - read one register"
        operation_cmd = int(input("operation:"))
        if (operation_cmd > 2 ):
            print "operation input error!"
            return
        
        if (operation_cmd == 1): ## write
            reg_addr = input("register address:")
            wdata = input("write data:")
            ret = smb_write_reg(reg_addr, wdata)
            if (ret != 0):
                print "[ERR] write error! <%d>" % ret
            else:
                print "write: %d-->address(%d)" % (wdata, reg_addr)
        elif (operation_cmd == 2): ## read
            reg_addr = input("register address:")
            (ret, rdata) = smb_read_reg(reg_addr)
            if (ret != 0):
                print "[ERR] read error! <%d>" % ret
            else:
                print "read: %d<--address(%d)" % (rdata, reg_addr)
        elif (operation_cmd == 0): ## quit
            return
            

#read tempreture history
def get_temp_his():
    string_array = ["70 oC -- Above    ",
                    "65 oC -- 70 oC:   ",
                    "60 oC -- 65 oC:   ",
                    "55 oC -- 60 oC:   ",
                    "50 oC -- 55 oC:   ",
                    "45 oC -- 50 oC:   ",
                    "40 oC -- 45 oC:   ",
                    "35 oC -- 40 oC:   ",
                    "30 oC -- 35 oC:   ",
                    "25 oC -- 30 oC:   ",
                    "20 oC -- 25 oC:   ",
                    "15 oC -- 20 oC:   ",
                    "10 oC -- 15 oC:   ",
                    "5  oC -- 10 oC:   ",
                    "0  oC --  5 oC:   ",
                    "Below --  0 oC:   "]
    
    print "PGM Temperature History: "
    print "-------------------"
    

    data_arry = array('H')
    
    for i in range(16):
        (ret1, rdata1) = read_ee_byte(0x062 + i * 2)
        (ret2, rdata2) = read_ee_byte(0x062 + i * 2 + 1)
        if (ret1 != 0 or ret2 != 0):
            return -1
        data_arry.append(rdata1 | (rdata2 << 8))

    iloop = 0
    total = 0
    for hour in data_arry:
        if (hour == 0xFFFF):
            hour = 0
        print string_array[iloop], hour, "hours"
        total = total + hour
        iloop = iloop + 1

    print "--------"
    print "total: ", total, "hours"
    
    return 0

#read capacitance history
def get_cap_his():
    string_array = ["120% -- Above   ",
                    "115% -- 120%:   ",
                    "110% -- 115%:   ",
                    "105% -- 110%:   ",
                    "100% -- 105%:   ",
                    " 95% -- 100%:   ",
                    " 90% --  95%:   ",
                    " 85% --  90%:   ",
                    " 80% --  85%:   ",
                    " 75% --  80%:   ",
                    " 70% --  75%:   ",
                    " 65% --  70%:   ",
                    " 60% --  65%:   ",
                    " 55% --  60%:   ",
                    " 50% --  55%:   ",
                    "Below--  50%:   "]
    
    print "PGM Capacity History: "
    print "-------------------"

    data_arry = array('H')
    for i in range(16):
        (ret1, rdata1) = read_ee_byte(0x106 + i * 2)
        (ret2, rdata2) = read_ee_byte(0x106 + i * 2 + 1)
        if (ret1 != 0 or ret2 != 0):
            return -1
        data_arry.append(rdata1 | (rdata2 << 8))

    iloop = 0
    total = 0
    for days in data_arry:
        if (days == 0xFFFF):
            days = 0
        print string_array[iloop], days, "days"
        total = total + days
        iloop = iloop + 1
        
    print "--------"
    print "total: ", total, "days"
    
    
    return 0

#write manufactory information
def manufac_input_henry():
    print "\nPlease fill the content below:"
    
    for item in vpd_list[:10]:
        
        if (item[1] == type(tstr)):
            str_input = raw_input(item[0]+" : ")
            print len(str_input)
            if (len(str_input) != item[2]):
                print "error length, it should be %d bytes."%item[2]
                continue
            for i in range(item[2]):
                wdata = struct.unpack("B", str_input[i])[0]
                ret = write_ee_byte(item[3]+i, wdata)
                if (ret != 0):
                    print "error write eeprom"
                    return
        
        elif (item[1] == type(tint)):
            num_input = input(item[0]+" : ")
            ret = write_ee_byte(item[3], num_input)
            if (ret != 0):
                print "error write eeprom"
                return
        
    return


main_menu = (["Quit",                                   eeprom_exit],
             ["custom register",                        smb_custom_command],
             ["Show EEPROM",                            show_eeprom],
             ["GTG Show",                               show_GTG],
             ["Analyze VPD on Device",                  analyze_VPD, VPD_SRC_DEVICE],
             ["Analyze VPD in File",                    analyze_VPD, VPD_SRC_FILE],
             ["Write EEPROM Byte",                      cmd_write_ee],
             ["Read EEPROM Byte",                       cmd_read_ee],
             ["Unlock RW > 512",                        lock_unlock_rw, UNLOCK],
             ["Lock RW > 512",                          lock_unlock_rw, LOCK],
             ["Dump EEPROM to "+dump_file_name,         dump_eeprom_to_file],
             ["Program Device EEPROM",                  update_whole_eeprom],
             ["Get Temperature History",                get_temp_his],
             ["Get Capacity History",                   get_cap_his],
			       ["Show RUNLOG",                            print_runlog],
             ["Manufacture Input (henry)",              manufac_input_henry],
             )
def allreg():
    print "#############Read all registers##################"
    for i in reg_list:
        
        (ret, rdata) = smb_read_reg(i)
        print "Register 0x%x value is 0x%x " % (i, rdata)
        aa_sleep_ms(20)
    print "#############Read all registers##################"

if __name__ == '__main__':
    smb_init()
    

    display_main_menu(main_menu)
    
    
    smb_exit()
    
