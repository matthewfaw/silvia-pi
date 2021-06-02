from urllib.request import urlopen
import config as conf
from time import sleep
import logging
import sys

def _is_alive(args, p, h, r, s, slack):
    return (not args.with_scheduler or s.is_alive())\
            and (not (args.with_pid or args.with_temp) or p.is_alive())\
            and (not args.with_he or h.is_alive())\
            and (not args.with_server or r.is_alive())\
            and (not args.with_slack or slack.is_alive())

def watch(args, p, h, r, s, slack, pidstate):
    logging.getLogger('watchdog').info("Starting Watchdog...")
    piderr = 0
    weberr = 0
    weberrflag = 0
    urlhc = 'http://localhost:'+str(conf.port)+'/healthcheck'

    lasti = pidstate['i']
    sleep(1)

    while _is_alive(args, p, h, r, s, slack):
        try:
            hc = urlopen(urlhc,timeout=2)
        except:
            weberr += 1
            sleep(1)
        else:
            if hc.getcode() != 200 :
                weberr += 1
                sleep(1)
            else:
                weberr = 0

        if weberr > conf.server_hc_errors and args.with_server:
            logging.getLogger('watchdog').error('ERROR IN WEB SERVER THREAD, exiting')
            break

        weberrflag = 0

        sleep(1)
