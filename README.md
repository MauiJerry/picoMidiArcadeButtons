# picoMidiArcadeButtons
Raspberry Pi Pico 4xN midi buttons with Adafruit 1x4 i2c Stemma QT board

inspired by two Adafruit projects:
1) https://learn.adafruit.com/raspberry-pi-pico-led-arcade-button-midi-controller-fighter
   a 4x4 array of buttons with fancy little screen to change their notes
   buttons and leds are dirctly connected to the rPi Pico
2) https://learn.adafruit.com/adafruit-led-arcade-button-qt/arduino
   uses the Adafruit LED Arcade Button 1x4 STEMMA QT to handle buttons by i2c
   this is much nicer but doesnt do the midi or fadeIn/Out
   
The Arcade Buttons https://www.adafruit.com/product/3491 have a plain white led. They offer different color options for the plastic housing. The documentation doesnt give reference as to which are switch vs led pins:
 * switch is on staggered pins
 * led +/- is on in-line pins, +- with arrows point to that side

The i2c board (https://www.adafruit.com/product/5296) makes it MUCH easier to build a 4xN button box. Using I2C withjumper locations, up to 16 boards can be supported.  The arcade button quick connect wires (https://www.adafruit.com/product/1152) eliminate soldering for buttons/leds.  This reduces total number of solder connections to the 4 i2c lines.

The Adafruit code examples are written to support multiple boards. Some use board.i2c others use busio.I2C. Neither example mentions the rPi Pico.  The Pico uses busio.  I eliminated the board.i2c to reduce confusion.

There are five python files in top level, but really code.py is a copy of one of others. CircuitPython will execute code.py when the pico is booted.  Two versions of code are:
 * code_QTMidi_digLED.py: uses simple on/off digital leds
 * code_QTMidi_pwmLED.py: uses pwm leds for fadeIn fadeOut effects
 * code_QTMidi_5x4.py: pwm version supporting 5 1x4 boards for 20 total buttons
 * code_QTMidi_bankSwitch.py: one of 5 boards is used to Bank Switch the other 4 (16) midi buttons
 
copy desired version to code.py

note the program uses print statements sent to USB.
this should not affect midi devices but is useful for debugging
especially using the Mu editor

Currently the two primary examples only have one arcade_qt defined at the default address (0x3A). The 5x4.py version adds four more boards. See  "https://learn.adafruit.com/adafruit-led-arcade-button-qt" section "Addres Jumpers" (under Pinout section) for the addresses.  Insert these in:
   seeSawAddr = [0x3A, 0x3B, 0x3C, 0x3E, 0x42]  

When adding boards, you must also extend midi_notes[] so there are the proper number for your setup.  The 5x4.py version exends this array to 20 notes.

The "code_MidiQT_bankSwitch.py" version drops back to 16 midi buttons, with the 5th (default address) board being used as a "bank switch" - it changes the midi notes associated with the midi buttons.  4 arrays are used to hold the Banks, and pressing one of the BankSwitches,  changes which bank is active.
