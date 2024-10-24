# pixel trinkey mouse jiggler
"""
Wrting this, I considered the circuitpython 'no sleeping' guide.
https://learn.adafruit.com/multi-tasking-with-circuitpython/no-sleeping
It uses time.monotonic() and comparison instead of the sleep() function.
That would have lead to button press waits and led waits to conflict or stack and mess up timing.
"""

import time
import board
import touchio
import neopixel

import usb_hid
from adafruit_hid.mouse import Mouse
from random import randint

import supervisor

#------------------------------------------------------------------------------#
# Waste of flashRAM to import all these, but here are the class names.         #
# Importing more than 4-5 of these causes the trinkey to crash.                #
# overall I think this should be replaced with manually setting the led's      #
# but this mouse mover example is very very small so I'm not worried.          #
# https://github.com/adafruit/Adafruit_CircuitPython_LED_Animation/tree/main   #
#------------------------------------------------------------------------------#
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.solid import Solid
import adafruit_led_animation.color as color
### RED, YELLOW, ORANGE, GREEN, TEAL, CYAN, BLUE, PURPLE, MAGENTA, WHITE, BLACK, GOLD, PINK, AQUA, JADE, AMBER, OLD_LACE

pixels = neopixel.NeoPixel(board.NEOPIXEL, 4)
touch1 = touchio.TouchIn(board.TOUCH1)
touch2 = touchio.TouchIn(board.TOUCH2)
DEBUG = False


"""
the brightness of these neopixels is crazy! This is not a lighting project, they are indicators!
setting this to 1/40 is bright enough to see in a brightly lit room. 
1/128 is low enough to see the indiviual leds in the neopixel.
Warning: The adafruit animations look horrifically ugly at low brightness because the R,G,B values scale right down to 0/off.
Droping the 'pulse' animation for that reason.

looks like the pixels on this board are rgb, not rgbw
"""
default_brightness = (1/128)
pixels.brightness = default_brightness

blink_blue = Blink(pixels, 0.5, color.BLUE)
blink_red = Blink(pixels, 0.5, color.BLUE)
chase_cyan = Chase(pixels, 0.5, color.CYAN)
chase_red = Chase(pixels, 0.5, color.RED)
solid_red = Solid(pixels, color.RED)
solid_green = Solid(pixels, color.GREEN)
solid_yellow = Solid(pixels, color.YELLOW)

idle_animation = chase_cyan

loop_start= time.monotonic()
last_move = loop_start # starter value for the mouse mover
move_interval = 30 # seconds between moves
mouse = Mouse(usb_hid.devices)
move_length = 1 # length of each move in seconds
move_started = False # to avoid starting a new move before the previous one is finished

touch_any = False # use for both buttons
touched1 = False # use for button 1
touched2 = False # use for button 2
touch_time = 3 # touch sensor delay time, seconds
touch_started = False # to avoid starting a new touch before the previous one is finished
first_touch = time.monotonic() # used by touch sensors to remember the first touch event

def jiggle():
    """ Move cursor a random x and y distance between 1 and 50 pixels then move it back """
    for each in range(randint(1, 4)):
        x = randint(1, 50)
        y = randint(1, 50)
        mouse.move(x, y)
        mouse.move(-x, -y)
    
while True:
	#determine what animation to show based on some conditions
    shown_animation = idle_animation
    

    # initial warmup to show board was reset soft or hard
    if (time.monotonic()-loop_start) < 3:
        # once at start for two seconds
        shown_animation = blink_blue

    # initial warmup to show board was reset soft or hard
    
    if (time.monotonic()-last_move) > move_interval:
        # every move_interval seconds
        shown_animation = solid_yellow

        # enter conditions for the move period are met
        if move_started == False:
            move_time = time.monotonic()
            move_started = True
            jiggle()

        if (time.monotonic()-move_time) > move_length:
            # move is finished, reset the move_started flag and previous move time
            # move actually takes much less time than the alloted length, but brief flashes are hard to read.
            shown_animation = idle_animation
            last_move = time.monotonic()
            move_started = False

    if touch1.value or touch2.value:
        shown_animation = solid_red
        if touch_any == False:
            # entry conditions to check for a long press event
            touch_any = True
            first_touch = time.monotonic()
        else:
            touched1 = touch1.value
            touched2 = touch2.value
            # check that both buttons have been pressed for a long enough period to be considered a long press event
            if ((time.monotonic()-first_touch) > touch_time) and touched1 == True and touched2 == True:
                shown_animation = solid_green
                # See boot.py comments for why I cant put the microcontroller into USB storage and REPL mode from here. 
                # this is a gentle reset, like control-D in the REPL
                supervisor.reload()

             
    else:
        # neither touch sensor is activated, put flags back to defaults
        touch_any = False
        touched1 = False 
        touched2 = False 
        touch_started = False
        first_touch = None

    """
    the LED should look like:
    blink blue to greet / show a reset state
    chase cyan to show running / waiting

    circuitpython has their own led states i wont need to replace:
    - One green flash - code completed without error. 
    - Two red flashes - code ended due to an exception. 
    - Three yellow flashes - safe mode.
    These are at full brightness, look for a way to reduce that. 
    """
    # finally show the relevant animation
    shown_animation.animate()