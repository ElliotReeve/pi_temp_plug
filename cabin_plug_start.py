#!/usr/bin/python

import re
import glob
from time import sleep
from pyHS100 import SmartPlug
import RPi.GPIO as GPIO
from datetime import datetime
from pytz import timezone

plug_status_file = open("/d1/cabin_plug.txt", "w")
plug_log = open("/d1/cabin_log.txt", "a")
gmt = timezone('GMT')
time_now = datetime.now(gmt)
string_time = time_now.strftime("%d/%m/%y %H:%M:%S")
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
plug = SmartPlug("192.168.1.144")

#set board numbering to BCM
GPIO.setmode(GPIO.BCM)

#setup output pins
GPIO.setup(17,GPIO.OUT)
GPIO.setup(27,GPIO.OUT)

def read_temp_raw():
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines

def read_temp():
	lines = read_temp_raw()
	while lines[0].strip()[-3:] != 'YES':
		sleep(0.2)
		lines = read_temp_raw()
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string) / 1000.0
		return temp_c

temp = read_temp()
if temp < 6:
	plug.turn_on()
	GPIO.output(17,GPIO.HIGH)
	GPIO.output(27,GPIO.HIGH)
	plug_status_file.write("1")
	plug_log.write(string_time+" Plug turned on as temperature is: "+str(temp)+"C\n")
else:
	plug_log.write(string_time+" Cabin at optimum temperature: "+str(temp)+"C\n")

plug_status_file.close()
plug_log.close()
