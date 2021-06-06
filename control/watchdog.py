from urllib.request import urlopen
import config as conf
from time import sleep
import logging
import sys

def _is_alive(args, p, h, r, s, slack):
    sched_is_alive = (not args.with_scheduler or s.is_alive())
    pid_is_alive = (not (args.with_pid or args.with_temp) or p.is_alive())
    he_is_alive = (not args.with_he or h.is_alive())
    server_is_alive = (not args.with_server or r.is_alive())
    slack_is_alive = (not args.with_slack or slack.is_alive())
    if sched_is_alive and pid_is_alive and he_is_alive and server_is_alive and slack_is_alive:
        return True
    else:
        logging.getLogger('watchdog').error('Determined that sched_alive={}, pid_alive={}, he_alive={}, server_alive={}, slack_alive={}.'.format(sched_is_alive,
            pid_is_alive,
            he_is_alive,
            server_is_alive, 
            slack_is_alive))
        return False

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
            logging.getLogger('watchdog').warn('ERROR No={} IN WEB SERVER THREAD, Retrying...'.format(weberr))
            sleep(1)
        else:
            if hc.getcode() != 200 :
                weberr += 1
                logging.getLogger('watchdog').warn('ERROR No={} IN WEB SERVER THREAD because response is not 200, Retrying...'.format(weberr))
                sleep(1)
            else:
                weberr = 0

        if weberr > conf.server_hc_errors and args.with_server:
            logging.getLogger('watchdog').error('Encountered {} >= {} hc errors, exiting'.format(weberr, conf.server_hc_errors))
            break

        weberrflag = 0

        sleep(1)
    logging.getLogger('watchdog').error('A thread is no longer alive. Cannot continue. Goodbye!')
