#!/usr/bin/env python
"""
rotary_encoder.py
2020-11-18
Public Domain

http://abyz.me.uk/lg/py_rgpio.html

./rotary_encoder.py [chip] gpioA gpioB

E.g.

./rotary_encoder.py 20 21 # gpiochip 0, gpioA 20, gpioB 21

./rotary_encoder.py 2 7 5 # gpiochip 2, gpioA 7, gpioB 5
"""

import rgpio

class decoder:

   """Class to decode mechanical rotary encoder pulses."""

   def __init__(self, sbc, gpiochip, gpioA, gpioB, callback):

      """
      Instantiate the class with the sbc, gpiochip, and GPIO connected
      to rotary encoder contacts A and B.  The common contact
      should be connected to ground.  The callback is
      called when the rotary encoder is turned.  It takes
      one parameter which is +1 for clockwise and -1 for
      counterclockwise.

      EXAMPLE

      import time
      import rgpio

      import rotary_encoder

      pos = 0

      def callback(way):

         global pos

         pos += way

         print("pos={}".format(pos))

      sbc = rgpio.sbc()
      if not sbc.connected:
         exit()

      decoder = rotary_encoder.decoder(sbc, 0, 7, 8, callback)

      time.sleep(300)

      decoder.cancel()

      sbc.stop()
      """

      self.sbc = sbc
      self.chip = sbc.gpiochip_open(gpiochip)
      self.gpioA = gpioA
      self.gpioB = gpioB
      self.callback = callback

      self.levA = 0
      self.levB = 0

      self.lastGpio = None

      self.sbc.gpio_claim_alert(self.chip, gpioA, rgpio.BOTH_EDGES)

      self.sbc.gpio_claim_alert(self.chip, gpioB, rgpio.BOTH_EDGES)

      self.cbA = self.sbc.callback(
         self.chip, gpioA, rgpio.BOTH_EDGES, self._pulse)

      self.cbB = self.sbc.callback(
         self.chip, gpioB, rgpio.BOTH_EDGES, self._pulse)

   def _pulse(self, chip, gpio, level, tick):

      """
      Decode the rotary encoder pulse.

                   +---------+         +---------+      0
                   |         |         |         |
         A         |         |         |         |
                   |         |         |         |
         +---------+         +---------+         +----- 1

             +---------+         +---------+            0
             |         |         |         |
         B   |         |         |         |
             |         |         |         |
         ----+         +---------+         +---------+  1
      """

      if gpio == self.gpioA:
         self.levA = level
      else:
         self.levB = level;

      if gpio != self.lastGpio: # debounce
         self.lastGpio = gpio

         if   gpio == self.gpioA and level == 1:
            if self.levB == 1:
               self.callback(1)
         elif gpio == self.gpioB and level == 1:
            if self.levA == 1:
               self.callback(-1)

   def cancel(self):

      """
      Cancel the rotary encoder decoder.
      """

      self.cbA.cancel()
      self.cbB.cancel()

if __name__ == "__main__":

   import time
   import sys

   import rgpio

   import rotary_encoder

   if len(sys.argv) == 4: # chip gpioA gpioB
      chip = int(sys.argv[1])
      gpioA = int(sys.argv[2])
      gpioB = int(sys.argv[3])

   elif len(sys.argv) == 3: # gpioA gpioB (chip 0)
      chip = 0
      gpioA = int(sys.argv[1])
      gpioB = int(sys.argv[2])

   else:
      print("Usage: ./rotary_encoder.py [chip] gpioA gpioB")
      exit()

   pos = 0

   def callback(way):

      global pos

      pos += way

      print("pos={}".format(pos))

   sbc = rgpio.sbc()
   if not sbc.connected:
      exit()

   decoder = rotary_encoder.decoder(sbc, chip, gpioA, gpioB, callback)

   time.sleep(300)

   decoder.cancel()

   sbc.stop()

