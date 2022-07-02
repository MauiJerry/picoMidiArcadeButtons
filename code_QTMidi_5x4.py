# SPDX-FileCopyrightText: 2022 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
# Mod June  2022 Jerry Isdale Maui Institute of Art and Technology
# this is a mashup of adafruit's pico arcade box and stemma at button board
# Can support N of the seesaw arcadeQT boards at different i2c addresses
# creates consolidated array of buttons, leds and midiStates, adding 4 for each board
# an array midi_notes[] hard codes the midi note numbers

"""Arcade QT example that sends Midi Notes when the button-LED is button pressed"""
import time
import board
import digitalio
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw.digitalio import DigitalIO
from adafruit_seesaw.pwmout import PWMOut
import busio
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

# not sure why but mu/cp keeps doing a reload/soft reboot unless we do this
# so then we have to use Ctrl-D to reload with Mu editor
import supervisor

supervisor.disable_autoreload()
print("autoreload disabled")

#  MIDI setup as MIDI out device
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

# bunch of print statements for debugging in Mu editor
print("Hello! pico midi here")
print("try init i2c")

# rPi Pico also requires busio to get i2c
# for other boards see adafruit docs
i2c = busio.I2C(board.GP1, board.GP0)
print("i2c initialized")

# Now instantiate N of the Seesaw board instances
# each needs its own i2c address based on which jumpers are cut
# TODO: fill in correct addresses for 4 available addr
seeSawAddr = [0x3A, 0x3B, 0x3C, 0x3E, 0x42]  # only 4 for now: , 0x3A, 0x3A, 0x3A)

# each ArcadeQT board hold supports 4 led/buttons
# these could be pwm or digital. pwm could be blocking or async efx
# button and led pins are consistent on all N boards
# Button pins in order (1, 2, 3, 4)
button_pins = (18, 19, 20, 2)
# LED pins in order (1, 2, 3, 4)
led_pins = (12, 13, 0, 1)

#  array of default MIDI notes
# order here will be how they are assigned to array of all buttons
midi_notes = [
    60,
    61,
    62,
    63,
    64,
    65,
    66,
    67,
    68,
    69,
    70,
    71,
    72,
    73,
    74,
    75,
    76,
    77,
    78,
    79,
]

# now build array of 4 boards
arcadeBoards = []
print("create seesaw boards from array of addresses", seeSawAddr)
for idx, boardAddress in enumerate(seeSawAddr):
    print("try with board address", boardAddress)
    arcade_qt = Seesaw(i2c, addr=boardAddress)
    arcadeBoards.append(arcade_qt)

print("ArcadeBoards created", arcadeBoards)

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
        # orig leds were DigialIO, changed to PWM to support fadeIn/Out
        # led = DigitalIO(arcade_qt, led_pin)
        # led.direction = digitalio.Direction.OUTPUT
        led = PWMOut(arcade_qt, led_pin)
        leds.append(led)

print("Buttons initialized")
print(buttons)
print("Leds initialized")
print(leds)

# array of midiStates, one for each button, start in off/False state
midiStates = [False for i in range(len(buttons))]

# some constants for fading
minDutyCycle = 500
maxDutyCycle = 65535
stepDutyCycle = 2000
fadeDelay = 0.01


def fadeIn(led):
    for cycle in range(minDutyCycle, maxDutyCycle, stepDutyCycle):
        led.duty_cycle = cycle
        time.sleep(fadeDelay)
    led.duty_cycle = maxDutyCycle


def fadeOut(led):
    for cycle in range(maxDutyCycle, minDutyCycle, -stepDutyCycle):
        led.duty_cycle = cycle
        time.sleep(fadeDelay)
    led.duty_cycle = minDutyCycle


# cycle all leds in order
for idx, led in enumerate(leds):
    fadeIn(led)  # .value = True
    time.sleep(0.1)
    fadeOut(led)  # led.value = False
    time.sleep(0.1)
    # led.duty_cycle = 0

print("looks like we got all setup, start forever loop")
while True:
    # buttons, leds and midiStates should all be same size
    # check each button using current value & midiState to determine when
    # button is pressed or released, ignoring held down
    for idx, button in enumerate(buttons):
        #  if button is pressed...
        if not button.value and midiStates[idx] is False:
            print("Button", str(idx), "pressed")
            # button just pressed, send the MIDI note and light up the LED
            midi.send(NoteOn(midi_notes[idx], 120))
            midiStates[idx] = True
            fadeIn(leds[idx])
            # leds[idx].value = True

        #  if the button is released...
        if button.value and midiStates[idx] is True:
            #  stop sending the MIDI note and turn off the LED
            print("Button", str(idx), "released")
            midi.send(NoteOff(midi_notes[idx], 120))
            midiStates[idx] = False
            fadeOut(leds[idx])
            # leds[idx].value = False
    time.sleep(0.1)
