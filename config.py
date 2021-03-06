#!/usr/bin/python

import logging, os

# Raspberry Pi SPI Port and Device
spi_port = 0
spi_dev = 0

# Pin # for relay connected to heating element
he_pin = 26

# Default goal temperature
#set_temp = 221.
set_temp = 203.
set_temp_tolerance = 2.
cold_state = 100
warm_state = 200

pid_history_length = 10
temp_history_length = 5

startup_sleep_time = 1

# Default sleep/wake times
sched_enabled = True
sched_disabled_op = "wakeup"
#sched_disabled_op = "gotosleep"
weekday_wake_time = '07:30'
weekday_sleep_time = '10:30'
weekend_wake_time = '10:00'
weekend_sleep_time = '12:30'
schedule_sample_time = 1

# Main loop sample rate in seconds
sample_time = 0.5
# Number of seconds until machine changes between hot & cold states.
num_secs_for_state_change = 60*15
num_secs_for_state_constant = 60*1

# Number of times to allow RuntimeError("short circuit to ground")
temp_reading_errors = 100
gpio_errors = 100
server_hc_errors = 100
slack_send_message_retry = 100
slack_send_message_fail_sleep = 1

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

#Slack channel to monitor
#slack_channel_type="public_channel"
slack_channel_type="im"
#slack_channel_name="general"
slack_channel_name="matthewfaw"
slack_sample_time=5

# Logging info
log_level = logging.INFO
log_maxbytes = int(1e7)
#log_level = logging.DEBUG
basedir=os.path.dirname(os.path.realpath(__file__))
log_files = {
        "main": "silvia-pi.log",
        "pid": "pid.log",
        "dummy": "dummy.log",
        "he": "heat_exchange.log",
        "schedule": "scheduler.log",
        "server": "webserver.log",
        "slack": "slack.log",
        "watchdog": "watchdog.log",
        }
