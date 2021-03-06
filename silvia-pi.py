from multiprocessing import Process, Manager
from datetime import timedelta
import time
from time import sleep
import config as conf
import argparse
import os
import sys
import logging
import logging.handlers

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
    
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", '%Y-%m-%dT%H:%M:%SZ')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    file_handler = {}
    for key, fname in conf.log_files.items():
        thislogger = logging.getLogger(key)

        handler = logging.handlers.RotatingFileHandler("{}/{}".format(conf.basedir, fname), maxBytes=conf.log_maxbytes, backupCount=5, encoding='utf-8')
        handler.setFormatter(formatter)
        handler.setLevel(conf.log_level)
        file_handler[key] = handler

        thislogger.setLevel(conf.log_level)
        thislogger.addHandler(console_handler)
        thislogger.addHandler(handler)

    logger = logging.getLogger("main")

    logger.info("CLI Args: {}".format(args))

    manager = Manager()
    pidstate = manager.dict()
    pidstate['is_awake'] = False
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
    pidstate['num_he_failures'] = 0
    pidstate['avgpid'] = 0.
    pidstate['curr_nanct'] = 0
    pidstate['total_nanct'] = 0
    pidstate['last_nan_time'] = -1
    pidstate['slack_last_processed_ts'] = "{:.6f}".format(time.time())

    threads = []
    if args.with_scheduler:
        logger.info("Starting Scheduler thread...")
        s = Process(target=scheduler,args=(1,pidstate))
        s.daemon = True
        s.start()
        threads.append(s)
    else:
        s = None

    if args.with_pid or args.with_temp:
        logger.info("Starting PID thread... Temp readings enabled={}, PID enabled={}".format(args.with_temp, args.with_pid))
        p = Process(target=pid_loop,args=(1,pidstate, args.with_temp, args.with_pid))
        p.daemon = True
        p.start()
        threads.append(p)
    else:
        p = None

    if args.with_he:
        logger.info("Starting HE Control thread...")
        h = Process(target=he_control_loop,args=(1,pidstate))
        h.daemon = True
        h.start()
        threads.append(h)
    else:
        h = None

    if args.with_server:
        logger.info("Starting REST Server thread...")
        basedir = os.path.dirname(os.path.realpath(__file__))
        r = Process(target=rest_server,args=(1, pidstate, basedir))
        r.daemon = True
        r.start()
        threads.append(r)
    else:
        r = None

    if args.with_slack:
        logger.info("Starting Slack interaction thread...")
        slack = Process(target=slack_interact,args=(1, pidstate))
        slack.daemon = True
        slack.start()
        threads.append(slack)
    else:
        slack = None

    try:
        watch(args, p, h, r, s, slack, pidstate)
    finally:
        logger.info("Goodbye to all!")
        for thread in threads:
            if thread.is_alive():
                thread.terminate()
