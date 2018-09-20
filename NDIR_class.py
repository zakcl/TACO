import serial
import array
import time
import struct
from sys import getsizeof

####communication parameters####
RESET = [0x02,0x30,0xE3,0xD0]
BENCH_DATA = [0x02,0x3D,0xE3,0xDD]
COMPENSATED_DATA = [0x02,0x31,0xE3,0xD1]
ZERO = [0x02,0x35,0xE3,0xD5]
Span_Bench = [0x02,0x36,0x81,0x80,0x90,0x90,0x90,0x90,0x90,0x90,0x90,0x90,0x90,0x90,0x90,0x90,0x90,0x90,
   0x94,0x9B,0x90,0x90,0x90,0x90,0xE3,0xD6]
SERVICE_ERR = [0x02,0x3E,0xE3,0xDE]
NIB_MASK=15
WORD_PREFIX=144
CO2Conc=8.5
COConc=0.8
hexaneConc=0
propaneConc=0
NOxConc=0
#################################

class NDIR7911(object):

   #establish serial connection
   def __init__(self):
      self.conn=0
      print "\nConnecting to device..."
      self.scon=serial.Serial(port="/dev/ttyUSB0",
         baudrate=9600,
         stopbits=1,
         bytesize=8,
         parity='N',
         timeout=0.4)
      self.scon.write(bytearray(RESET))
      time.sleep(1)
      self.scon.flushInput()
#      self.scon.write(bytearray([0x02,0x4C,0x80,0x80,0x80,0x80,0xE4,0xDC]))
#      time.sleep(1)
#      self.scon.flushInput()
      self.scon.write(bytearray(BENCH_DATA))
      time.sleep(1)
      rbuff=self.scon.readall()
      self.scon.flushInput()
      if len(rbuff)>40:
         print "Connected to S/N: ",rbuff[4:11],"\n"
         self.conn=1
      else :
         print "Unable to connect to device\n"
         self.conn=0

   def errchk(self):
      #aquire and check service error bits
      self.scon.write(bytearray(SERVICE_ERR))
      time.sleep(.5)
      rbuff=self.scon.readall()
      nibble1=ord(rbuff[2])&NIB_MASK
      nibble2=ord(rbuff[3])&NIB_MASK
      print 'byte 0:'
      print format((nibble1<<4)|nibble2,'#010b')
      nibble1=ord(rbuff[4])&NIB_MASK
      nibble2=ord(rbuff[5])&NIB_MASK
      print 'byte 1:'
      print format((nibble1<<4)|nibble2,'#010b')
      nibble1=ord(rbuff[6])&NIB_MASK
      nibble2=ord(rbuff[7])&NIB_MASK
      print 'byte 2:'
      print format((nibble1<<4)|nibble2,'#010b')
      nibble1=ord(rbuff[8])&NIB_MASK
      nibble2=ord(rbuff[9])&NIB_MASK
      print 'byte 3:'
      print format((nibble1<<4)|nibble2,'#010b')
      nibble1=ord(rbuff[10])&NIB_MASK
      nibble2=ord(rbuff[11])&NIB_MASK
      print 'status:'
      print format((nibble1<<4)|nibble2,'#010b')
      self.scon.flushInput()


   #aquire compensated data from the device
   def compdat(self):
      if self.conn==0:
         return
      #send/recieve
      self.scon.write(bytearray(COMPENSATED_DATA))
      time.sleep(.2)
      rbuff=self.scon.readall()
      #parse input
      nibble1=ord(rbuff[2])&NIB_MASK
      nibble2=ord(rbuff[3])&NIB_MASK
      nibble3=ord(rbuff[4])&NIB_MASK
      nibble4=ord(rbuff[5])&NIB_MASK
      val=((nibble1<<12)|(nibble2<<8)|(nibble3<<4)|(nibble4))
      self.nHX=val

      nibble1=ord(rbuff[10])&NIB_MASK
      nibble2=ord(rbuff[11])&NIB_MASK
      nibble3=ord(rbuff[12])&NIB_MASK
      nibble4=ord(rbuff[13])&NIB_MASK
      val=((nibble1<<12)|(nibble2<<8)|(nibble3<<4)|(nibble4))
      self.CO2=val

      nibble1=ord(rbuff[14])&NIB_MASK
      nibble2=ord(rbuff[15])&NIB_MASK
      nibble3=ord(rbuff[16])&NIB_MASK
      nibble4=ord(rbuff[17])&NIB_MASK
      val=((nibble1<<12)|(nibble2<<8)|(nibble3<<4)|(nibble4))
      self.CO=val

      nibble1=ord(rbuff[18])&NIB_MASK
      nibble2=ord(rbuff[19])&NIB_MASK
      nibble3=ord(rbuff[20])&NIB_MASK
      nibble4=ord(rbuff[21])&NIB_MASK
      val=((nibble1<<12)|(nibble2<<8)|(nibble3<<4)|(nibble4))
      self.O2=val

      self.scon.flushInput()

   #zero CO/CO2 using room air, spans O2
   def zero(self):
      if self.conn==0:
         return
      #send/recieve
      self.scon.write(bytearray(ZERO))
      time.sleep(5)
      rbuff=self.scon.readall()
      time.sleep(5)
      self.scon.flushInput()

    #span CO/CO2 using room air, spans O2
    def span(self):
       if self.conn==0:
          return
       #send/recieve
       self.scon.write(bytearray(Span_Bench)
       time.sleep(5)
       rbuff=self.scon.readall()
       time.sleep(5)
       self.scon.flushInput()
