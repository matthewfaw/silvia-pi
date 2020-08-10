# silvia-pi
A Raspberry Pi modification to the Rancilio Silvia Espresso Machine implementing PID temperature control.

#### Currently Implemented Features:
* Brew temperature control
* RESTful API
* Web interface for displaying temperature and other statistics
* Programmable machine warm-up/wake-up

#### Planned Features:
* Steam temperature control
* Timed shots with pre-infusion
* Digital pressure gauge

#### Dashboard
<img src="https://github.com/brycesub/silvia-pi/blob/master/media/silvia_dashboard.gif" width=800 />

#### Hardware
* Raspberry Pi 2
  * $35 - http://www.amazon.com/Raspberry-Pi-Model-Project-Board/dp/B00T2U7R7I
* Wi-Fi Adapter that works with Raspbian
  * $10 - http://www.amazon.com/Edimax-EW-7811Un-150Mbps-Raspberry-Supports/dp/B003MTTJOY or
* Power Adapter
  * Any Micro USB 5v / 2A supply will do, the longer the cable the better
  * I used an Apple USB block, and a 3ft long micro-usb cable
* Micro SD Card
  * 4GB minimum, 8GB Class 10 recommended
  * $7 - http://www.amazon.com/Samsung-Class-Adapter-MB-MP16DA-AM/dp/B00IVPU7KE
* Solid State Relay - For switching on and off the heating element
  * $10 - https://www.amazon.com/gp/product/B00HV974KC/ref=ppx_yo_dt_b_asin_title_o01_s01?ie=UTF8&psc=1
* Thermocouple Amplifier - For interfacing between the Raspberry Pi and Thermocouple temperature probe
  * $15 - https://www.amazon.com/gp/product/B01MR5EG6L/ref=ppx_yo_dt_b_asin_title_o01_s02?ie=UTF8&psc=1
* Type K Thermocouple - For accurate temperature measurement
  * $15 - https://www.amazon.com/gp/product/B00N2QTHLM/ref=ppx_yo_dt_b_asin_title_o01_s04?ie=UTF8&psc=1
* Ribbon Cable - For connecting everything together
  * $5 - https://www.amazon.com/gp/product/B07GD2BWPY/ref=ppx_yo_dt_b_asin_title_o01_s00?ie=UTF8&th=1
* 14 gauge wire - For connecting the A/C side of the relay to the circuit
  * $5 - https://www.amazon.com/gp/product/B017TFR6SM/ref=ppx_yo_dt_b_asin_title_o01_s06?ie=UTF8&psc=1
    * Don't skimp here.  Remember this wire will be in close proximity to a ~240*F boiler
* Gardner Bender 16-14 AWG 4-6 Stud Spade Terminal, Vinyl Blue (10-Pack)
  * https://www.homedepot.com/p/Gardner-Bender-16-14-AWG-4-6-Stud-Spade-Terminal-Vinyl-Blue-10-Pack-15-113/205846650
    * To connect wire from SSR to b1 and b2
* Mounting screws/nuts
  * M4 for the SSR
    * https://www.homedepot.com/p/Everbilt-M4-0-7-x-14-mm-Phillips-Flat-Head-Stainless-Steel-Machine-Screw-2-Pack-843748/204849533
  * M2.5 for the Raspberry pi
    * https://www.homedepot.com/p/Everbilt-M2-5-0-45-x-25-mm-Phillips-Pan-Head-Stainless-Steel-Machine-Screw-2-Pack-842638/204845996
* Drill + drill bits
  * To make holes for mounting raspberry pi + SSR, and to run power to pi
* Wire stripper + crimper
  * https://www.homedepot.com/p/Klein-Tools-Klein-Kurve-Multi-Tool-Wire-Stripper-Crimper-1019SEN/305303655
* Heat shrink + solder + soldering iron to connect everything
  * Heat shrink
    * https://www.homedepot.com/p/Gardner-Bender-8-Piece-Heat-Shrink-Tubing-Assortment-HST-AST/100166440
  * Solder
    * https://www.amazon.com/gp/product/B072WP4H99/ref=ppx_yo_dt_b_asin_title_o01_s03?ie=UTF8&psc=1
  * Soldering iron
    * https://www.amazon.com/gp/product/B000AS28UC/ref=ppx_yo_dt_b_asin_title_o01_s00?ie=UTF8&psc=1
  * Soldering iron tips
    * https://www.amazon.com/gp/product/B07MH9P37S/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=1


#### Hardware Installation
[Installation Instructions / Pictures](http://imgur.com/a/3WLVt)

#### Circuit Diagram
High-level circuit diagram:

![Circuit Diagram](media/circuit.png?raw=true "Circuit Diagram")

#### Software
* OS - Raspbian Jessie
  * Full - https://downloads.raspberrypi.org/raspbian_latest
  * Lite (for smaller SD Cards) - https://downloads.raspberrypi.org/raspbian_lite_latest

Install Raspbian and configure Wi-Fi, timezone, and ssh access.

#### silvia-pi Software Installation Instructions
Execute on the pi bash shell:
````
sudo git clone https://github.com/brycesub/silvia-pi.git /root/silvia-pi
sudo /root/silvia-pi/setup.sh
sudo reboot
````
This last step will download the necessariy python libraries and install the silvia-pi software in /root/silvia-pi

It also creates an entry in /etc/rc.local to start the software on every boot.

#### API Documentation

##### GET /allstats
Returns JSON of all the following statistics:
* i : Current loop iterator value (increases 10x per second)
* tempf : Temperature in °F
* avgtemp : Average temperature over the last 10 cycles (1 second) in °F
* settemp : Current set (goal) temperature in °F
* iscold : True if the temp was <120°F in the last 15 minutes
* hestat : 0 if heating element is currently off, 1 if heating element is currently on
* pidval : PID output from the last cycle
* avgpid : Average PID output over the last 10 cycles (1 second)
* pterm : PID P Term value (Proportional error)
* iterm : PID I Term value (Integral error)
* dterm : PID D Term value (Derivative error)
* snooze : Current or last snooze time, a string in the format HH:MM (24 hour)
* snoozeon : true if machine is currently snoozing, false if machine is not snoozing

##### GET /curtemp
Returns string of the current temperature in °F

##### GET /settemp
Returns string of the current set (goal) temperature in °F

##### POST /settemp
Expects one input 'settemp' with a value between 200-260.  
Sets the set (goal) temperature in °F
Returns the set temp back or a 400 error if unsuccessful.

##### GET /snooze
Returns string of the current or last snooze time formatted "HH:MM" (24 hour).  
e.g. 13:00 if snoozing until 1:00 PM local time.

##### POST /snooze
Expects one input 'snooze', a string in the format "HH:MM" (24 hour).  
This enables the snooze function, the machine will sleep until the time specified.  
Returns the snooze time set or 400 if passed an invalid input.

##### POST /resetsnooze
Disables/cancels the current snooze functionality.  
Returns true always.

##### GET /restart
Issues a reboot command to the Raspberry Pi.

##### GET /healthcheck
A simple healthcheck to see if the webserver thread is repsonding.  
Returns string 'OK'.
