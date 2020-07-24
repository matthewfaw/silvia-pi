#!/usr/bin/python

def scheduler(dummy,state):
  import time
  import sys
  import schedule
  from datetime import datetime

  #sys.stdout = open("scheduler.log", "a")
  #sys.stderr = open("scheduler.err.log", "a")

  with open("scheduler.log", "a") as fsch:
    print("Starting scheduler thread ...", file=fsch)

    last_wake = 0
    last_sleep = 0
    last_sched_switch = 0

    while True:

      if last_wake != state['wake_time'] or last_sleep != state['sleep_time'] or last_sched_switch != state['sched_enabled']:
        schedule.clear()

        if state['sched_enabled'] == True:
          schedule.every().day.at(state['sleep_time']).do(gotosleep,1,state)
          schedule.every().day.at(state['wake_time']).do(wakeup,1,state)

          nowtm = float(datetime.now().hour) + float(datetime.now().minute)/60.
          sleeptm = state['sleep_time'].split(":")
          sleeptm = float(sleeptm[0]) + float(sleeptm[1])/60.
          waketm = state['wake_time'].split(":")
          waketm = float(waketm[0]) + float(waketm[1])/60.

          if waketm < sleeptm:
            if nowtm >= waketm and nowtm < sleeptm:
              wakeup(1,state)
            else:
              gotosleep(1,state)
          elif waketm > sleeptm:
            if nowtm < waketm and nowtm >= sleeptm:
              gotosleep(1,state)
            else:
              wakeup(1,state)

        else:
          wakeup(1,state)

      last_wake = state['wake_time']
      last_sleep = state['sleep_time']
      last_sched_switch = state['sched_enabled']

      schedule.run_pending()

      time.sleep(1)

def wakeup(dummy,state):
  state['is_awake'] = True

def gotosleep(dummy,state):
  state['is_awake'] = False

def he_control_loop(dummy,state):
  from time import sleep
  import RPi.GPIO as GPIO
  import config as conf

  GPIO.setmode(GPIO.BCM)
  GPIO.setup(conf.he_pin, GPIO.OUT)
  GPIO.output(conf.he_pin,0)

  heating = False

  try:
    while True:
      avgpid = state['avgpid']

      if state['is_awake'] == False :
        state['heating'] = False
        GPIO.output(conf.he_pin,0)
        sleep(1)
      else:
        if avgpid >= 100 :
          state['heating'] = True
          GPIO.output(conf.he_pin,1)
          sleep(1)
        elif avgpid > 0 and avgpid < 100:
          state['heating'] = True
          GPIO.output(conf.he_pin,1)
          sleep(avgpid/100.)
          GPIO.output(conf.he_pin,0)
          sleep(1-(avgpid/100.))
          state['heating'] = False
        else:
          GPIO.output(conf.he_pin,0)
          state['heating'] = False
          sleep(1)

  finally:
    GPIO.output(conf.he_pin,0)
    GPIO.cleanup()

