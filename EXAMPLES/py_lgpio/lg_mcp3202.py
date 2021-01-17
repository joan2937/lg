#!/usr/bin/env python
"""
lg_mcp3202.py
2021-01-17
Public Domain

http://abyz.me.uk/lg/py_lgpio.html
http://abyz.me.uk/lg/py_rgpio.html
"""

class MCP3202:
   """
   MCP3202 2 ch 12-bit ADC

   CS  1 o o 8 V+
   CH0 2 o o 7 CLK
   CH1 3 o o 6 DO
   GND 5 o o 4 DI

   Be aware that DO will be at the same voltage as V+.
   """
   def __init__(self, sbc, channel, device, speed=1e6, flags=0, enable=None):
      """
      """
      self._sbc = sbc
      self._enable = enable
      self._adc = sbc.spi_open(channel, device, speed, flags)

   def read_single_ended(self, channel):
      assert 0 <= channel <= 1

      if self._enable is not None:
         self._enable(True)

      (b, d) = self._sbc.spi_xfer(self._adc, [1, 0xA0+(channel<<6), 0])

      if self._enable is not None:
         self._enable(False)

      c1 = d[1] & 0x0f
      c2 = d[2]
      val = (c1<<8)+c2

      return val

   def read_differential_plus(self):

      if self._enable is not None:
         self._enable(True)

      (b, d) = self._sbc.spi_xfer(self._adc, [1, 0x20, 0])

      if self._enable is not None:
         self._enable(False)

      c1 = d[1] & 0x0f
      c2 = d[2]
      val = (c1<<8)+c2

      return val

   def read_differential_minus(self):

      if self._enable is not None:
         self._enable(True)

      (b, d) = self._sbc.spi_xfer(self._adc, [1, 0x60, 0])

      if self._enable is not None:
         self._enable(False)

      c1 = d[1] & 0x0f
      c2 = d[2]
      val = (c1<<8)+c2

      return val

   def close(self):
      self._sbc.spi_close(self._adc)

if __name__ == "__main__":

   RGPIO = False # set to True if using rgpio, False if using lgpio

   import time
   import lg_mcp3202

   if RGPIO:

      import rgpio
      sbc = rgpio.sbc()
      if not sbc.connected:
         exit()

   else:

      import lgpio as sbc

   adc = lg_mcp3202.MCP3202(sbc, 0, 1, 50000)

   end_time = time.time() + 60

   while time.time() < end_time:
      print(adc.read_single_ended(0))
      time.sleep(0.1)

   adc.close()

   if RGPIO:
      sbc.stop()

