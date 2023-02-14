from t_all_function_garnet import *

# Read all register's value
allreglist = {"CAPMEAS":0x03,"RESET_SYS":0x04,"RESET_MIN_MAX":0x05,
	            "ES_CHARGE_TIMEOUT0":0x10,"ES_CHARGE_TIMEOUT1":0x11,
	            "MIN_ES_OPERATING_TEMP":0x12,"MAX_ES_OPERATING_TEMP":0x13,
	            "ES_ATTRIBUTES":0x14,"ES_TECH":0x15,"ES_LIFETIME":0x16,
	            "HWREADY":0x20,"GTG":0x21,"GTG_WARN":0x22,"PGEMSTAT":0x23,
	            "ES_TEMP0":0x24,"ES_TEMP1":0x25,"VIN":0x26,"VCAP":0x27,"CHG_TIME":0x28,
	            "POR_V":0x29,"TCHG_V":0x2A}



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
    
    
    
if __name__ == '__main__':
    
    smb_init()
    
    allreg()
    #display_main_menu(eep_menu)
    
    
    
    smb_exit()



