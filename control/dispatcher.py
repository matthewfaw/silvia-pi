from subprocess import call
from datetime import datetime

def dispatch(op, state, body=None):
    if op == "curr_temp":
        return str(state['avgtemp'])
    if op == "get_settemp":
        return str(state['settemp'])
    elif op == "settemp":
        settemp = float(body)
        if settemp >= 200 and settemp <= 260 :
            state['settemp'] = settemp
            return str(settemp)
        else:
            raise Exception('Set temp out of range 200-260.')
    elif op == "is_awake":
        return str(state['is_awake'])
    elif op == "schedule":
        sched = body
        if sched == "True":
            state['sched_enabled'] = True
            return True
        elif sched == "False":
            state['sched_enabled'] = False
            state['is_awake'] = True
            return False
        else:
            raise Exception('Invalid scheduler setting. Expecting True or False')
    elif op == "set_wake":
        wake = body[0]
        weekday_or_weekend = body[1]
        datetime.strptime(wake,'%H:%M')
        state['{}_wake_time'.format(weekday_or_weekend)] = wake
        return str(wake)
    elif op == "set_sleep":
        sleep = body[0]
        weekday_or_weekend = body[1]
        datetime.strptime(sleep,'%H:%M')
        state['{}_sleep_time'.format(weekday_or_weekend)] = sleep
        return str(sleep)
    elif op == "all_stats":
        return dict(state)
    elif op == "restart":
        call(["reboot"])
        return '';
    elif op == "shutdown":
        call(["shutdown","-h","now"])
        return '';
    elif op == "hc":
        return "OK"
    else:
        return ["curr_temp","get_settemp","settemp <200-260>","is_awake","schedule <True/False>","set_wake <HH:MM> <weekday/weekend>","set_sleep <HH:MM> <weekday/weekend>","all_stats","reboot","shutdown", "hc", "list"]
