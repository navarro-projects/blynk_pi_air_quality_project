Created by: Gabriel Navarro

# Blynk x Raspberry Pi - Air Quality Project
This guide is for creating a low-cost air quality measurement device based on a Raspberry Pi and paired with a Blynk smartphone app. I put together this homemade project during a smokey weekend in California, and I've attempted to create a simple guide here so others can reproduce it. You will learn how to how to prepare all the hardware, set up the Raspberry Pi, and build your own free Blynk app. Enjoy!

## Project Overview
The Raspberry Pi is connected to the air quality sensor (see model below), which provides realtime measurements of air quality as raw quantities of PM1, PM2.5, and PM10 in ug/m3. The AQI score is calculated from the PM2.5 value, and all the data is sent to the Blynk app on your smartphone. 

## Necessary Hardware and Software
- WiFi access at home
- Blynk app installed on smartphone, with free account 
- Raspberry Pi with WiFi (compatible with Pi Zero W, 3, or 4)
- SD Card formatted for use on a Pi (see these instructions: https://www.raspberrypi.org/downloads/noobs/)
- Laptop / computer with SD card input
- Raspberry Pi 5V power supply
- Amphenol SMUART-04L air quality sensor (https://www.digikey.com/short/zfvftt)
- header for sensor wiring (https://www.digikey.com/short/zfvft5)
- 6 wires (preferably different colors; these make it easy to connect to the Pi's pins: https://www.digikey.com/short/zfvfpj)
- soldering iron and solder
- Optional: heat-shrink tubing and single row header for easy connection to the Pi (https://www.digikey.com/short/z2t225)

## Instructions

### Sensor wiring setup
Overview: 
The wires are soldered to the header which plugs into the back of the sensor. The other end of the wires plug into the pins on the Pi. This connection provides power from the Pi to the sensor and enables communication between the two devices. Additionally, there are wired connections to reset the device and set it into operating mode. Note: sensor RX connects to Pi TX, and vice versa. Do not connect sensor TX to Pi TX, or RX to RX.

1. Solder the 6 wires onto the header according to the pinout below. The pin numbers for the header are defined in the datasheet of the sensor on DigiKey, in the link given above. Be sure to note the orientation of the pins on the header - plugging the header in backwards may damage the devices.

Header Pin #  | Pin Description | Corresponding Pin # on Pi
- 1 and/or 2    | 5V              | 2                       
- 3 and/or 4    | GND             | 6                       
- 7             | Sensor RX       | 8 (Pi TX)               
- 9             | Sensor TX       | 10 (Pi RX)              
- 5             | Reset           | 16 (GPIO-23)            
- 10            | Set             | 18 (GPIO-24)            

2. (Optional) Twist the wires to form a singular cable and seal each end with heat-shrink tubing for a nice, contained finish. If using heat-shrink tubing, be sure to leave enough slack at the free end to connect all the wires to the pins on the Pi. I soldered all my wire ends to the single row header above to make it easier to connect the cable to the Pi.

3. Connect the wires to both the sensor and the Pi, being careful that all pins are matching the positions defined here. The pin numbers for the Pi can be found here https://www.raspberrypi.org/documentation/usage/gpio/. 

4. If you've done everything correctly, you can briefly turn on the Pi and confirm that the fan on the sensor spins. Turn off the Pi and remove the SD card if it's inserted.

### Downloading Blynk
Overview:
Blynk provides a free platform for IoT app development, allowing you to connect your phone to various devices like the Raspberry Pi. Download the app on your phone from the App Store or Google Play store and create a free account.

1. In the Blynk app, create a new project and name it whatever you want.

2. Select the model of the Raspberry Pi you have for your device. For the newest Pi models, using Raspberry Pi 3B will be sufficient.

3. Set Connection Type to WiFi.

4. Select if you want a Light or Dark theme. You can change this later.

5. When the project is created, an authentication key will be emailed to you. You will need to insert this later into the code of the main program.

### Pi setup
Overview:
In this section, the Pi will be configured to be used for this project. All necessary software will be installed and the Pi will be connected to your home WiFi. Raspberrypi.org has great documentation which will be leveraged a lot here. These steps are a bit tedious the first time around, but going through them will teach you how to set up a Pi for other DIY projects.

1. Follow the instructions above to prepare the SD card. I recommend that first-time users try the Raspberry Pi Imager, which is described in the link provided. When finished, leave the SD card in your computer.

2. To configure the Pi to connect to your home WiFi, you need to create a file on your computer called "wpa_supplicant.conf" and add your WiFi name and password. This file needs to be placed in the root folder on the SD card, where all the software was loaded in the previous step. Instructions for this can be found here: https://www.raspberrypi.org/documentation/configuration/wireless/headless.md. Be sure to add your ISO 3166-1 country code ("country=US" for United States), and your WiFi name ("SSID") and password ("psk") in the appropriate fields, and retain the exact formatting given in these instructions. 

3. With your computer, you can connect to and transfer files to and from the Pi with SSH. To enable SSH on the Pi, create a blank file named "ssh" and place it in the same boot directory of the SD card referenced above. That's it. See section 3 at this link for details: https://www.raspberrypi.org/documentation/remote-access/ssh/README.md

4. Now it's time to check if the Pi can connect to the internet. Safely remove the SD card from your computer, insert it into the Pi, and power it up. If everything up to this point was done correctly, after a minute or two the Pi should have booted up and be connected to your WiFi. In a terminal window (or command window on Windows), type "ping raspberrypi.local" and press enter. If the Pi is online, the terminal should print out responses from the Pi with the reply time. If it's not online, power down the Pi, remove the SD card, and try step 2 again.

5. Now you will SSH into your Pi. On a Mac or Linux machine, open the terminal window and type "ssh pi@raspberrypi.local" to connect to it. For Windows instructions, see here: https://www.raspberrypi.org/documentation/remote-access/ssh/windows10.md. The default username is "pi" and the default password is "raspberry". Enter the password, and you will be connected remotely to the Pi.

6. The default directory when you login to the Pi is "/home/pi". Create a new directory at this location with "mkdir Projects", and type "cd Projects" to move to that location ("/home/pi/Projects"). You can name the directory anything you like.

7. The project files will be downloaded in the Projects directory using Git. First install Git on the Pi with "sudo apt-get install git" and allow it to run. Next, grab the URL of the main page of my repository, which can be found by clicking on the "Clone or Download" button. To clone the repo to the Pi, which will install the main program, type "git clone https://github.com/navarro-projects/blynk_pi_air_quality_project.git". This will create a new directory with Projects called "blynk_pi_air_quality_project" containing the main program file.

8. The Blynk Python library also needs to be installed on the Pi. In the terminal, enter "sudo pip3 install blynklib".

9. You need to add your Blynk authentication key to the Python program so the app can connect to your Pi. To do this, type "nano blynk_pi_air_quality_project/blynkairquality.py" to open the file editor, scroll down to the variable "blynk_key", and enter your key in single quotes. Press Ctrl-X to close and save the file.

10. The Pi can be configured so that the program runs automatically after bootup. This is preferred so you don't need to manually start the program any time the Pi is power cycled. To do this, you need to modify a file on the Pi called "rc.local". In the terminal, enter "sudo nano /etc/rc.local", and scroll to the bottom of the file. On the line before "exit 0", add the line "python3 /home/pi/Projects/blynk_pi_air_quality_project/blynkairquality.py &". Make sure that this path matches the location of the program in your Pi, in case you renamed any directories. Save and close the file.

11. The Pi uses its TX and RX pins to talk to the sensor. To enable this serial interface (since it's disabled by default), type "sudo raspi-config" and press enter. Navigate to option 5 "Interfacing Options" and then P6 "Serial". Select "No" for "Would you like a login shell to be accessible over serial?" and "Yes" for "Would you like the serial port hardware to be enabled?". Select "Ok", then "Finish". Don't reboot the Pi, just exit and power it off. 

### Blynk app setup
Overview:
The hard part is over! Now the real fun begins with configuring your app to however you like. The Python program on the Pi will spit out 5 values about your air quality (PM1 count, PM2.5 count, PM10 count, AQI score, and AQI level) every 5 seconds by default. You can edit the variable "sample_rate" in the code to increase this duration if you'd like. The 5 values are returned in the above order to "virtual pins" V0 - V4, respectively, which the app reads and can display. 

1. Blynk's website has lots of great information and tutorials to get you started (see: https://blynk.io/en/getting-started), but it's pretty easy to figure out. Basically, you select whatever "widgets" you want on your app screen, name each one, and set it to read a virtual pin. You can play around with color schemes, text sizes, labels, and max/min values. Be sure to set the Reading Rate of each widget to "PUSH" so it receives data from the program on the Pi. If you exceed to free budget for widgets but want to add more features, you have the option to buy more credits.

For example: I prefer using 4 guages for the PM counts and the AQI score, printing the level reading at the top, and using a graph to plot all 4 (see sample photo). For the guages, I use the following ranges: 0-150 for AQI, 0-50 for PM1, 0-60 for PM2.5, and 0-250 for PM10 (I chose these max values because air with concentrations beyond these limits receive an unhealthy rating from the EPA - except for PM1 for which there currently is no limit established). I set labels for the PM counts to "/pin/ug/m3" to show the units, and set the text size to medium. For the text color, I use the gradiant which ascends from green to red.

2. (Optional) If you want to receive notification on your phone, add the Notifications widget to your app. I set my app to let me know if my Pi goes offline after 30 seconds, and I set the priority to High. With these settings, the program will update you depending on whether the current AQI score is Good or not inside your home. If the Pi does loose its WiFi connection temporarily, the program will keep trying to reconnect, upon which time it will resume sending data to the app. The data from the interim period will be lost, however. 

3. Once you're done building your app, click the Play button and turn on your Pi. When the Pi connects to your WiFi, it will start sending data to the app which you can view in real time. You can leave the app in play mode, and open and close it like any other app on your phone. The data sent from your Pi will be stored on a Blynk server until your app is opened again.

### The finish line
That's it! Have fun tweaking your app to suit your needs, and feel free to adjust anything in the code to make it work better for you. I hope this process was fun and empowers you by giving you insight about the quality of the air you breath every day!

## Support
If you appreciate my work and would like to donate me a tip, feel free to use the PayPal button. Thanks!
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=BYB2U76KLDSJ4&currency_code=USD&source=url)
