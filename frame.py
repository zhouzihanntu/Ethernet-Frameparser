#!/usr/bin/env python

import sys
import os, os.path, platform, struct

def crc8(data,bits=8):
    crc = 0xFFFF
    for op, code in zip(data[0::2], data[1::2]):
        crc = crc ^ int(op + code, 16)
        for bit in range(0, bits):
            if (crc & 0x0001) == 0x0001:
                crc = ((crc >> 1) ^ 0xA001)
            else:
                crc = crc >> 1
    return typecasting(crc)

def typecasting(crc):
    msb = hex(crc >> 8)
    lsb = hex(crc & 0x00FF)
    return lsb + msb

def Framepack(filename):
    # Open a file
    fo = open(filename, "rb+")
    op = open("output"+filename, "wb+")
    fName = fo.name
    fContent = fo.read()
    # fData = fContent.encode('hex')
    sum = fo.tell()
    num = sum / 1500

    if (sum - num * 1500) < 46:
        for i in range(0, 46 - (sum - num * 1500)):
            fo.write(0x0)
    fo.seek(0)
    src = ["00","16","76","B4","E4","77"]
    des = ["FF","FF","FF","FF","FF","FF"]
    type = ["08","00"]

    header_data = ""
    for j in range(0,num+1):
        for i in range(0,7):
            header_data += "0xaa"
        header_data += "0xab"
        for i in range(0,6):
            header_data += des[i]
        for i in range(0, 6):
            header_data += src[i]
        header_data += type[0]
        header_data += type[1]
        if j == 0:
            fd = fName
            header_data += fd
            print len(fd)
            # dataCrc = crc8(fd,1500)
            # header_data += dataCrc
            # print dataCrc
        if j != num :
            fd = fo.read(1500)
            header_data += fd
            # dataCrc = crc8(fd,1500)
            # header_data += dataCrc
            # print dataCrc
        else:
            lastP = fo.tell()
            fd = fo.read(sum-lastP)
            header_data += fd
            # dataCrc = crc8(fd,sum-lastP)
            # header_data += dataCrc
            # print dataCrc
    header_data = header_data.encode('hex')
    print header_data
    op.write(header_data)
    op.close()
    print "file packed!"

def Frameunpack(filename):
    fo = open(filename,"rb+")
    sum = fo.tell()
    fo.seek(0)
    fContent = fo.read()
    checkStr = "0xaa0xaa0xaa0xaa0xaa0xaa0xaa0xab"
    num = fContent.count(checkStr)
    for j in range(0, num):
        seq = j+1
        print "NO:", seq
        fo.seek(0)
    for j in range(0 ,num):
        preAmble = ""
        locator = ""
        Des = ""
        Src = ""
        Type = ""
        dataContent = ""
        for i in range(0,7):
            preAmble += fo.read(4)
        locator = fo.read(4)
        for i in range(0,6):
            Des += (fo.read(2) + " ")
        for i in range(0, 6):
            Src += (fo.read(2) + " ")
        for i in range(0, 2):
            Type += (fo.read(2) + " ")
        if j != num:
            dataContent = fo.read(1500)
        print "Preamble:", preAmble
        print "Locator :",locator
        print "Des:",Des
        print "Src:", Src
        print "Type:", Type
        print "dataContent:", dataContent
    print "File parsed"








if __name__ == "__main__" and len(sys.argv) > 2:
    opType = sys.argv[1]
    filename = sys.argv[2]
    if opType == "-e":
        Framepack(filename)
    if opType == "-u":
        Frameunpack(filename)
