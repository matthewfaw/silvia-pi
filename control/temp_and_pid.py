import sys
from time import sleep, time
from math import isnan
import board, busio, digitalio, adafruit_max31855
import PID as PID
import config as conf
from control.dummy import DummyPID, DummySensor, DummyDigitalIO, DummySPI
from collections import deque
from datetime import datetime as dt


def _c_to_f(c):
    return c * 9.0 / 5.0 + 32.0

def pid_loop(dummy,state, temp_readings_enabled, pid_enabled):

    spi_constructor = busio.SPI if temp_readings_enabled else DummySPI
    cs_constructor = digitalio.DigitalInOut if temp_readings_enabled else DummyDigitalIO
    sensor_constructor = adafruit_max31855.MAX31855 if temp_readings_enabled else DummySensor

    pid_constructor = PID.PID if pid_enabled else DummyPID

    spi = spi_constructor(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = cs_constructor(board.D8)
    sensor = sensor_constructor(spi=spi, cs=cs) 

    pid = pid_constructor(conf.Pc,conf.Ic,conf.Dc)
    pid.SetPoint = state['settemp']
    pid.setSampleTime(conf.sample_time)

    curr_nanct=0
    total_nanct=0
    last_nan_time=-1
    i=0
    j=0
    pidhist = deque([0.]*10)
    avgpid = 0.
    temphist = deque([0.]*5)
    avgtemp = 0.
    lastsettemp = state['settemp']
    iscold = True
    iswarm = False
    lastcold = 0
    lastwarm = 0

    with open('pid.log','a') as fpid:
        try:
            while True: # Loops 10x/second
                # Get the temp
                try:
                    tempc = sensor.temperature
                except RuntimeError as err:
                    curr_nanct += 1
                    total_nanct += 1
                    last_nan_time = dt.now()
                    print("Encountered the following error while reading the temperature for the {}th time in a row:\n{}".format(curr_nanct, err))
                    if curr_nanct > conf.temp_reading_errors:
                        print("Exceeded temp reading error threshold... Exiting")
                        sys.exit("Too many temp reading errors!")
                    else:
                        sleep(conf.sample_time)
                        continue
                else:
                    curr_nanct = 0

                tempf = _c_to_f(tempc)
                temphist.popleft()
                temphist.append(tempf)
                avgtemp = sum(temphist)/len(temphist)

                if avgtemp < 100:
                    lastcold = i

                if avgtemp > 200:
                    lastwarm = i

                if iscold and (i-lastcold)*conf.sample_time > 60*15:
                    pid = pid_constructor(conf.Pw,conf.Iw,conf.Dw)
                    pid.SetPoint = state['settemp']
                    pid.setSampleTime(conf.sample_time)
                    iscold = False

                if iswarm and (i-lastwarm)*conf.sample_time > 60*15: 
                    pid = pid_constructor(conf.Pc,conf.Ic,conf.Dc)
                    pid.SetPoint = state['settemp']
                    pid.setSampleTime(conf.sample_time)
                    iscold = True

                if state['settemp'] != lastsettemp:
                    pid.SetPoint = state['settemp']
                    lastsettemp = state['settemp']

                pid.update(avgtemp)
                pidout = pid.output
                pidhist.popleft()
                pidhist.append(pidout)
                avgpid = sum(pidhist)/len(pidhist)

                state['i'] = i
                state['curr_nanct'] = curr_nanct
                state['total_nanct'] = total_nanct
                state['last_nan_time'] = last_nan_time
                state['tempf'] = round(tempf,2)
                state['avgtemp'] = round(avgtemp,2)
                state['pidval'] = round(pidout,2)
                state['avgpid'] = round(avgpid,2)
                state['pterm'] = round(pid.PTerm,2)
                if iscold:
                    state['iterm'] = round(pid.ITerm * conf.Ic,2)
                    state['dterm'] = round(pid.DTerm * conf.Dc,2)
                else:
                    state['iterm'] = round(pid.ITerm * conf.Iw,2)
                    state['dterm'] = round(pid.DTerm * conf.Dw,2)
                state['iscold'] = iscold

                print(time(), state, file=fpid)

                sleep(conf.sample_time)
                i += 1

        finally:
            pid.clear()
