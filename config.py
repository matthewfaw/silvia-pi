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
wake_time = '07:45'
sleep_time = '09:45'

# Main loop sample rate in seconds
sample_time = 0.2

# PID Proportional, Integral, and Derivative values
Pc = 3.4
Ic = 0.3
Dc = 40.0

Pw = 2.9
Iw = 0.03
Dw = 40.0
#Pw = 1.1
#Iw = 0.01
#Dw = 11.0

#Web/REST Server Options
port = 8080
