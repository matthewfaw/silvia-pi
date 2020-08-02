#!/usr/bin/python

# Raspberry Pi SPI Port and Device
spi_port = 0
spi_dev = 0

# Pin # for relay connected to heating element
he_pin = 26

# Default goal temperature
set_temp = 221.

# Default sleep/wake times
sched_enabled = True
weekday_wake_time = '07:45'
weekday_sleep_time = '09:45'
weekend_wake_time = '10:00'
weekend_sleep_time = '12:30'

# Main loop sample rate in seconds
sample_time = 0.5

# PID Proportional, Integral, and Derivative values
Pc = 3.4
Ic = 0.3
Dc = 40.0
#Pc = 8
#Ic = 0.2
#Dc = 60

Pw = 2.9
Iw = 0.3
Dw = 40.0
#Pw = 8
#Iw = 0.2
#Dw = 60

#Web/REST Server Options
port = 8080
