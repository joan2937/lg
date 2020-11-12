#!/usr/bin/env python

# DHT.py
# 2020-10-16
# Public Domain

import time
import lgpio as sbc

DHTAUTO=0
DHT11=1
DHTXX=2

DHT_GOOD=0
DHT_BAD_CHECKSUM=1
DHT_BAD_DATA=2
DHT_TIMEOUT=3

class sensor:
   """
   A class to read the DHTXX temperature/humidity sensors.
   """
   def __init__(self, chip, gpio, model=DHTAUTO, callback=None):
      """
      Instantiate with the gpiochip, and the GPIO connected
      to the DHT temperature and humidity sensor.

      Optionally the model of DHT may be specified.  It may be one
      of DHT11, DHTXX, or DHTAUTO.  It defaults to DHTAUTO in which
      case the model of DHT is automtically determined.

      Optionally a callback may be specified.  If specified the
      callback will be called whenever a new reading is available.

      The callback receives a tuple of timestamp, GPIO, status,
      temperature, and humidity.

      The timestamp will be the number of seconds since the epoch
      (start of 1970).

      The status will be one of:
      0 DHT_GOOD (a good reading)
      1 DHT_BAD_CHECKSUM (receieved data failed checksum check)
      2 DHT_BAD_DATA (data receieved had one or more invalid values)
      3 DHT_TIMEOUT (no response from sensor)
      """
      self._chip = chip
      self._gpio = gpio
      self._model = model

      self._new_data = False

      self._bits = 0
      self._code = 0
      self._last_edge_tick = 0

      self._timestamp = time.time()
      self._status = DHT_TIMEOUT
      self._temperature = 0.0
      self._humidity = 0.0

      sbc.gpio_set_watchdog_micros(chip, gpio, 1000) # watchdog after 1 ms
      self._cb = sbc.callback(chip, gpio, sbc.RISING_EDGE, self._rising_edge)


   def _datum(self):
      return ((self._timestamp, self._gpio, self._status,
              self._temperature, self._humidity))

   def _validate_DHT11(self, b1, b2, b3, b4):
      t = b2
      h = b4
      if (b1 == 0) and (b3 == 0) and (t <= 60) and (h >= 9) and (h <= 90):
         valid = True
      else:
         valid = False
      return (valid, t, h)

   def _validate_DHTXX(self, b1, b2, b3, b4):
      if b2 & 128:
         div = -10.0
      else:
         div = 10.0
      t = float(((b2&127)<<8) + b1) / div
      h = float((b4<<8) + b3) / 10.0
      if (h <= 110.0) and (t >= -50.0) and (t <= 135.0):
         valid = True
      else:
         valid = False
      return (valid, t, h)

   def _decode_dhtxx(self):
      """
            +-------+-------+
            | DHT11 | DHTXX |
            +-------+-------+
      Temp C| 0-50  |-40-125|
            +-------+-------+
      RH%   | 20-80 | 0-100 |
            +-------+-------+

               0      1      2      3      4
            +------+------+------+------+------+
      DHT11 |check-| 0    | temp |  0   | RH%  |
            |sum   |      |      |      |      |
            +------+------+------+------+------+
      DHT21 |check-| temp | temp | RH%  | RH%  |
      DHT22 |sum   | LSB  | MSB  | LSB  | MSB  |
      DHT33 |      |      |      |      |      |
      DHT44 |      |      |      |      |      |
            +------+------+------+------+------+
      """
      b0 =  self._code        & 0xff
      b1 = (self._code >>  8) & 0xff
      b2 = (self._code >> 16) & 0xff
      b3 = (self._code >> 24) & 0xff
      b4 = (self._code >> 32) & 0xff
      
      chksum = (b1 + b2 + b3 + b4) & 0xFF

      if chksum == b0:
         if self._model == DHT11:
            valid, t, h = self._validate_DHT11(b1, b2, b3, b4)
         elif self._model == DHTXX:
            valid, t, h = self._validate_DHTXX(b1, b2, b3, b4)
         else: # AUTO
            # Try DHTXX first.
            valid, t, h = self._validate_DHTXX(b1, b2, b3, b4)
            if not valid:
               # try DHT11.
               valid, t, h = self._validate_DHT11(b1, b2, b3, b4)
         if valid:
            self._timestamp = time.time()
            self._temperature = t
            self._humidity = h
            self._status = DHT_GOOD
         else:
            self._status = DHT_BAD_DATA
      else:
         self._status = DHT_BAD_CHECKSUM
      self._new_data = True

   def _rising_edge(self, chip, gpio, level, tick):
      if level != sbc.TIMEOUT:
         edge_len = tick - self._last_edge_tick
         self._last_edge_tick = tick
         if edge_len > 2e8: # 0.2 seconds
            self._bits = 0
            self._code = 0
         else:
            self._code <<= 1
            if edge_len > 1e5: # 100 microseconds, so a high bit
               self._code |= 1
            self._bits += 1
      else: # watchdog
         if self._bits >= 30:
            self._decode_dhtxx()

   def _trigger(self):
      sbc.gpio_claim_output(self._chip, self._gpio, 0)
      if self._model != DHTXX:
         time.sleep(0.015)
      else:
         time.sleep(0.001)
      self._bits = 0
      self._code = 0
      sbc.gpio_claim_alert(
         self._chip, self._gpio, sbc.RISING_EDGE)

   def cancel(self):
      """
      """
      if self._cb is not None:
         self._cb.cancel()
         self._cb = None

   def read(self):
      """
      """
      self._new_data = False
      self._status = DHT_TIMEOUT
      self._trigger()
      for i in range(20): # timeout after 1 seconds.
         time.sleep(0.05)
         if self._new_data:
            break
      if not self._new_data:
         print("data timeout")
      datum = self._datum()
      return datum

if __name__== "__main__":
   import sys
   import argparse
   import lgpio
   import DHT # import current module as a class

   ap = argparse.ArgumentParser()

   ap.add_argument("-c", "--gpiochip", help="gpiochip device number",
      type=int, default=0)

   ap.add_argument("gpio", nargs="+", type=int)

   args = ap.parse_args()

   chip = sbc.gpiochip_open(args.gpiochip)

   # Instantiate a class for each GPIO

   S = []
   for g in args.gpio:
      s = DHT.sensor(chip, g)
      S.append(s) # save class

   while True:
      try:
         for s in S:
               d = s.read()
               print("{:.3f} g={:2d} s={} t={:3.1f} rh={:3.1f}".
                  format(d[0], d[1], d[2], d[3], d[4]))
         time.sleep(2)
      except KeyboardInterrupt:
         break

   for s in S:
      s.cancel()
