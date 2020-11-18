#!/usr/bin/env python
"""
monitor.py
2020-11-18
Public Domain

http://abyz.me.uk/lg/py_lgpio.html

./monitor.py [chip:]gpio ...

chip specifies a gpiochip number.  gpio is a GPIO in the previous
gpiochip (gpiochip0 if there is no previous gpiochip).

e.g.

./monitor.py 23 24 25        # monitor gpiochip0: 23,24,25
./monitor.py 0:23 24 1:0 5 6 # monitor gpiochip0: 23,24 gpiochip1: 0,5,6
"""

import sys
import time
import lgpio as sbc

def cbf(chip, gpio, level, tick):
   print("chip={} gpio={} level={} time={:.09f}".format(
      chip, gpio, level,  tick / 1e9))

handle = -1
chip = 0
gpio = 0

argc = len(sys.argv)

sbc.exceptions = False

for i in range(1, argc):

   p = sys.argv[i].split(':')

   if len(p) == 2:

      # chip:gpio option

      c = int(p[0])
      g = int(p[1])

      print("chip={} gpio={}".format(c, g))

      if c != chip:
         handle = -1; # force open of new gpiochip

      chip = c
      gpio = g

   elif len(p) == 1:

      # gpio option

      g = int(p[0])

      print("chip={} gpio={}".format(chip, g))

      # chip the same as previous
      gpio = g

   else:

      # bad option

      print("don't understand {}".format(sys.argv[i]))
      exit()

   if gpio >= 0:

      if handle < 0:

         # get a handle to the gpiochip
         handle = sbc.gpiochip_open(chip)

      if handle >= 0:

         # got a handle, now open the GPIO for alerts
         err = sbc.gpio_claim_alert(handle, gpio, sbc.BOTH_EDGES)

         if err < 0:

            print("GPIO in use {}:{} ({})",
               chip, gpio, sbc.error_text(err))
            exit()

         cb_id = sbc.callback(handle, gpio, sbc.BOTH_EDGES, cbf)

      else:

         print("can't open gpiochip {} ({})".format(
            chip, sbc.error_text(handle)))
         exit()

   else:

      print("don't understand {}".format(sys.argv[i]))
      exit()

sbc.exceptions = True

while True:
   time.sleep(1)