def pid_loop(dummy,state, temp_readings_enabled, pid_enabled):
  import sys
  from time import sleep, time
  from math import isnan
  import board, busio, digitalio, adafruit_max31855
  import PID as PID
  import config as conf
  from dummy import DummyPID, DummySensor, DummyDigitalIO, DummySPI
  from collections import deque

  #sys.stdout = open("pid.log", "a")
  #sys.stderr = open("pid.err.log", "a")

  def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0

  spi_constructor = busio.SPI if temp_readings_enabled else DummySPI
  cs_constructor = digitalio.DigitalInOut if temp_readings_enabled else DummyDigitalIO
  sensor_constructor = adafruit_max31855.MAX31855 if temp_readings_enabled else DummySensor

  pid_constructor = PID.PID if pid_enabled else DummyPID

  spi = spi_constructor(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
  cs = cs_constructor(board.D8)
  sensor = sensor_constructor(spi=spi, cs=cs) 

  pid = pid_constructor(conf.Pc,conf.Ic,conf.Dc)
  pid.SetPoint = state['settemp']
  pid.setSampleTime(conf.sample_time*5)

  nanct=0
  i=0
  j=0
  pidhist = deque([0.]*10)
  avgpid = 0.
  temphist = deque([0.]*5)
  avgtemp = 0.
  lastsettemp = state['settemp']
  lasttime = time()
  sleeptime = 0
  iscold = True
  iswarm = False
  lastcold = 0
  lastwarm = 0

  with open('pid.log','a') as fpid:
    try:
      while True : # Loops 10x/second
        tempc = sensor.temperature
        if isnan(tempc) :
          nanct += 1
          if nanct > 100000 :
            sys.exit
          continue
        else:
          nanct = 0

        tempf = c_to_f(tempc)
        temphist.popleft()
        temphist.append(tempf)
        avgtemp = sum(temphist)/len(temphist)

        if avgtemp < 100 :
          lastcold = i

        if avgtemp > 200 :
          lastwarm = i

        if iscold and (i-lastcold)*conf.sample_time > 60*15 :
          pid = pid_constructor(conf.Pw,conf.Iw,conf.Dw)
          pid.SetPoint = state['settemp']
          pid.setSampleTime(conf.sample_time*5)
          iscold = False

        if iswarm and (i-lastwarm)*conf.sample_time > 60*15 : 
          pid = pid_constructor(conf.Pc,conf.Ic,conf.Dc)
          pid.SetPoint = state['settemp']
          pid.setSampleTime(conf.sample_time*5)
          iscold = True

        if state['settemp'] != lastsettemp :
          pid.SetPoint = state['settemp']
          lastsettemp = state['settemp']

        if i%10 == 0 :
          pid.update(avgtemp)
          pidout = pid.output
          pidhist.popleft()
          pidhist.append(pidout)
          avgpid = sum(pidhist)/len(pidhist)

        state['i'] = i
        state['tempf'] = round(tempf,2)
        state['avgtemp'] = round(avgtemp,2)
        state['pidval'] = round(pidout,2)
        state['avgpid'] = round(avgpid,2)
        state['pterm'] = round(pid.PTerm,2)
        if iscold :
          state['iterm'] = round(pid.ITerm * conf.Ic,2)
          state['dterm'] = round(pid.DTerm * conf.Dc,2)
        else :
          state['iterm'] = round(pid.ITerm * conf.Iw,2)
          state['dterm'] = round(pid.DTerm * conf.Dw,2)
        state['iscold'] = iscold

        print(time(), state, file=fpid)

        sleeptime = lasttime+conf.sample_time-time()
        if sleeptime < 0 :
          sleeptime = 0
        sleep(sleeptime)
        i += 1
        lasttime = time()

    finally:
      pid.clear()

def rest_server(dummy,state):
  from bottle import route, run, get, post, request, static_file, abort
  from subprocess import call
  from datetime import datetime
  import config as conf
  import os

  @route('/')
  def docroot():
    return static_file('index.html',wwwdir)

  @route('/<filepath:path>')
  def servfile(filepath):
    return static_file(filepath,wwwdir)

  @route('/curtemp')
  def curtemp():
    return str(state['avgtemp'])

  @get('/settemp')
  def settemp():
    return str(state['settemp'])

  @post('/settemp')
  def post_settemp():
    try:
      settemp = float(request.forms.get('settemp'))
      if settemp >= 200 and settemp <= 260 :
        state['settemp'] = settemp
        return str(settemp)
      else:
        abort(400,'Set temp out of range 200-260.')
    except:
      abort(400,'Invalid number for set temp.')

  @get('/is_awake')
  def get_is_awake():
    return str(state['is_awake'])

  @post('/scheduler')
  def set_sched():
    sched = request.forms.get('scheduler')
    if sched == "True":
      state['sched_enabled'] = True
    elif sched == "False":
      state['sched_enabled'] = False
      state['is_awake'] = True
    else:
      abort(400,'Invalid scheduler setting. Expecting True or False')

  @post('/setwake')
  def set_wake():
    wake = request.forms.get('wake')
    try:
      datetime.strptime(wake,'%H:%M')
    except:
      abort(400,'Invalid time format.')
    state['wake_time'] = wake
    return str(wake)

  @post('/setsleep')
  def set_sleep():
    sleep = request.forms.get('sleep')
    try:
      datetime.strptime(sleep,'%H:%M')
    except:
      abort(400,'Invalid time format.')
    state['sleep_time'] = sleep
    return str(sleep)

  @get('/allstats')
  def allstats():
    return dict(state)

  @route('/restart')
  def restart():
    call(["reboot"])
    return '';

  @route('/shutdown')
  def shutdown():
    call(["shutdown","-h","now"])
    return '';

  @get('/healthcheck')
  def healthcheck():
    return 'OK'

  with open('webserver.log','a') as fweb:
    print('derp',file=fweb)
    basedir = os.path.dirname(os.path.realpath(__file__))
    print("basedir:",basedir,file=fweb)
    wwwdir = basedir+'/www/'
    print("wwwdir:",wwwdir,file=fweb)
    print("running the server now...",file=fweb)
    run(host='0.0.0.0',port=conf.port,server='cheroot')

def is_alive(args, p, h, r, s):
  return (not args.with_scheduler or s.is_alive())\
            and (not args.with_pid or p.is_alive())\
            and (not args.with_he or h.is_alive())\
            and (not args.with_server or r.is_alive())

if __name__ == '__main__':
  from multiprocessing import Process, Manager
  from time import sleep
  from urllib.request import urlopen
  import config as conf
  import argparse

  parser = argparse.ArgumentParser(description="Start the server")
  parser.add_argument("--with-scheduler", type=bool, default=True, required=False, help="Indicates whether or not scheduler should be started")
  parser.add_argument("--with-temp", type=bool, default=False, required=False, help="Indicates whether or not temperature reading will be taken from the MAX31855")
  parser.add_argument("--with-pid", type=bool, default=False, required=False, help="Indicates whether or not PID controller should be started")
  parser.add_argument("--with-he", type=bool, default=False, required=False, help="Indicates whether or not HE Controller should be started")
  parser.add_argument("--with-server", type=bool, default=True, required=False, help="Indicates whether or not server should be started")
  args = parser.parse_args()
  print("CLI Args:",args)

  manager = Manager()
  pidstate = manager.dict()
  pidstate['is_awake'] = True
  pidstate['sched_enabled'] = conf.sched_enabled
  pidstate['sleep_time'] = conf.sleep_time
  pidstate['wake_time'] = conf.wake_time
  pidstate['i'] = 0
  pidstate['settemp'] = conf.set_temp
  pidstate['avgpid'] = 0.

  if args.with_scheduler:
    print("Starting Scheduler thread...")
    s = Process(target=scheduler,args=(1,pidstate))
    s.daemon = True
    s.start()
  else:
    s = None

  if args.with_pid or args.with_temp:
    print("Starting PID thread... Temp readings enabled={}, PID enabled={}".format(args.with_temp, args.with_pid))
    p = Process(target=pid_loop,args=(1,pidstate, args.with_temp, args.with_pid))
    p.daemon = True
    p.start()
  else:
    p = None

  if args.with_he:
    print("Starting HE Control thread...")
    h = Process(target=he_control_loop,args=(1,pidstate))
    h.daemon = True
    h.start()
  else:
    h = None

  if args.with_server:
    print("Starting REST Server thread...")
    r = Process(target=rest_server,args=(1,pidstate))
    r.daemon = True
    r.start()
  else:
    r = None

  #Start Watchdog loop
  print("Starting Watchdog...")
  piderr = 0
  weberr = 0
  weberrflag = 0
  urlhc = 'http://localhost:'+str(conf.port)+'/healthcheck'

  lasti = pidstate['i']
  sleep(1)

  while is_alive(args, p, h, r, s):
    curi = pidstate['i']
    if curi == lasti:
      piderr = piderr + 1
    else:
      piderr = 0

    lasti = curi

    if piderr > 9 and args.with_pid:
      print('ERROR IN PID THREAD, RESTARTING')
      p.terminate()

    try:
      hc = urlopen(urlhc,timeout=2)
    except:
      weberrflag = 1
    else:
      if hc.getcode() != 200 :
        weberrflag = 1

    if weberrflag != 0:
      weberr = weberr + 1

    if weberr > 9 and args.with_server:
      print('ERROR IN WEB SERVER THREAD, RESTARTING')
      r.terminate()

    weberrflag = 0

    sleep(1)
