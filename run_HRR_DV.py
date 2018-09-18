
#command line program for operation of 7911 gas analyzer
#including calibration and data logging
import time
import os.path
import smbus
import Adafruit_ADS1x15
from datetime import datetime
import NDIR_class
import SDP8x_class 
print("\n!!!! Welcome to the UoE rPi/Python software !!!!\n")

#initialize i2c ADC
adc = Adafruit_ADS1x15.ADS1115()
GAIN=2/3
DATA_RATE=16
TC_SCALE=0.0001875
TMP=[0]*3

sdp=SDP8x_class.SDP8x()

#program loop
dcon=0
while(1):
   print("\n...please select operation:")
   print("   (C)onnect to NDIR")
   print("   (Z)ero CO/CO2 (span O2)")
   print("   (R)eturn error bytes (diagnostic)")
   print("   (D)isplay current values")
   print("   (L)og data")
   print("   (E)xit")

   UI=raw_input("\n---> ")

   if UI.lower()=="c":
      dcon=1
      ga_dev=NDIR_class.NDIR7911()

   elif UI.lower()=='d':
      if dcon==0:
         print "No NDIR device connected... \n"
      else:
         ga_dev.compdat()
         print 'HC:{0:.3f}, O2:{1:.3f}, CO2:{2:.3f}, CO:{3:.3f},'.format(ga_dev.nHX,
               ga_dev.O2/100.0,ga_dev.CO2/100.0,ga_dev.CO/1000.0)

      for i in range(2,3):
         TI = adc.read_adc(i, gain=GAIN, data_rate=DATA_RATE)
         TMP[i] = 200.92*(TI*TC_SCALE)-6.2974
         print "TC",i+1,": ",TMP[i],"C\n"
      sdp.getDP()
      print sdp.DP

   elif UI.lower()=='r':
      if dcon==0 or ga_dev.conn==0:
         print "\nERROR: No NDIR device connected...\n"
      else:
         ga_dev.errchk()

   elif UI.lower()=='l':
      if dcon==0 or ga_dev.conn==0:
         print "\nWARNING: No NDIR device connected...\n"
      print "\nStarting logging procedure...\n"
      #####main logging loop####

      #open and initialize data output file
      #including header
      tinit=datetime.utcnow()
      foi=0
      foname="./GA_log/"+tinit.strftime("%d_%m_%y")+"_dat_"+str(foi)+".csv"
      while os.path.isfile(foname):
         foi=foi+1
         foname="./GA_log/"+tinit.strftime("%d_%m_%y")+"_dat_"+str(foi)+".csv"
      dat_file=open(foname,"w")
      dat_file.write("7911 bench data aquisition\n")
      dat_file.write(tinit.strftime("%d:%m:%y,%H:%M:%S\n"))
      dat_file.write("date [dd:mm:yy],time (UTC) [hh:mm:ss],record [-],"
         "HC [%],O2 [%],CO2 [%],CO [%],TMP1 [C],TMP2 [C],TMP3 [C],DP [Pa]\n")

      count=1
      tstart=time.time()
      #currently runs for 10 hrs
      while(count<36000):

         while (time.time()-tstart<1):
            time.sleep(0.01)

         #user output
         print("Record: "+str(count))
         #time and record
         tcur=datetime.utcnow()
         dat_file.write(tcur.strftime("%d:%m:%y,%H:%M:%S,"))
         dat_file.write(str(count)+",")
         if dcon==0 or ga_dev.conn==0:
            dat_file.write('NS,NS,NS,NS,')
         else:
            ga_dev.compdat()
            dat_file.write('{0:.3f},{1:.3f},{2:.3f},{3:.3f},'.format(ga_dev.nHX,
               ga_dev.O2/100.0,ga_dev.CO2/100.0,ga_dev.CO/1000.0))
         for i in range(2,3):
            TI = adc.read_adc(i, gain=GAIN, data_rate=DATA_RATE)
            TMP[i] = 200.92*(TI*TC_SCALE)-6.2974
         dat_file.write('{0:.2f},{1:.2f},{2:.2f},'.format(TMP[0],TMP[1],TMP[2]))
         sdp.getDP()
         dat_file.write('{0:.2f},'.format(sdp.DP))
         dat_file.write("\n")
         count=count+1
         tstart=tstart+1

      dat_file.close()

   elif UI.lower()=="z":
      if dcon==0 or ga_dev.conn==0:
         print "\nError: No NDIR device connected...\n"
      else:
         print "\nZeroing..."
         ga_dev.zero()

   elif UI.lower()=="e":
      print "\nExiting...\n"
      exit()
   

   
