#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import socket
import time

HOST = '127.0.0.1'

PORT = 8800
server_addr = (HOST, PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

a = True
while a:
    outdata = 'heartbeat'
    print('sendto ' + str(server_addr) + ': ' + outdata)
    try:
        s.sendto(outdata.encode(), server_addr)
        print("yes")
    except:
        logging.log("no")

    indata, addr = s.recvfrom(1024)
    print('recvfrom ' + str(addr) + ': ' + indata.decode())
    time.sleep(0.1)

nothing = ""
s.sendto(nothing.encode(), server_addr)
s.close()
