from subprocess import call
from datetime import datetime
from enum import Enum

class DispatchOptions(Enum):
    CURR_TEMP = r"^curr[a-z]*[\ _]?temp"
    GET_SETTEMP = r"^get[\ _]?set[\ _]?temp"
    SETTEMP = r"^set[\ _]?temp [0-9]{3}"
    IS_AWAKE = r"^is[\ _]?awake"
    SCHEDULE = r"^sched[a-z]* (true|false)"
    SCHED_DISABLED_OP = r"^sched[a-z]*_disabled_op[a-z]* (wakeup|gotosleep)"
    SET_WAKE = r"^set[_]?wake [0-9]{2}:[0-9]{2} (weekday|weekend)"
    SET_SLEEP = r"^set[_]?sleep [0-9]{2}:[0-9]{2} (weekday|weekend)"
    ALLSTATS = r"^all[\ _]?stats"
    REBOOT = r"^(reboot|restart)"
    SHUTDOWN = r"^shut[\ _]?down"
    HC = r"^(hc|healthcheck)"
    NO_OP = r"^.*\(noop\)"
    LIST = r"^(list|.*)"

def dispatch(op, state, body=None):
    if op == DispatchOptions.CURR_TEMP:
        return str(state['avgtemp'])
    if op == DispatchOptions.GET_SETTEMP:
        return str(state['settemp'])
    if op == DispatchOptions.SETTEMP:
        settemp = float(body)
        if settemp >= 200 and settemp <= 260 :
            state['settemp'] = settemp
            return str(settemp)
        else:
            raise Exception('Set temp out of range 200-260.')
    if op == DispatchOptions.IS_AWAKE:
        return str(state['is_awake'])
    if op == DispatchOptions.SCHEDULE:
        sched = body
        if sched.lower() == "true":
            state['sched_enabled'] = True
            return True
        elif sched.lower() == "false":
            state['sched_enabled'] = False
            return False
        else:
            raise Exception('Invalid scheduler setting. Expecting True or False')
    if op == DispatchOptions.SCHED_DISABLED_OP:
        sched_disabled_op = body
        if sched_disabled_op.lower() in ['wakeup', 'gotosleep']:
            state['sched_disabled_op'] = sched_disabled_op
            return sched_disabled_op
        else:
            raise Exception('Invalid disabled op. Expecting either wakeup or gotosleep')
    if op == DispatchOptions.SET_WAKE:
        wake = body[0]
        weekday_or_weekend = body[1]
        datetime.strptime(wake,'%H:%M')
        state['{}_wake_time'.format(weekday_or_weekend.lower())] = wake
        return str(wake)
    if op == DispatchOptions.SET_SLEEP:
        sleep = body[0]
        weekday_or_weekend = body[1]
        datetime.strptime(sleep,'%H:%M')
        state['{}_sleep_time'.format(weekday_or_weekend.lower())] = sleep
        return str(sleep)
    if op == DispatchOptions.ALLSTATS:
        return dict(state)
    if op == DispatchOptions.REBOOT:
        call(["reboot"])
        return '';
    if op == DispatchOptions.SHUTDOWN:
        call(["shutdown","-h","now"])
        return '';
    elif op == DispatchOptions.HC:
        return "OK"
    elif op == DispatchOptions.NO_OP:
        return None
    else:
        return [r"{}: {}".format(op.name, op.value) for op in DispatchOptions]
