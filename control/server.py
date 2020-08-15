from bottle import route, run, get, post, request, static_file, abort
import config as conf
from control.dispatcher import dispatch

def rest_server(dummy, state, basedir):

    @route('/')
    def docroot():
        return static_file('index.html',wwwdir)

    @route('/<filepath:path>')
    def servfile(filepath):
        return static_file(filepath,wwwdir)

    @route('/curtemp')
    def curtemp():
        return dispatch(op="curr_temp", state=state)

    @get('/settemp')
    def settemp():
        return dispatch(op="get_settemp", state=state)

    @post('/settemp')
    def post_settemp():
        try:
            return dispatch(op="settemp", state=state, body=float(request.forms.get('settemp')))
        except:
            abort(400,'Invalid number for set temp.')

    @get('/is_awake')
    def get_is_awake():
        return dispatch(op="is_awake", state=state)

    @post('/scheduler')
    def set_sched():
        try:
            sched = request.forms.get('scheduler')
            dispatch(op="schedule", state=state, body=sched)
        except:
            abort(400,'Invalid scheduler setting. Expecting True or False')

    @post('/setwake')
    def set_wake():
        wake = request.forms.get('wake')
        weekday_or_weekend = "weekday" if request.forms.get('weekday') == "True" else "weekend"
        try:
            return dispatch(op="set_wake", state=state, body=[wake, weekday_or_weekend])
        except:
            abort(400,'Invalid time format.')

    @post('/setsleep')
    def set_sleep():
        sleep = request.forms.get('sleep')
        weekday_or_weekend = "weekday" if request.forms.get('weekday') == "True" else "weekend"
        try:
            return dispatch(op="set_sleep", state=state, body=[sleep, weekday_or_weekend])
        except:
            abort(400,'Invalid time format.')

    @get('/allstats')
    def allstats():
        return dispatch(op="all_stats", state=state)

    @route('/restart')
    def restart():
        return dispatch(op="restart", state=state)

    @route('/shutdown')
    def shutdown():
        return dispatch(op="shutdown", state=state)

    @get('/healthcheck')
    def healthcheck():
        return dispatch(op="hc", state=state)

    with open('webserver.log','a') as fweb:
        print("basedir:",basedir,file=fweb)
        wwwdir = basedir+'/www/'
        print("wwwdir:",wwwdir,file=fweb)
        print("running the server now...",file=fweb)
        run(host='0.0.0.0',port=conf.port,server='cheroot')
