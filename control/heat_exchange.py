from time import sleep
import RPi.GPIO as GPIO
import config as conf
import sys

def he_control_loop(dummy,state):

    num_he_failures = 0
    while True:
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(conf.he_pin, GPIO.OUT)
            GPIO.output(conf.he_pin,0)

            heating = False

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
            print("Encountered a failure in GPIO output!!")
            if num_he_failures > conf.gpio_errors:
                print("Cleaning up the GPIO and exiting gracefully")
                GPIO.output(conf.he_pin,0)
                GPIO.cleanup()
                sys.exit("Too many GPIO Errors...")
            else:
                print("Retrying...")
                num_he_failures += 1
                state['num_he_failures'] = num_he_failures
                sleep(1)
