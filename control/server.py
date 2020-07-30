from bottle import route, run, get, post, request, static_file, abort
from subprocess import call
from datetime import datetime
import config as conf

def rest_server(dummy, state, basedir):

    @route('/')
    def docroot():
        return static_file('index.html',wwwdir)

    @route('/<filepath:path>')
    def servfile(filepath):
        return static_file(filepath,wwwdir)

    @route('/curtemp')
    def curtemp():
        return str(state['avgtemp'])

    @get('/settemp')
    def settemp():
        return str(state['settemp'])

    @post('/settemp')
    def post_settemp():
        try:
            settemp = float(request.forms.get('settemp'))
            if settemp >= 200 and settemp <= 260 :
                state['settemp'] = settemp
                return str(settemp)
            else:
                abort(400,'Set temp out of range 200-260.')
        except:
            abort(400,'Invalid number for set temp.')

    @get('/is_awake')
    def get_is_awake():
        return str(state['is_awake'])

    @post('/scheduler')
    def set_sched():
        sched = request.forms.get('scheduler')
        if sched == "True":
            state['sched_enabled'] = True
        elif sched == "False":
            state['sched_enabled'] = False
            state['is_awake'] = True
        else:
            abort(400,'Invalid scheduler setting. Expecting True or False')

    @post('/setwake')
    def set_wake():
        wake = request.forms.get('wake')
        try:
            datetime.strptime(wake,'%H:%M')
        except:
            abort(400,'Invalid time format.')
        state['wake_time'] = wake
        return str(wake)

    @post('/setsleep')
    def set_sleep():
        sleep = request.forms.get('sleep')
        try:
            datetime.strptime(sleep,'%H:%M')
        except:
            abort(400,'Invalid time format.')
        state['sleep_time'] = sleep
        return str(sleep)

    @get('/allstats')
    def allstats():
        return dict(state)

    @route('/restart')
    def restart():
        call(["reboot"])
        return '';

    @route('/shutdown')
    def shutdown():
        call(["shutdown","-h","now"])
        return '';

    @get('/healthcheck')
    def healthcheck():
        return 'OK'

    with open('webserver.log','a') as fweb:
        print("basedir:",basedir,file=fweb)
        wwwdir = basedir+'/www/'
        print("wwwdir:",wwwdir,file=fweb)
        print("running the server now...",file=fweb)
        run(host='0.0.0.0',port=conf.port,server='cheroot')
