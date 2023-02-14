'''
Created on 2011-5-26

@author: Gabriel
'''


import sys
import struct
import os

BIGENDIAN = 1
LITTLEENDIAN = 2

def binary_read_byte(hFile):
    rdata = 0
    ret = 0
    rchar = hFile.read(1)
    if (rchar == ""):
        ret = -1
    else:
        rdata = struct.unpack("B", rchar)[0]
    return (ret, rdata)




def binary_write_byte(hFile, wdata):
    ret = 0
    struct_data = struct.pack("B", wdata)
    hFile.write(struct_data)
    
    return ret



def binary_write_4byte(hFile, wlong, endian):
    ret = 0
    if (endian == LITTLEENDIAN):
        struct_data = struct.pack("I", wlong)
        hFile.write(struct_data)
    elif (endian == BIGENDIAN):
        struct_data = struct.pack("B", ((wlong >> 24) & 0xFF))
        hFile.write(struct_data)
        struct_data = struct.pack("B", ((wlong >> 16) & 0xFF))
        hFile.write(struct_data)
        struct_data = struct.pack("B", ((wlong >> 8) & 0xFF))
        hFile.write(struct_data)
        struct_data = struct.pack("B", (wlong & 0xFF))
        hFile.write(struct_data)
        
        
        
        
    return ret

def binary_write_2byte(hFile, wint, endian):
    ret = 0
    if (endian == LITTLEENDIAN):
        struct_data = struct.pack("H", wint)
        hFile.write(struct_data)
    elif (endian == BIGENDIAN):
        struct_data = struct.pack("B", ((wint >> 8) & 0xFF))
        hFile.write(struct_data)
        struct_data = struct.pack("B", (wint & 0xFF))
        hFile.write(struct_data)
        
    return ret



def string_compare(x, y):
    '''
    Used by sort() function
    '''
    if x > y:
        return 1
    elif x == y:
        return 0
    else:
        return -1

        

def file_selection(select_string, ext_name, directory):
    '''
    print out file selection menu, 
    according to file ext name (ext_name), directory (directory)
    give prompt information (select_string).
    
    return the full file name (file_string) which user select.
    '''
    file_string = ""
    print "==================="
    print select_string, ":"
    fileList = [os.path.splitext(os.path.normcase(f))[0] for f in os.listdir(directory) \
                if os.path.splitext(f)[1] == ext_name]
    if (len(fileList) == 0):
        return (-1, file_string)
    fileList.sort(string_compare)
    
    i = 0
    for file_item in fileList:
        print i, " --> ", file_item+ext_name
        i = i + 1
    select_item = int(input("please select file:" ))
    if (select_item < 0 or select_item > (i - 1)):
        print "error input!!!"
        return (-2, file_string)

    file_string = fileList[select_item] + ext_name
    print "You selected: [", file_string, "]"
    
    return (0, file_string)

        