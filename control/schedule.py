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

        last_wake = 0
        last_sleep = 0
        last_sched_switch = 0

        while True:
            if last_wake != state['wake_time'] or last_sleep != state['sleep_time'] or last_sched_switch != state['sched_enabled']:
                schedule.clear()

                if state['sched_enabled'] == True:
                    schedule.every().day.at(state['sleep_time']).do(_gotosleep,1,state)
                    schedule.every().day.at(state['wake_time']).do(_wakeup,1,state)

                    nowtm = float(datetime.now().hour) + float(datetime.now().minute)/60.
                    sleeptm = state['sleep_time'].split(":")
                    sleeptm = float(sleeptm[0]) + float(sleeptm[1])/60.
                    waketm = state['wake_time'].split(":")
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

            last_wake = state['wake_time']
            last_sleep = state['sleep_time']
            last_sched_switch = state['sched_enabled']

            schedule.run_pending()

            time.sleep(1)
