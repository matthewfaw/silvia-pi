from urllib.request import urlopen
import config as conf

def _is_alive(args, p, h, r, s):
    return (not args.with_scheduler or s.is_alive())\
            and (not args.with_pid or p.is_alive())\
            and (not args.with_he or h.is_alive())\
            and (not args.with_server or r.is_alive())

def watch(pidstate):
    print("Starting Watchdog...")
    piderr = 0
    weberr = 0
    weberrflag = 0
    urlhc = 'http://localhost:'+str(conf.port)+'/healthcheck'

    lasti = pidstate['i']
    sleep(1)

    while _is_alive(args, p, h, r, s):
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
