import sys
sys.path.append( "..//")
sys.path.append( ".//")


import os

if os.name == "nt":
    from smb_aardvark import *
elif os.name == "posix":
    from smb_amd import *
else:
    sys.exit()


from t_all_function_garnet import *
allreglist = {"CAPMEAS":0x03,"RESET_SYS":0x04,"RESET_MIN_MAX":0x05,
	            "ES_CHARGE_TIMEOUT0":0x10,"ES_CHARGE_TIMEOUT1":0x11,
	            "MIN_ES_OPERATING_TEMP":0x12,"MAX_ES_OPERATING_TEMP":0x13,
	            "ES_ATTRIBUTES":0x14,"ES_TECH":0x15,"ES_LIFETIME":0x16,
	            "HWREADY":0x20,"GTG":0x21,"GTG_WARN":0x22,"PGEMSTAT":0x23,
	            "ES_TEMP0":0x24,"ES_TEMP1":0x25,"VIN":0x26,"VCAP":0x27,"CHG_TIME":0x28,
	            "POR_V":0x29,"TCHG_V":0x2A}

def eeprom_exit():
    smb_exit()


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
        (ret1, rdata1) = read_ee_byte(0x0062 + i * 2)
        (ret2, rdata2) = read_ee_byte(0x0062+ i * 2 + 1)
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


def get_t_run ():
    
    #"-----------Run time----------"
    
    data = 0

    for i in range(1):
        (ret1, rdata1) = read_ee_byte(0x200 )
        (ret2, rdata2) = read_ee_byte(0x201 )
        if (ret1 != 0 ):
            return -1
        data = rdata1 + (rdata2<<8)


    print "Run time ----------------------",data," hours"


def get_t_lastpf ():
    
    #"-----------Run time at last power fail----------"
    
    (ret1, rdata1) = read_ee_byte(0x202 )
    if (ret1 != 0):
        return -1

    print "Run time at last power fail ---",rdata1," hours"


def get_pwrcycs ():
    
    #"-----------power cycles----------"
   
    (ret1, rdata1) = read_ee_byte(0x206 )
    (ret2, rdata2) = read_ee_byte(0x207 )
    if (ret1 != 0 or ret2 != 0):
        return -1
    data = rdata1 + (rdata2<<8)

    print "Power cycles ------------------", data," times"


def get_lastcap ():
    
    #"-----------Last PCT cap measure----------"


    (ret1, rdata1) = read_ee_byte(0x100 )
 
    if (ret1 != 0):
        return -1

    print "Last PCT cap measure  ----------",rdata1,"%"


def get_model ():
    j = []
    #"-----------Garnet module number----------"
    for i in range(16):
        (ret1, rdata1) = read_ee_byte(0x0000 + i )
        j.append(rdata1)
        if (ret1 != 0):
            return -1 

    print "Garnet Model Number:%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c" % (j[0],j[1],j[2],j[3],j[4],j[5],j[6],j[7],j[8],j[9],j[10],j[11],j[12],j[13],j[14],j[15])


def get_fw_ver ():

    #"-----------Garnet fw version----------"

    for i in range(1):
        (ret1, rdata1) = read_ee_byte(0x0010 )
        (ret2, rdata2) = read_ee_byte(0x0011 )
     
    if (ret1 != 0 or ret2 != 0):
        return -1
       
    print "Garnet FW version: V%x.%x" % (rdata1,rdata2)


def get_hw_ver ():

    #"-----------Garnet hw version----------"

    (ret1, rdata1) = read_ee_byte(0x0012 )

    if (ret1 != 0):
        return -1
       
    print "Garnet HW version: %x" % rdata1


def get_cappn ():

    #"-----------Capacitor part number----------"

    for i in range(11):
        (ret1, rdata1) = read_ee_byte(0x0020 )
        (ret2, rdata2) = read_ee_byte(0x0021 )
        (ret3, rdata3) = read_ee_byte(0x0022 )
        (ret4, rdata4) = read_ee_byte(0x0023 )
        (ret5, rdata5) = read_ee_byte(0x0024 )
        (ret6, rdata6) = read_ee_byte(0x0025 )
        (ret7, rdata7) = read_ee_byte(0x0026 )
        (ret8, rdata8) = read_ee_byte(0x0027 )
        (ret9, rdata9) = read_ee_byte(0x0028 )
        (ret10, rdata10) = read_ee_byte(0x0029 )
        (ret11, rdata11) = read_ee_byte(0x002a )
        (ret12, rdata12) = read_ee_byte(0x002b )
     
        if (ret1 != 0 or ret2 != 0 or ret3 != 0 or ret4 != 0 or ret5 != 0 or ret6 != 0 or ret7 != 0 or ret8 != 0 ):
            return -1
       
    print "Capacitor part number: %c%c%c%c%c%c%c%c%c%c%c%c" % (rdata1,rdata2,rdata3,rdata4,rdata5,rdata6,rdata7,rdata8,rdata9,rdata10,rdata11,rdata12)


