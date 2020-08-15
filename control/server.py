from bottle import route, run, get, post, request, static_file, abort
import config as conf
from control.dispatcher import dispatch, DispatchOptions

def rest_server(dummy, state, basedir):

    @route('/')
    def docroot():
        return static_file('index.html',wwwdir)

    @route('/<filepath:path>')
    def servfile(filepath):
        return static_file(filepath,wwwdir)

    @route('/curtemp')
    def curtemp():
        return dispatch(op=DispatchOptions.CURR_TEMP, state=state)

    @get('/settemp')
    def settemp():
        return dispatch(op=DispatchOptions.GET_SETTEMP, state=state)

    @post('/settemp')
    def post_settemp():
        try:
            return dispatch(op=DispatchOptions.SETTEMP, state=state, body=float(request.forms.get('settemp')))
        except:
            abort(400,'Invalid number for set temp.')

    @get('/is_awake')
    def get_is_awake():
        return dispatch(op=DispatchOptions.IS_AWAKE, state=state)

    @post('/scheduler')
    def set_sched():
        try:
            sched = request.forms.get('scheduler')
            dispatch(op=DispatchOptions.SCHEDULE, state=state, body=sched)
        except:
            abort(400,'Invalid scheduler setting. Expecting True or False')

    @post('/sched_disabled_op')
    def set_sched_disabled_op():
        try:
            sched_disabled_op = request.forms.get('op')
            dispatch(op=DispatchOptions.SCHED_DISABLED_OP, state=state, body=sched_disabled_op)
        except:
            abort(400,'Invalid sched_disabled_op setting. Expecting wakeup or gotosleep')

    @post('/setwake')
    def set_wake():
        wake = request.forms.get('wake')
        weekday_or_weekend = "weekday" if request.forms.get('weekday') == "True" else "weekend"
        try:
            return dispatch(op=DispatchOptions.SET_WAKE, state=state, body=[wake, weekday_or_weekend])
        except:
            abort(400,'Invalid time format.')

    @post('/setsleep')
    def set_sleep():
        sleep = request.forms.get('sleep')
        weekday_or_weekend = "weekday" if request.forms.get('weekday') == "True" else "weekend"
        try:
            return dispatch(op=DispatchOptions.SET_SLEEP, state=state, body=[sleep, weekday_or_weekend])
        except:
            abort(400,'Invalid time format.')

    @get('/allstats')
    def allstats():
        return dispatch(op=DispatchOptions.ALLSTATS, state=state)

    @route('/restart')
    def restart():
        return dispatch(op=DispatchOptions.REBOOT, state=state)

    @route('/shutdown')
    def shutdown():
        return dispatch(op=DispatchOptions.SHUTDOWN, state=state)

    @get('/healthcheck')
    def healthcheck():
        return dispatch(op=DispatchOptions.HC, state=state)

    with open('webserver.log','a') as fweb:
        print("basedir:",basedir,file=fweb)
        wwwdir = basedir+'/www/'
        print("wwwdir:",wwwdir,file=fweb)
        print("running the server now...",file=fweb)
        run(host='0.0.0.0',port=conf.port,server='cheroot')
