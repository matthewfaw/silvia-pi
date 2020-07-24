from time import sleep
import RPi.GPIO as GPIO
import config as conf

def he_control_loop(dummy,state):

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(conf.he_pin, GPIO.OUT)
    GPIO.output(conf.he_pin,0)

    heating = False

    try:
        while True:
            avgpid = state['avgpid']

            if state['is_awake'] == False :
                state['heating'] = False
                GPIO.output(conf.he_pin,0)
                sleep(1)
            else:
                if avgpid >= 100 :
                    state['heating'] = True
                    GPIO.output(conf.he_pin,1)
                    sleep(1)
                elif avgpid > 0 and avgpid < 100:
                    state['heating'] = True
                    GPIO.output(conf.he_pin,1)
                    sleep(avgpid/100.)
                    GPIO.output(conf.he_pin,0)
                    sleep(1-(avgpid/100.))
                    state['heating'] = False
                else:
                    GPIO.output(conf.he_pin,0)
                    state['heating'] = False
                    sleep(1)

    finally:
        GPIO.output(conf.he_pin,0)
        GPIO.cleanup()
