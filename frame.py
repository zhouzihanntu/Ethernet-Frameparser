#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import binascii

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
    fo = open(filename,"rb+")
    fName = fo.name
    fName = re.sub('\.\S*', '', fName)
    newFile = "output" + fName
    op = open(newFile, "wb+")
    fContent = fo.read()
    fContent = binascii.b2a_hex(fContent)
    # print fContent
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
        print j
        for i in range(0,7):
            header_data += "0xAA"
        header_data += "0xAB"
        for i in range(0,6):
            header_data += des[i]
        for i in range(0, 6):
            header_data += src[i]
        header_data += type[0]
        header_data += type[1]

        if j != (num + 1) and j != 0:
            fd = "write: " + fo.read(743)
            header_data += fd
            # dataCrc = crc8(fd,1500)
            # header_data += dataCrc
            # print dataCrc
        elif j == 0:
            fd = "creat file: " + newFile
            header_data += fd
            # print len(fd)
            # dataCrc = crc8(fd,1500)
            # header_data += dataCrc
            # print dataCrc
        else:
            lastP = fo.tell()
            fd = "lastFrame:" + fo.read(sum-lastP)
            header_data += fd
            # dataCrc = crc8(fd,sum-lastP)
            # header_data += dataCrc
            # print dataCrc
    header_data = binascii.b2a_hex(header_data)
    print header_data[0:100]
    op.write(header_data)
    op.close()
    print "file packed!"
    print newFile + " created!"
    print fName


def Frameunpack(filename):
    fo = open(filename,"rb+")
    sum = fo.tell()
    fo.seek(0)
    fContent = fo.read(7000)
    fContent = binascii.a2b_hex(fContent)
    # fContent = binascii.unhexlify(fContent)
    print fContent
    checkStr = "0xAA0xAA0xAA0xAA0xAA0xAA0xAA0xAB"
    num = fContent.count(checkStr)
    for j in range(0 ,num+1):
        preAmble = ""
        locator = ""
        Des = ""
        Src = ""
        Type = ""
        dataContent = ""
        for i in range(0,7):
            preAmble += (binascii.a2b_hex(fo.read(8))[2:4] + " ")
        locator = binascii.a2b_hex(fo.read(8))[2:4]
        for i in range(0,6):
            Des += (binascii.a2b_hex(fo.read(4)) + " ")
        for i in range(0, 6):
            Src += (binascii.a2b_hex(fo.read(4)) + " ")
        for i in range(0, 2):
            Type += (binascii.a2b_hex(fo.read(4)) + " ")
        if j != (num + 1) and j != 0:
            dataContent = binascii.a2b_hex(fo.read(1500))
        elif j==0 :
            pos = fContent.find("write: ")
            dataContent = binascii.a2b_hex(fo.read((pos - 2)/3 - 2))
        print "序号:", j
        print "前导码:", preAmble
        print "帧前定位符:", locator
        print "目的地址:",Des.replace(" ","-",5)
        print "源地址:", Src.replace(" ","-",5)
        print "类型字段:", Type
        print "数据字段:", dataContent
        # print "CRC校验:", crcData
        print fo.tell()
        print "dddddddddd",num

    print "File parsed"


if __name__ == "__main__" and len(sys.argv) > 2:
    opType = sys.argv[1]
    filename = sys.argv[2]
    if opType == "-e":
        Framepack(filename)
    if opType == "-u":
        Frameunpack(filename)
