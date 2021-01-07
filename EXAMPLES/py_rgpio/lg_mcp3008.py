#!/usr/bin/env python
"""
lg_mcp3008.py
2021-01-09
Public Domain

http://abyz.me.uk/lg/py_lgpio.html
http://abyz.me.uk/lg/py_rgpio.html
"""

class MCP3008:
   """
   MCP3008 8 ch 10-bit ADC

   CH0     1 o o 16 V+
   CH1     2 o o 15 Vref
   CH2     3 o o 14 AGND
   CH3     4 o o 13 SCLK
   CH4     5 o o 12 SDO 
   CH5     6 o o 11 SDI 
   CH6     7 o o 10 CS/SHDN
   CH7     8 o o  9 DGND

   Be aware that SDO will be at the same voltage as V+.
   """
   def __init__(self, sbc, channel, device, speed=1e6, flags=0,
      chip_select=None, chip_deselect=None):
      """
      """
      self._sbc = sbc
      self._chip_select = chip_select
      self._chip_deselect = chip_deselect
      self._adc = sbc.spi_open(channel, device, speed, flags)

   def read_single_ended(self, channel):
      assert 0 <= channel <= 7

      if self._chip_select is not None:
         self._chipselect

      (b, d) = self._sbc.spi_xfer(self._adc, [1, 0x80+(channel<<4), 0])

      if self._chip_deselect is not None:
         self._chipdeselect

      c1 = d[1] & 0x03
      c2 = d[2]
      val = (c1<<8)+c2

      return val

   def read_differential_plus(self, channel):
      assert 0 <= channel <= 3

      if self._chip_select is not None:
         self._chipselect

      (b, d) = self._sbc.spi_xfer(self._adc, [1, channel<<5, 0])

      if self._chip_deselect is not None:
         self._chipdeselect

      c1 = d[1] & 0x03
      c2 = d[2]
      val = (c1<<8)+c2

      return val

   def read_differential_minus(self, channel):
      assert 0 <= channel <= 3

      if self._chip_select is not None:
         self._chipselect

      (b, d) = self._sbc.spi_xfer(self._adc, [1, (channel<<5)+16, 0])

      if self._chip_deselect is not None:
         self._chipdeselect

      c1 = d[1] & 0x03
      c2 = d[2]
      val = (c1<<8)+c2

      return val

   def close(self):
      self._sbc.spi_close(self._adc)

if __name__ == "__main__":

   RGPIO = True # set to True if using rgpio, False if using lgpio

   import time
   import lg_mcp3008

   if RGPIO:

      import rgpio
      sbc = rgpio.sbc()
      if not sbc.connected:
         exit()

   else:

      import lgpio as sbc

   adc = lg_mcp3008.MCP3008(sbc, 0, 1, 50000)

   end_time = time.time() + 60

   while time.time() < end_time:
      print(adc.read_single_ended(0))
      time.sleep(0.1)

   adc.close()

   if RGPIO:
      sbc.stop()

