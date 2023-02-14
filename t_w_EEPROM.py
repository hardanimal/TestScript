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


def eeprom_exit():
    smb_exit()

def w_eep():
		

		i = 0
		j = 0
		addr = 0
		wdata = 0
		for i in range(146):		
			#write eeprom byte		
			

				for j in range(7):				
					ret = smb_write_reg(EEPROM_REG_ADDRL, addr & 0xFF)
					ret |= smb_write_reg(EEPROM_REG_ADDRH, (addr >> 8) & 0xFF)
					ret |= smb_write_reg(EEPROM_REG_RWDATA, wdata & 0xFF)
			    
					if (ret != 0):
						print "<E>write_ee_byte 1"
					else:
						print"."
					addr +=1		   
	
				wdata +=1
		    
		    #return ret



if __name__ == '__main__':
    smb_init()
    
    w_eep()
        
    
    
    smb_exit()
    