from multiprocessing import Process, Manager
from datetime import timedelta
import time
from time import sleep
import config as conf
import argparse
import os

from control.schedule import scheduler
from control.temp_and_pid import pid_loop
from control.heat_exchange import he_control_loop
from control.server import rest_server
from control.slack import slack_interact
from control.watchdog import watch

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Start the server")
    parser.add_argument("--with-scheduler", type=bool, default=True, required=False, help="Indicates whether or not scheduler should be started")
    parser.add_argument("--with-temp", type=bool, default=True, required=False, help="Indicates whether or not temperature reading will be taken from the MAX31855")
    parser.add_argument("--with-pid", type=bool, default=True, required=False, help="Indicates whether or not PID controller should be started")
    parser.add_argument("--with-he", type=bool, default=True, required=False, help="Indicates whether or not HE Controller should be started")
    parser.add_argument("--with-server", type=bool, default=True, required=False, help="Indicates whether or not server should be started")
    parser.add_argument("--with-slack", type=bool, default=True, required=False, help="Indicates whether or not slack integration should be started")
    args = parser.parse_args()
    print("CLI Args:",args)

    manager = Manager()
    pidstate = manager.dict()
    pidstate['is_awake'] = True
    pidstate['awake_time'] = -1
    pidstate['time_since_awake'] = str(timedelta(0))
    pidstate['sched_enabled'] = conf.sched_enabled
    pidstate['sched_disabled_op'] = conf.sched_disabled_op
    pidstate['weekday_sleep_time'] = conf.weekday_sleep_time
    pidstate['weekday_wake_time'] = conf.weekday_wake_time
    pidstate['weekend_sleep_time'] = conf.weekend_sleep_time
    pidstate['weekend_wake_time'] = conf.weekend_wake_time
    pidstate['i'] = 0
    pidstate['time_outside_target_temp'] = str(timedelta(0))
    pidstate['settemp'] = conf.set_temp
    pidstate['avgpid'] = 0.
    pidstate['curr_nanct'] = 0
    pidstate['total_nanct'] = 0
    pidstate['last_nan_time'] = -1
    pidstate['slack_last_processed_ts'] = "{:.6f}".format(time.time())

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

    if args.with_slack:
        print("Starting Slack interaction thread...")
        slack = Process(target=slack_interact,args=(1, pidstate))
        slack.daemon = True
        slack.start()
    else:
        slack = None

    watch(args, p, h, r, s, slack, pidstate)
