#!/usr/bin/env python
"""
lg_mcp4251.py
2021-01-20
Public Domain

http://abyz.me.uk/lg/py_lgpio.html
http://abyz.me.uk/lg/py_rgpio.html
"""

class MCP4251:
   """
   MCP4251 DIG DUAL POT

   CS      1 o o 14 V+
   SCLK    2 o o 13 SDO
   SDI     3 o o 12 SHDN
   GND     4 o o 11 WP
   P1B     5 o o 10 P0B
   P1W     6 o o  9 P0W
   P1A     7 o o  8 P0A

   This Python module does not use SDO which may be left unconnected.

   Be aware that SDO will be at the same voltage as V+.
   """
   MAX_WIPER_VALUE = 256
   WIPERS = 2

   def __init__(self, sbc, channel, device, speed=1e6, flags=0,
      wiper_value=128, enable=None):
      """
      """
      self._sbc = sbc
      self._enable = enable
      self._dac = sbc.spi_open(channel, device, speed, flags)
      self._wiper_value = [wiper_value]*2
      self.set_wiper(0, wiper_value)
      self.set_wiper(1, wiper_value)

   def set_wiper(self, wiper, value):
      assert 0 <= wiper < self.WIPERS
      assert 0 <= value <= self.MAX_WIPER_VALUE

      self._wiper_value[wiper] = value

      if self._enable is not None:
         self._enable(True)

      if value < self.MAX_WIPER_VALUE:
         b0 = wiper << 4
         b1 = value
      else:
         b0 = (wiper << 4) | 1
         b1 = 0

      self._sbc.spi_write(self._dac, [b0, b1])

      if self._enable is not None:
         self._enable(False)

   def get_wiper(self, wiper):
      assert 0 <= wiper < self.WIPERS
      return self._wiper_value[wiper]

   def increment_wiper(self, wiper):
      assert 0 <= wiper < self.WIPERS
      if self._wiper_value[wiper] < self.MAX_WIPER_VALUE:
         self.set_wiper(wiper, self._wiper_value[wiper] + 1)

   def decrement_wiper(self, wiper):
      assert 0 <= wiper < self.WIPERS
      if self._wiper_value[wiper] > 0:
         self.set_wiper(wiper, self._wiper_value[wiper] - 1)

   def close(self):
      self._sbc.spi_close(self._dac)

if __name__ == "__main__":

   RGPIO = True # set to True if using rgpio, False if using lgpio

   import time
   import lg_mcp4251

   if RGPIO:

      import rgpio
      sbc = rgpio.sbc()
      if not sbc.connected:
         exit()

   else:

      import lgpio as sbc

   dac = lg_mcp4251.MCP4251(sbc, 0, 0, 50000)

   for i in range(dac.MAX_WIPER_VALUE+1):
      dac.set_wiper(0, i)
      dac.set_wiper(1, dac.MAX_WIPER_VALUE-i)
      time.sleep(0.2)

   dac.close()

   if RGPIO:
      sbc.stop()

