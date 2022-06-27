# SPDX-FileCopyrightText: 2022 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT

# Mod June  2022 Jerry Isdale Maui Institute of Art and Technology
# from 2x4 buttons with two board, to 4x4 with 4 boards
# this is a mashup of adafruit's pico arcade box and stemma at button board

#not sure why but mu/cp keeps doing a reload/soft reboot unless we do this
# so then we have to use Ctrl-D to reload with Mu editor
import supervisor
supervisor.disable_autoreload()
print("autoreload disabled")

"""Arcade QT example that sends Midi Notes when the button LED on button press"""
import time
import board
import digitalio
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw.digitalio import DigitalIO
from adafruit_seesaw.pwmout import PWMOut

import usb_midi
import adafruit_midi
from adafruit_midi.note_on  import NoteOn
from adafruit_midi.note_off import NoteOff

#  MIDI setup as MIDI out device
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)


print("Hello! pico midi here");
print("try init i2c")

# rPi Pico also requires busio to get i2c
# for other boards see adafruit docs
import busio
i2c = busio.I2C(board.GP1, board.GP0)
print("i2c initialized")

# Now instantiate N of the Seesaw board instances
# each needs its own i2c address based on which jumpers are cut
# TODO: fill in correct addresses for 4 available addr
seeSawAddr = [0x3A] # only 1 for now: , 0x3A, 0x3A, 0x3A)
# for multi, build an array of these with different addr

# each ArcadeQT board hold supports 4 led/buttons
# these could be pwm or digital. pwm could be blocking or async efx
# button and led pins are consistent on all N boards
# Button pins in order (1, 2, 3, 4)
button_pins = (18, 19, 20, 2)
# LED pins in order (1, 2, 3, 4)
led_pins = (12, 13, 0, 1)

#  array of default MIDI notes
midi_notes = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]

# now build array of 4 boards
arcadeBoards =[]
print("create seesaw boards from array of addresses",seeSawAddr)
for idx, boardAddress in enumerate(seeSawAddr):
    print("try with board address",boardAddress)
    arcade_qt = Seesaw(i2c, addr=boardAddress)
    arcadeBoards.append(arcade_qt)

print("ArcadeBoards created",arcadeBoards)

# create arrays for buttons and leds
buttons = []
leds = []
for arcade_qt in arcadeBoards:
    for button_pin in button_pins:
        button = DigitalIO(arcade_qt, button_pin)
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.UP
        buttons.append(button)

    for led_pin in led_pins:
        #for now leds are DigialIO, would be nice to have PWM fadeIn/Out
        led = DigitalIO(arcade_qt, led_pin)
        led.direction = digitalio.Direction.OUTPUT
        leds.append(led)

print("Buttons initialized")
print(buttons)
print("Leds initialized")
print (leds)

# flash leds in order
for idx, led in enumerate(leds):
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)

# array of midiStates, one for each button, start in off/False state
midiStates = [False for i in range(len(buttons))]

# The delay on the PWM cycles. Increase to slow down the LED pulsing, decrease to speed it up.
delay = 0.01

print("looks like we got all setup, start forever loop")

while True:
    # buttons, leds and midiStates should all be same size
    for idx, button in enumerate(buttons):
        #  if button is pressed...
        if not button.value and midiStates[idx] is False:
            print("Button",str(idx),"pressed")
            # button just pressed, send the MIDI note and light up the LED
            midi.send(NoteOn(midi_notes[idx], 120))
            midiStates[idx] = True
            leds[idx].value = True
            #pwm led could fade in:
            #for cycle in range(pwm_minWidth, pwm_maxWidth, pwm_stepSize):
            #    leds[idx].duty_cycle = cycle
            #    time.sleep(delay)

        #  if the button is released...
        if button.value and midiStates[idx] is True:
            #  stop sending the MIDI note and turn off the LED
            print("Button",str(idx),"released")
            midi.send(NoteOff(midi_notes[idx], 120))
            midiStates[idx] = False
            leds[idx].value = False
            #for cycle in range(pwm_maxWidth, pwm_minWidth, -pwm_stepSize):
            #    arcade_qt.leds[led_number].duty_cycle = cycle
            #    time.sleep(delay)
