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
i2c = busio.I2C(board.GP1, board.GP0, frequency=400000)
print("i2c initialized")

# Now instantiate N of the Seesaw board instances
# each needs its own i2c address based on which jumpers are cut
seeSawAddr = [0x3B, 0x3C, 0x3E, 0x42]
specialAddr = 0x3A

# each ArcadeQT board hold supports 4 led/buttons
# these could be pwm or digital. pwm could be blocking or async efx
# button and led pins are consistent on all N boards
# Button pins in order (1, 2, 3, 4)
button_pins = (18, 19, 20, 2)
# LED pins in order (1, 2, 3, 4)
led_pins = (12, 13, 0, 1)

#  array of default MIDI notes
# order here will be how they are assigned to array of all buttons
midi_notes_a = [
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
    75
]

midi_notes_b = [
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25
]

midi_notes_c = [
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45
]

midi_notes_d = [
    80,
    81,
    82,
    83,
    84,
    85,
    86,
    87,
    88,
    89,
    90,
    91,
    92,
    93,
    94,
    95
]

midi_notes = midi_notes_a

# now build array of 4 boards
arcadeBoards = []
print("create seesaw boards from array of addresses", seeSawAddr)
for idx, boardAddress in enumerate(seeSawAddr):
    print("try with board address", boardAddress)
    arcade_qt = Seesaw(i2c, addr=boardAddress)
    arcadeBoards.append(arcade_qt)

specialBoard = Seesaw(i2c, addr=specialAddr)
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


special_buttons = []
special_leds = []

for button_pin in button_pins:
    button = DigitalIO(specialBoard, button_pin)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    special_buttons.append(button)

for led_pin in led_pins:
    # orig leds were DigialIO, changed to PWM to support fadeIn/Out
    led = DigitalIO(specialBoard, led_pin)
    led.direction = digitalio.Direction.OUTPUT
    #led = PWMOut(specialBoard, led_pin)
    special_leds.append(led)

special_leds[0].value = True
special_leds[1].value = False
special_leds[2].value = False
special_leds[3].value = False

print("Buttons initialized")
print(buttons)
print("Leds initialized")
print(leds)

# array of midiStates, one for each button, start in off/False state
midiStates = [False for i in range(len(buttons))]

# some constants for fading
minDutyCycle = 1000
maxDutyCycle = 65535
stepDutyCycle = 4000
fadeDelay = 0.001


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
    time.sleep(fadeDelay)
    fadeOut(led)  # led.value = False
    time.sleep(fadeDelay)
    # led.duty_cycle = 0

def checkMidiButtons ():
    # buttons, leds and midiStates should all be same size
    # check each button using current value & midiState to determine when
    # button is pressed or released, ignoring held down
    for idx, button in enumerate(buttons):
        #  if button is pressed...
        if not button.value and midiStates[idx] is False:
            print("Button", str(idx), "pressed note:", str(midi_notes[idx]))
            print(midi_notes)
            # button just pressed, send the MIDI note and light up the LED
            midi.send(NoteOn(midi_notes[idx], 120))
            midiStates[idx] = True
            fadeIn(leds[idx])
            # leds[idx].value = True

        #  if the button is released...
        if button.value and midiStates[idx] is True:
            #  stop sending the MIDI note and turn off the LED
            print("Button", str(idx), "released note:", str(midi_notes[idx]))
            midi.send(NoteOff(midi_notes[idx], 120))
            midiStates[idx] = False
            fadeOut(leds[idx])
            # leds[idx].value = False

def checkSpecialButtons ():
    global midi_notes
    # buttons, leds and midiStates should all be same size
    # check each button using current value & midiState to determine when
    # button is pressed or released, ignoring held down
    for idx, button in enumerate(special_buttons):
        #  if button is pressed...
        if not button.value and special_leds[idx].value is False:
            # button pressed,
            if idx is 0:
                midi_notes = midi_notes_a
                special_leds[0].value = True
                special_leds[1].value = False
                special_leds[2].value = False
                special_leds[3].value = False
            elif idx is 1:
                midi_notes = midi_notes_b
                special_leds[0].value = False
                special_leds[1].value = True
                special_leds[2].value = False
                special_leds[3].value = False
            elif idx is 2:
                midi_notes = midi_notes_c
                special_leds[0].value = False
                special_leds[1].value = False
                special_leds[2].value = True
                special_leds[3].value = False
            else :
                midi_notes = midi_notes_d
                special_leds[0].value = False
                special_leds[1].value = False
                special_leds[2].value = False
                special_leds[3].value = True
            print(midi_notes)
            # leds[idx].value = True

print("looks like we got all setup, start forever loop")

while True:
    checkMidiButtons()
    checkSpecialButtons()
