#!/usr/bin/env python3
# #Libraries
import RPi.GPIO as GPIO
import tm1637
import datetime
import time
import timeout_decorator

# setup the tm1637 4 digit 7 segment display
tm = tm1637.TM1637(clk=6, dio=5)

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
# set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
 
# set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
debug = False

def display_time(turn_on):
    """ display the time on the tm1637 display

    Inputs:
        turn_on (bool) - True will display the current time for 10 seconds, False will clear the display
    """
    if debug:
        print(f"turn_on = {turn_on}")
    if turn_on:
        for x in range(0,10):
            if debug:
                print(f"loop {x}")
            now = datetime.datetime.now()
            hour = now.hour
            minute = now.minute
            tm.numbers(hour, minute)
            time.sleep(1)
    else:
        tm.write([0, 0, 0, 0])

@timeout_decorator.timeout(2)
def detect_object(object_closer_then):
    """Check if the sensor is reading any objects within a given distance.

    Inputs
        object_closer_then (int) - the distance in CM that an object should be closer then
    Returns
        Boolean, True if distance < object_closer_then, False if it is not
    """
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    if debug:
        print ("Measured Distance = %.1f cm" % distance)

    return distance < object_closer_then


if __name__ == '__main__':
    print("Starting motion-clock v1.0")
    try:
        while True:
            turn_on = False
            if detect_object(45):
                turn_on = True
                #confirm it's still there 3 more times
                for x in range(0,3):
                    time.sleep(0.1)
                    print(f"verifying detection, attempt {x}")
                    if not detect_object(45):
                        turn_on = False
                        break
            display_time(turn_on)
            time.sleep(0.25)
 
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()