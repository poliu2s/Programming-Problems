# -*- coding: cp1252 -*-
# Author: Po Liu
# Created: November 15, 2012
# Derived seleton code from the textbook
# "Computer Networking 6th Edition" by Kurose and Ross
# Part of Socket Programming Assignment 5

# Written as an assignment for the course
# EECE 456 - Computer Communications
# at the University of British Columbia


import socket
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8


def checksum(str):
    csum = 0
    countTo = (len(str) / 2) * 2

    
    count = 0
    while count < countTo:
        thisVal = ord(str[count+1]) * 256 + ord(str[count])
        csum = csum + thisVal
        csum = csum & 0xffffffffL
        count = count + 2


    if countTo < len(str):
        csum = csum + ord(str[len(str) - 1])
        csum = csum & 0xffffffffL

        
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout


    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)


        if whatReady[0] == []: # Timeout
            return "Request timed out."


        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)


        #Fill in start
        
        #Fetch the ICMP header from the IP packet
        icmpHeader=recPacket[20:28]
        type1,code,checksum,packetID,sequence=struct.unpack("bbHHh",icmpHeader)
        if packetID==ID:
              bytesInDouble=struct.calcsize("d")
              timeSent=struct.unpack("d",recPacket[28:28+bytesInDouble])[0]
              return timeReceived-timeSent, type1, code

        
        #Fill in end


    timeLeft = timeLeft - howLongInSelect
    if timeLeft <= 0:
        return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)


    myChecksum = 0
    # Make a dummy header with a 0 checksum.
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)


    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        myChecksum = socket.htons(myChecksum) & 0xffff
        #Convert 16-bit integers from host to network byte order.
    else:
        myChecksum = socket.htons(myChecksum)


    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data


    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str
    #Both LISTS and TUPLES consist of a number of objects
    #which can be referenced by their position number within the object


def doOnePing(destAddr, timeout):
    icmp = socket.getprotobyname("icmp")
    #SOCK_RAW is a powerful socket type. For more details see: http://sock-raw.org/papers/sock_raw


    #Fill in start

    #Create Socket here
    mySocket=socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)

    #Fill in end


    myID = os.getpid() & 0xFFFF #Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)


    mySocket.close()
    return delay


def ping(host, timeout=1):
    #timeout=1 means: If one second goes by without a reply from the server,
    #the client assumes that either the client�s ping or the server�s pong is lost
    dest = socket.gethostbyname(host)
    print "Pinging " + dest + " using Python:"
    print ""

    numPingsSucessful = 0
    numPingsFail = 0
    numPingsTotal = 0
    maxDelay = 0
    minDelay = 9999
    runningSum = 0
    avgDelay = 0

    
    
    
    #Send ping requests to a server separated by approximately one second
    while 1 :
        delay, typeNum, codeNum = doOnePing(dest, timeout)

        print "---------------------------"
        numPingsTotal = numPingsTotal + 1
        if ( isinstance(delay, float) and typeNum == 0):
            runningSum = runningSum + delay
            numPingsSucessful = numPingsSucessful + 1
            avgDelay = runningSum / numPingsSucessful

            #Calculate minimum
            if (minDelay > delay):
                minDelay = delay

            #Calculate maximum
            if (maxDelay < delay):
                maxDelay = delay
        elif (typeNum == 3 and codeNum == 0):
            delay = "Destination network unreachable"
        elif (typeNum == 3 and codeNum == 1):
            dleay = "Destination host unreachable"
        else:
            numPingsFail = numPingsFail + 1

        packetLoss = numPingsFail / numPingsTotal

        
        print "Packet Delay: " + str(delay)
        print "Avg Delay: " + str(avgDelay)
        print "Max Delay: " + str(maxDelay)
        print "Min Delay: " + str(minDelay)
        print "Packet loss rate: " + str(packetLoss)
        time.sleep(1)# one second
    return delay


ping("www.ubc.ca")
