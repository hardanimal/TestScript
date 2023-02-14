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


def cap_measure():
	
        print"Start endurance test"
        for i in range(10000):   
            ret = smb_write_reg(0x03,0x01)
            if (ret != 0):
                print "[ERR] write error! <%d>" % ret  
        
            aa_sleep_ms(30)
      
if __name__ == '__main__':
    smb_init()
    

    cap_measure()
    
    
    smb_exit()
    
