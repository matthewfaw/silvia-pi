import time
import sys
import schedule
from datetime import datetime

def _wakeup(dummy,state):
    state['is_awake'] = True

def _gotosleep(dummy,state):
    state['is_awake'] = False

def scheduler(dummy,state):
    with open("scheduler.log", "a") as fsch:
        print("Starting scheduler thread ...", file=fsch)
        last_weekday_wake = 0
        last_weekday_sleep = 0
        last_weekend_wake = 0
        last_weekend_sleep = 0
        last_sched_switch = 0

        while True:
            if last_weekday_wake != state['weekday_wake_time'] or\
                    last_weekday_sleep != state['weekday_sleep_time'] or\
                    last_weekend_wake != state['weekend_wake_time'] or\
                    last_weekend_sleep != state['weekend_sleep_time'] or\
                    last_sched_switch != state['sched_enabled']:
                schedule.clear()

                if state['sched_enabled'] == True:
                    for weekday in ['monday','tuesday','wednesday','thursday','friday']:
                        eval("schedule.every().{}.at(state['weekday_sleep_time']).do(_gotosleep,1,state)".format(weekday))
                        eval("schedule.every().{}.at(state['weekday_wake_time']).do(_wakeup,1,state)".format(weekday))
                    for weekend in ['saturday','sunday']:
                        eval("schedule.every().{}.at(state['weekend_sleep_time']).do(_gotosleep,1,state)".format(weekend))
                        eval("schedule.every().{}.at(state['weekend_wake_time']).do(_wakeup,1,state)".format(weekend))

                    nowtm = float(datetime.now().hour) + float(datetime.now().minute)/60.
                    weekday_or_weekend = "weekday" if datetime.today().weekday() < 5 else "weekend"
                    sleeptm = state['{}_sleep_time'.format(weekday_or_weekend)].split(":")
                    sleeptm = float(sleeptm[0]) + float(sleeptm[1])/60.
                    waketm = state['{}_wake_time'.format(weekday_or_weekend)].split(":")
                    waketm = float(waketm[0]) + float(waketm[1])/60.

                    if waketm < sleeptm:
                        if nowtm >= waketm and nowtm < sleeptm:
                            _wakeup(1,state)
                        else:
                            _gotosleep(1,state)
                    elif waketm > sleeptm:
                        if nowtm < waketm and nowtm >= sleeptm:
                            _gotosleep(1,state)
                        else:
                            _wakeup(1,state)
                else:
                    _wakeup(1,state)

            last_weekday_wake = state['weekday_wake_time']
            last_weekday_sleep = state['weekday_sleep_time']
            last_weekend_wake = state['weekend_wake_time']
            last_weekend_sleep = state['weekend_sleep_time']
            last_sched_switch = state['sched_enabled']

            schedule.run_pending()

            time.sleep(1)
