from multiprocessing import Process, Manager
from time import sleep
import config as conf
import argparse
import os

from control.schedule import scheduler
from control.temp_and_pid import pid_loop
from control.heat_exchange import he_control_loop
from control.server import rest_server
from control.watchdog import watch

if __name__ == '__main__':
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
    pidstate['weekday_sleep_time'] = conf.weekday_sleep_time
    pidstate['weekday_wake_time'] = conf.weekday_wake_time
    pidstate['weekend_sleep_time'] = conf.weekend_sleep_time
    pidstate['weekend_wake_time'] = conf.weekend_wake_time
    pidstate['i'] = 0
    pidstate['settemp'] = conf.set_temp
    pidstate['avgpid'] = 0.
    pidstate['nanct'] = 0

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
        basedir = os.path.dirname(os.path.realpath(__file__))
        r = Process(target=rest_server,args=(1, pidstate, basedir))
        r.daemon = True
        r.start()
    else:
        r = None

    watch(args, p, h, r, s, pidstate)
