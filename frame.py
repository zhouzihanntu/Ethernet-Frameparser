#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import binascii


def crc8(msg):
    msg = bytearray(msg)
    check = 0
    for i in msg:
        check = addToCRC(i, check)
    checkH =  hex(check)
    if len(checkH) == 3:
        checkH = "0x0" + checkH[2]
        # print checkH
    return checkH


def addToCRC(b, crc):
    if b < 0:
        b += 256
    for i in range(8):
        odd = ((b ^ crc) & 1) == 1
        crc >>= 1
        b >>= 1
        if odd:
            crc ^= 0x8C     # this means crc ^= 140
    return crc


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
    for j in range(0,num+2):
        # print j
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
            crcRes = crc8(fd)
            dataCrc = crcRes
            header_data += dataCrc
        elif j == 0:
            fd = "creat file: " + newFile
            header_data += fd
            # print len(fd)
            crcRes = crc8(fd)
            print "len:", len(crcRes)
            dataCrc = crcRes
            header_data += dataCrc
        if j == (num + 1):
            print "kkkkk"
            lastP = fo.tell()
            fd = "lastFrame:" + fo.read(sum-lastP)
            header_data += fd
            crcRes = crc8(fd)
            print "len:",len(crcRes)
            dataCrc = crcRes
            header_data += dataCrc
        print "crcCode :",dataCrc
    header_data = binascii.b2a_hex(header_data)
    op.write(header_data)
    op.close()
    fo.close()
    print "file packed!"
    print newFile + " created!"
    print "共",num+2,"帧"


def Frameunpack(filename):
    fo = open(filename,"rb+")
    fo.seek(0)
    fContent = fo.read()
    newPackage = filename + "parse"
    np = open(newPackage, "wb+")
    writeContent = ""
    fContent = binascii.a2b_hex(fContent)
    # fContent = binascii.unhexlify(fContent)
    checkStr = "0xAA0xAA0xAA0xAA0xAA0xAA0xAA0xAB"
    num = fContent.count(checkStr)
    fArray =  fContent.split('0xAA0xAA0xAA0xAA0xAA0xAA0xAA0xAB',num)
    fo.seek(0)
    crcVerify = "break"
    preAmble = ""
    locator = ""
    Des = ""
    Src = ""
    Type = ""
    for j in range(0, 7):
        preAmble += (binascii.a2b_hex(fo.read(8))[2:4] + " ")
    locator = binascii.a2b_hex(fo.read(8))[2:4]
    for j in range(0, 6):
        Des += (binascii.a2b_hex(fo.read(4)) + " ")
    for j in range(0, 6):
        Src += (binascii.a2b_hex(fo.read(4)) + " ")
    for j in range(0, 2):
        Type += (binascii.a2b_hex(fo.read(4)) + " ")

    for i in range(1,len(fArray)):
    # for i in range(1, 5):
        dataContent = fArray[i]
        dataContent = dataContent.replace("FFFFFFFFFFFF001676B4E4770800","")[:-4]
        writeContent += dataContent
        crcData = fArray[i][-4:]
        # crcData = binascii.b2a_hex(crcD)
        crcCheck = crc8(dataContent)
        if crcData == crcCheck:
            crcVerify = "ACCEPT"
        print "序号:", i
        print "前导码:", preAmble
        print "帧前定位符:", locator
        print "目的地址:",Des.replace(" ","-",5)
        print "源地址:", Src.replace(" ","-",5)
        print "类型字段:", Type
        print "CRC校验:", crcData
        print "数据字段:", dataContent
        print "状态:",crcVerify
        print "  "
    np.write(writeContent)
    np.close()
    fo.close()
    print "帧解析结束,共",len(fArray) - 1,"帧,请查阅文件",newPackage


if __name__ == "__main__" and len(sys.argv) > 2:
    opType = sys.argv[1]
    filename = sys.argv[2]
    if opType == "-e":
        Framepack(filename)
    if opType == "-u":
        Frameunpack(filename)