def get_sn ():

    #"----------- Serial number----------"

    for i in range(7):
        (ret1, rdata1) = read_ee_byte(0x0030 )
        (ret2, rdata2) = read_ee_byte(0x0031 )
        (ret3, rdata3) = read_ee_byte(0x0032 )
        (ret4, rdata4) = read_ee_byte(0x0033 )
        (ret5, rdata5) = read_ee_byte(0x0034 )
        (ret6, rdata6) = read_ee_byte(0x0035 )
        (ret7, rdata7) = read_ee_byte(0x0036 )
        (ret8, rdata8) = read_ee_byte(0x0037 )
        
        if (ret1 != 0 or ret2 != 0 or ret3 != 0 or ret4 != 0 or ret5 != 0 or ret6 != 0 or ret7 != 0 or ret8 != 0 ):
            return -1
       
    print "Serial number:%c%c%c%c%c%c%c%c" % (rdata1,rdata2,rdata3,rdata4,rdata5,rdata6,rdata7,rdata8)


def get_pcbver ():

    #"----------- PCB version----------"

    for i in range(1):
        (ret1, rdata1) = read_ee_byte(0x0040 )
        (ret2, rdata2) = read_ee_byte(0x0041 )
        if (ret1 != 0 or ret2 != 0):
            return -1
       
    print "PCB version: %c%c" % (rdata1,rdata2)


def get_mfdate ():

    #"----------- Manufacture date---------"

    for i in range(3):
        (ret1, rdata1) = read_ee_byte(0x0042 )
        (ret2, rdata2) = read_ee_byte(0x0043 )
        (ret3, rdata3) = read_ee_byte(0x0044 )
        (ret4, rdata4) = read_ee_byte(0x0045 )
    if (ret1 != 0 or ret2 != 0 or ret3 != 0 or ret4 != 0 ):
            return -1
        
    print "Manufacture  date: %c%c%c%c" % (rdata1,rdata2,rdata3,rdata4)


def get_endusr ():

    #"----------- Manufacture name---------"

    for i in range(1):
        (ret1, rdata1) = read_ee_byte(0x0046 )
        (ret2, rdata2) = read_ee_byte(0x0047 )

     
        if (ret1 != 0 or ret2 != 0):
            return -1
           
    print "Manufacture  name: %c%c" % (rdata1,rdata2)

'''
def get_pca ():

    #"----------- PC assembly number---------"

    for i in range(7):
        (ret1, rdata1) = read_ee_byte(0x02ab )
        (ret2, rdata2) = read_ee_byte(0x02ac )
        (ret3, rdata3) = read_ee_byte(0x02ad )
        (ret4, rdata4) = read_ee_byte(0x02ae )
        (ret5, rdata5) = read_ee_byte(0x02af )
        (ret6, rdata6) = read_ee_byte(0x02b0 )
        (ret7, rdata7) = read_ee_byte(0x02b1 )
        (ret8, rdata8) = read_ee_byte(0x02b2 )
     
        if (ret1 != 0 or ret2 != 0 or ret3 != 0 or ret4 != 0 or ret5 != 0 or ret6 != 0 or ret7 != 0 or ret8 != 0 ):
            return -1
       
    print "PCassembly number: %c%c%c%c%c%c%c%c" % (rdata1,rdata2,rdata3,rdata4,rdata5,rdata6,rdata7,rdata8)


def get_cinit ():

    #"----------- initial capacitance---------"

		(ret1, rdata1) = read_ee_byte(0x0050 )
		if (ret1 != 0 ):
				return -1
       
		print "Cinit: %c" % (rdata1)

'''

def allreg():
    count = 1
    print 
    print "#############Read all registers##################"
    for key in allreglist:
        # Cap measurement
        (ret, rdata) = smb_read_reg(allreglist[key])
        print key,":" , rdata,"-",hex(rdata)
        aa_sleep_ms(10)  
    print "#############Read all registers##################"


def r_eepcont ():
	
    get_temp_his()
    get_cap_his()
    get_t_run()
    get_t_lastpf()
    get_pwrcycs()
    get_lastcap()
    get_model ()
    get_fw_ver ()
    get_hw_ver ()
    get_cappn ()
    get_sn ()
    get_pcbver ()
    get_mfdate ()
    get_endusr ()
    allreg()
        
    print "        "

if __name__ == '__main__':
    smb_init()
    
    r_eepcont ()

    smb_exit()