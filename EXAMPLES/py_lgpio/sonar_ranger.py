#!/usr/bin/env python
"""
sonar_ranger.py
2020-11-20
Public Domain

http://abyz.me.uk/lg/py_rgpio.html

./sonar_ranger.py [chip] trigger echo

chip specifies a gpiochip number.  gpio is a GPIO in the previous
gpiochip (gpiochip0 if there is no previous gpiochip).

e.g.

./sonar_ranger.py 1 24 25 # ping gpiochip1: trigger 24, echo 25
./sonar_ranger.py 24 25   # ping gpiochip0: trigger 24, echo 25
"""

import time
import lgpio

class ranger:
   """
   This class encapsulates a type of acoustic ranger.  In particular
   the type of ranger with separate trigger and echo pins.

   A pulse on the trigger initiates the sonar ping and shortly
   afterwards a sonar pulse is transmitted and the echo pin
   goes high.  The echo pins stays high until a sonar echo is
   received (or the response times-out).  The time between
   the high and low edges indicates the sonar round trip time.
   """

   def __init__(self, sbc, chip, trigger, echo):
      """
      The class is instantiated with the SBC to use, the gpiochip,
      and the GPIO connected to the trigger and echo pins.
      """
      self._sbc  = sbc
      self._chip = chip
      self._trigger = trigger
      self._echo = echo

      self._ping = False
      self._high = None
      self._time = None

      self._handle = sbc.gpiochip_open(chip)

      sbc.gpio_claim_output(self._handle, trigger)

      sbc.gpio_claim_alert(self._handle, echo, sbc.BOTH_EDGES)

      self._cb = sbc.callback(self._handle, echo, sbc.BOTH_EDGES, self._cbf)

      self._inited = True

   def _cbf(self, chip, gpio, level, tick):
      if level == 1:
         self._high = tick
      else:
         if self._high is not None:
            self._time = tick - self._high
            self._high = None
            self._ping = True

   def read(self):
      """
      Return the distance in cms if okay, otherwise 0.
      """
      if self._inited:
         self._ping = False
         # send a 15 microsecond high pulse as trigger
         self._sbc.tx_pulse(self._handle, self._trigger, 15, 0, 0, 1)
         start = time.time()
         while not self._ping:
            if (time.time()-start) > 0.3:
               return 0
            time.sleep(0.01)
         return 17015 * self._time / 1e9
      else:
         return None

   def cancel(self):
      """
      Cancels the ranger and returns the gpios to their
      original mode.
      """
      if self._inited:
         self._inited = False
         self._cb.cancel()
         self._sbc.gpio_free(self._chip, self._trigger)
         self._sbc.gpio_free(self._chip, self._echo)
         self._sbc.gpiochip_close(self._chip)
if __name__ == "__main__":

   import sys
   import time
   import lgpio as sbc
   import sonar_ranger

   if len(sys.argv) == 4: # chip trigger echo
      chip = int(sys.argv[1])
      trigger = int(sys.argv[2])
      echo = int(sys.argv[3])

   elif len(sys.argv) == 3: # trigger echo (chip 0)
      chip = 0
      trigger = int(sys.argv[1])
      echo = int(sys.argv[2])

   else:
      print("Usage: ./sonar_ranger.py [chip] trigger echo")
      exit()

   ranger = sonar_ranger.ranger(sbc, chip, trigger, echo)

   try:
      while True:
         print("cms={:.1f}".format(ranger.read()))
         time.sleep(0.2)
   except KeyboardInterrupt:
      pass

   ranger.cancel()

