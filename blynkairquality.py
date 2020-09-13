#!/usr/bin/env python3

'''
Author: Gabriel Navarro
Date: Sep. 2020

Raspberry Pi program to collect air quality data from Amphenol 
SMUART-04L sensor and send to Blynk app

Pinout:
______________________________________________
____PIN_____|___RASPBERRY PI____|___SENSOR____
    5V      |   2               |   1 and/or 2
    GND     |   6               |   3 and/or 4
    TX      |   8               |   7 (RX)
    RX      |   10              |   9 (TX)
    RESET   |   16 (GPIO-23)    |   5
    SET     |   18 (GPIO-24)    |   10

Blynk virtual pin assignment (for Blynk app):
V0 = PM1
V1 = PM2.5
V2 = PM10
V3 = AQI
V4 = AQI level

Notes:
- Add your Blynk authentication key (blynk_key)
- Set sample rate (sample_rate, default is 5 seconds)
- Review sensor datasheet for more details
- AQI calculation is only an approximation based on PM2.5 count,
  and the relationship between them is nonlinear. Using the raw PM
  counts is a more reliable measure of air quality. The AQI range
  is limited to 0-300.
- This program is meant to be both informative and fun, but should
  not replace medical advice

'''
blynk_key = '<Enter your key here>'

###

import blynklib
import blynktimer
import RPi.GPIO as GPIO
import requests
import serial
import sys
import time


### Pi and sensor setup ###

# Configure GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)

# Configure serial port
ser = serial.Serial(
    port='/dev/serial0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
) 

# Reset sensor on bootup
GPIO.output(23, 0)
time.sleep(5)
GPIO.output(23, 1)

# Take device out of dormancy and enable ask-answer mode
GPIO.output(24, 1)
time.sleep(1)
ser.write(b'\x42\x4D\xE1\x00\x00\x01\x70')
time.sleep(1)


### Functions ###

def check_wifi():
    # Wait until Pi is connected to WiFi
    test_url = 'http://google.com/'
    timeout = 5
    while True:
        try:
            request = requests.get(test_url, timeout=timeout)
            break
        except (requests.ConnectionError, requests.Timeout) as exception:
            pass

def read_data():
    # Read and return raw data from sensor
    ser.reset_input_buffer()
    ser.write(b'\x42\x4D\xE2\x00\x00\x01\x71')
    data = ser.read(32).hex()
    return data

def pm_count(data):
    # Extract PM1, PM2.5, and PM10 counts from data
    pm1 = int(data[8:12],16) 
    pm2_5 = int(data[12:16],16)
    pm10 = int(data[16:20],16) 
    return pm1, pm2_5, pm10

def aqi_calc(pm2_5):
    # AQI between 0-300 is approximated based on data from 
    # https://www.airnow.gov/aqi/aqi-calculator-concentration/
    # The data plotted out can roughly be broken up into 3 sections,
    # PM2.5 0-55: AQI = 6.49*PM2.5^0.778
    # PM2.5 55-150: AQI = 0.518*PM2.5+122
    # PM2.5 150-200: AQI = PM2.5+50
    # See Google Sheet for more:
    # https://docs.google.com/spreadsheets/d/1dsr7HrB9zRNAtoalXpf5PgXJEM3kYduQHnUA87svLsc/edit?usp=sharing
    global alert_flag
    if pm2_5 <= 55:
        aqi = round(6.49*(pm2_5**0.778))
    elif 55 < pm2_5 <= 150:
        aqi = round(0.518*pm2_5+122)
    elif 150 < pm2_5 <= 250:
        aqi = pm2_5+50
    else:
        aqi = 999 # error out
    if aqi <= 50:
        level = 'GOOD'
    elif 50 < aqi <= 100:
        level = 'MODERATE'
    elif 100 < aqi <= 150:
        level = 'UNHEALTHY FOR SOME'
    elif 150 < aqi <= 200:
        level = 'UNHEALTHY'
    elif 200 < aqi <= 300:
        level = 'VERY UNHEALTHY'
    elif 300 < aqi < 999:
        level = 'HAZARDOUS'
    else:
        level = 'SENSOR FAULT'
    if aqi >= (50 + hysteresis) and alert_flag is False:
        notify_msg = (f'The current air quality level is {level}, '
        'consider turning on or increasing the speed of '
        'your air purifier.')
        blynk.notify(notify_msg)
        alert_flag = True
    if aqi <= (50 - hysteresis) and alert_flag is True:
        notify_msg = ('The air quality level has returned '
        f'to {level}, consider turning off or reducing the speed of '
        'your air purifier to reduce energy consumption.')
        blynk.notify(notify_msg)
        alert_flag = False
    return aqi, level

def exit():
    ser.close()
    GPIO.output(23, 0)
    GPIO.output(23, 0)
    print('\nGoodbye!')
    sys.exit()


### Program initialization ###

# Make sure Pi is connected to WiFi
check_wifi()

# Initialize Blynk 
blynk = blynklib.Blynk(blynk_key)
timer = blynktimer.Timer()
alert_flag = False
hysteresis = 10
sample_rate = 5 # choose value > 1

# Create Blynk handler
@timer.register(pin=0, interval=5, run_once=False)
def read_virtual_pin_handler(pin):
    check_wifi()
    data = read_data()
    pm1, pm2_5, pm10 = pm_count(data)
    aqi, level = aqi_calc(pm2_5)
    blynk.virtual_write(0, pm1)
    blynk.virtual_write(1, pm2_5)
    blynk.virtual_write(2, pm10)
    blynk.virtual_write(3, aqi)
    blynk.virtual_write(4, level)
 

### MAIN ###

if __name__ == '__main__':
    time.sleep(1)
    try:
        while True:
            blynk.run()
            timer.run()
    except (KeyboardInterrupt):
        exit()
