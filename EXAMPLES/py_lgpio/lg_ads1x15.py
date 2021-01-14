#!/usr/bin/env python
"""
lg_ads1x15.py
2021-01-14
Public Domain

http://abyz.me.uk/lg/py_lgpio.html
http://abyz.me.uk/lg/py_rgpio.html
"""

class _ads1x15:
   """
   ada1015 4 ch 12-bit ADC 3300 sps
   ads1115 4 ch 16-bit ADC 860 sps

   F E D C   B A 9 8   7 6 5 4   3 2 1 0
   Z C C C   V V V S   R R R W   P L Q Q

   Z    1=start conversion
   CCC  0=A0/A1(*) 1=A0/A3 2=A1/A3 3=A2/A3 4=A0 5=A1 6=A2 7=A3
   VVV  0=6.144 1=4.096 2=2.048(*) 3=1.024 4=0.512 5=0.256 6=0.256 7=0.256
   S    0=continuous 1=single shot(*)
   RRR  0=8   1=16  2=32  3=64  4=128  5=250  6=475  7=860 sps ADS1115
   RRR  0=128 1=250 2=490 3=920 4=1600(*) 5=2400 6=3300 7=3300 sps ADS1015
   W    0=traditional(*) 1=window
   P    ALERT/RDY pin 0=active low(*)  1=active high
   L    comparator 0=non-latching(*) 1=latching
   QQ   queue 0=after 1 1=after 2, 2=after 4, 3=disable(*)
   """

   _GAIN=[6.144, 4.096, 2.048, 1.024, 0.512, 0.256, 0.256, 0.256]
   _CHAN=["A0-A1", "A0-A3", "A1-A3", "A2-A3", "A0", "A1", "A2", "A3"]

   A0_1 = 0
   A0_3 = 1
   A1_3 = 2
   A2_3 = 3
   A0 = 4
   A1 = 5
   A2 = 6
   A3 = 7

   _AR_ALERT = 0
   _AR_READY = 1
   _AR_NEVER = 2

   def _read_config(self):

      self._sbc.i2c_write_device(self._adc, [1]) # set config register

      (b, d) = self._sbc.i2c_read_device(self._adc, 2)

      self._configH = d[0]
      self._configL = d[1]

      self._sbc.i2c_write_device(self._adc, [2]) # set low compare register

      (b, d) = self._sbc.i2c_read_device(self._adc, 2)

      low = (d[0] << 8) | d[1]

      self._sbc.i2c_write_device(self._adc, [3]) # set high compare register

      (b, d) = self._sbc.i2c_read_device(self._adc, 2)

      high = (d[0] << 8) | d[1]

      self._sbc.i2c_write_device(self._adc, [0]) # set conversion register

      self._channel = (self._configH >> 4) & 7
      self._gain = (self._configH >> 1) & 7
      self._voltage_range = self._GAIN[self._gain]
      self._single_shot = self._configH & 1
      self._sps = (self._configL >> 5) & 7
      self._comparator_mode = (self._configL >> 4) & 1
      self._comparator_polarity = (self._configL >> 3) & 1
      self._comparator_latch = (self._configL >> 2) & 1
      self._comparator_queue = self._configL & 3

      if self._comparator_queue != 3:
         self._set_queue = self._comparator_queue
      else:
         self._set_queue = 0

   def _write_config(self):
      self._sbc.i2c_write_device(self._adc, [1, self._configH, self._configL])

      self._sbc.i2c_write_device(self._adc, [0])

   def _write_comparator_thresholds(self, high, low):

      if high > 32767:
         high = 32767
      elif high < -32768:
         high = -32768

      if low > 32767:
         low = 32767
      elif low < -32768:
         low = -32768

      self._sbc.i2c_write_device(self._adc,
         [3, (high >> 8) & 0xff, high & 0xff])

      self._sbc.i2c_write_device(self._adc,
         [2, (low >> 8) & 0xff, low & 0xff])

      self._sbc.i2c_write_device(self._adc, [0])

   def _update_comparators(self):

      if self._alert_rdy == self._AR_ALERT:

         h = int(self._vhigh * 32768 / self._voltage_range)
         l = int(self._vlow * 32768 / self._voltage_range)

         self._write_comparator_thresholds(h, l)

   def _update_config(self):

      H = self._configH
      L = self._configL

      self._configH = ((1 << 7) | (self._channel << 4) |
         (self._gain << 1) | self._single_shot)

      self._configL = ((self._sps << 5) | (self._comparator_mode << 4) |
         (self._comparator_polarity << 3) | (self._comparator_latch << 2) |
         self._comparator_queue)

      if (H != self._configH) or (L != self._configL):
         self._write_config()

   def __init__(self, sbc, bus, address, flags=0):
      """
      """
      self._sbc = sbc
      self._adc = sbc.i2c_open(bus, address, flags)

      self._read_config()

      self.alert_never() # switch off ALERT/RDY pin.

   def set_comparator_polarity(self, level):
      """
      Set the level of the ALERT/RDY pin when active.

      1 for active high, 0 for active low.
      """
      assert 0 <= level <= 1
      self._comparator_polarity = level
      self._update_config()

   def set_comparator_latch(self, value):
      """
      Sets whether the ALERT/RDY pin stays active when asserted
      or whether it is cleared automatically if the alert condition
      is no longer present.

      True or non-zero sets latch on, False or 0 sets latch off.
      """
      if value:
         self._comparator_latch = 1
      else:
         self._comparator_latch = 0

      self._update_config()

   def set_comparator_queue(self, queue):
      """
      Sets the number of consecutive alert readings required
      before asserting the ALERT/RDY pin.

      0 for 1 reading
      1 for 2 readings
      2 for 4 readings
      """
      assert 0 <= queue <= 2
      self._set_queue = queue
      self._update_config()

   def set_continuous_mode(self):
      """
      Set continuous conversion mode.
      """
      self._single_shot = 0
      self._update_config()

   def set_single_shot_mode(self):
      """
      Set single-shot conversion mode.
      """
      self._single_shot = 1
      self._update_config()

   def set_sample_rate(self, rate):
      """
      Set the sample rate.

      Any value less than the minimum will set the minimum rate.  Any
      value greater than the maximum will set the maximum rate.

      The ADS1015 supports 128, 250, 490, 920, 1600, 2400, and 3300
      samples per second.

      The ADS1115 supports 8, 16, 32, 64, 128, 250, 475, and 860 samples
      per second.

      The first sample rate greater than or equal to the specified
      value will be set,

      The set samples per second will be returned.
      """
      val = len(self._SPS) - 1
      for i in range(val+1):
         if rate <= self._SPS[i]:
            val = i
            break
      self._sps = val
      self._update_config()
      return self._SPS[val]

   def set_voltage_range(self, vrange):
      """
      Set the voltage range.

      Any value less than the minimum will set the minimum rate.  Any
      value greater than the maximum will set the maximum rate.

      The ADS1015/ADS1115 support voltage ranges 256 mV, 512 mV, 1.024 V,
      2.048 V, 4.096 V, and 6.144 V.

      The first range greater than or equal to the specified value will
      be set,

      The set voltage range will be returned.
      """
      val = len(self._GAIN) - 1
      for i in range(val+1):
         if vrange > self._GAIN[i]:
            val = i
            break
      if val > 0:
         val = val - 1
      self._gain = val
      self._update_comparators()
      self._update_config()
      return self._GAIN[val]

   def set_channel(self, channel):
      """
      Set the channel to be used for conversions.

      May be one of the following constants:

      A0 - single-ended A0
      A1 - single-ended A1
      A2 - single-ended A2
      A3 - single-ended A3

      A0_1 - differential A0 - A1
      A0_3 - differential A0 - A3
      A1_3 - differential A1 - A3
      A2_3 - differential A2 - A3

      Returns the channel set.
      """
      if channel < 0:
         channel = 0
      elif channel > 7:
         channel = 7
      self._channel = channel
      self._update_config()
      return self._CHAN[channel]

   def alert_when_high_clear_when_low(self, vhigh, vlow):
      """
      Set the ALERT/RDY pin to be used as an alert signal.

      The ALERT/RDY pin will be asserted when the voltage goes
      above high.  It will continue to be asserted until the
      voltage drops beneath low.

      This sets continuous coversion mode.

      To be useful your script will have to monitor the
      ALERT/RDY pin and react when it changes level (both
      edges is probably best).
      """
      assert vlow < vhigh

      self._vhigh = vhigh
      self._vlow = vlow

      self._comparator_mode = 0 # traditional
      self._comparator_queue = self._set_queue
      self._alert_rdy = self._AR_ALERT
      self._update_comparators()
      self._single_shot = 0 # must be in continuous mode
      self._update_config()

   def alert_when_high_or_low(self, vhigh, vlow):
      """
      Set the ALERT/RDY pin to be used as an alert signal.

      The ALERT/RDY pin will be asserted when the voltage goes
      above high or drops beneath low.  It will continue to be
      asserted until the voltage is between low to high.

      This sets continuous coversion mode.

      To be useful your script will have to monitor the
      ALERT/RDY pin and react when it changes level (both
      edges is probably best).
      """
      assert vlow < vhigh

      self._vhigh = vhigh
      self._vlow = vlow

      self._comparator_mode = 1 # window
      self._comparator_queue = self._set_queue
      self._alert_rdy = self._AR_ALERT
      self._update_comparators()
      self._single_shot = 0 # must be in continuous mode
      self._update_config()

   def alert_when_ready(self):
      """
      Set the ALERT/RDY pin to be used as a conversion
      complete signal.

      This sets continuous coversion mode.

      To be useful your script will have to monitor the
      ALERT/RDY pin and react when it is asserted (use
      falling edge if comparator polarity is the default 0,
      rising edge if comparator polarity is 1).
      """
      self._write_comparator_thresholds(-1, 1) # conversion alerts
      self._comparator_queue = self._set_queue
      self._alert_rdy = self._AR_READY
      self._single_shot = 0 # must be in continuous mode
      self._update_config()

   def alert_never(self):
      """
      Set the ALERT/RDY pin to unused.
      """
      self._comparator_queue = 3
      self._alert_rdy = self._AR_NEVER
      self._update_config()

   def read(self):
      """
      Returns the last conversion value.  For the ADS1115 this is a
      16-bit quantity,  For the ADS1015 this is a 12-bit quantity.
      The returned ADS1015 value is multiplied by 16 so it has the
      same range as the ADS1115.
      """
      if self._single_shot:
         self._write_config()
  
      (b, d) = self._sbc.i2c_read_device(self._adc, 2)

      return (d[0]<<8) + d[1]

   def read_voltage(self):
      """
      Returns the last conversion value as a voltage.
      """
      return self.read() * self._voltage_range / 32768

   def close(self):
      """
      Releases the resources used by the object.
      """
      self._sbc.i2c_close(self._adc)

class ads1015(_ads1x15):

   _SPS=[128, 250, 490, 920, 1600, 2400, 3300, 3300]

   def __init__(self, sbc, bus, address, flags=0):
      _ads1x15.__init__(self, sbc, bus, address, flags=0)

class ads1115(_ads1x15):

   _SPS=[  8,  16,  32,  64,  128,  250,  475,  860]

   def __init__(self, sbc, bus, address, flags=0):
      _ads1x15.__init__(self, sbc, bus, address, flags=0)


if __name__ == "__main__":

   RGPIO = False # set to True if using rgpio, False if using lgpio

   ALERT_RDY = False # set to True if using ALERT/RDY pin

   import time
   import lg_ads1x15

   if RGPIO:

      import rgpio

      sbc = rgpio.sbc()
      if not sbc.connected:
         exit()

      EDGE = rgpio.FALLING_EDGE

   else:

      import lgpio as sbc

      EDGE = sbc.FALLING_EDGE

   def cbf(chip, gpio, level, tick):
      print(adc.read_voltage())

   if ALERT_RDY:
      ALERT = 21 # set 
      chip = sbc.gpiochip_open(0)
      err = sbc.gpio_claim_alert(chip, ALERT, EDGE)
      if err < 0:
         print("GPIO in use: {} ({})".format(ALERT, sbc.error_text(err)))
         exit()

   adc = lg_ads1x15.ads1015(sbc, 1, 0x48)

   adc.set_voltage_range(3.3)
   adc.set_sample_rate(0) # minimum sampling rate
   adc.set_channel(adc.A0)

   if ALERT_RDY:
      adc.set_comparator_polarity(0)
      cb_id = sbc.callback(chip, ALERT, EDGE, cbf)
      adc.set_comparator_latch(True)
      adc.set_continuous_mode()
      #adc.alert_when_high_clear_when_low(3, 2)
      adc.alert_when_high_or_low(3, 0.3)
      #adc.alert_when_ready()

      time.sleep(120) # run for two minutes

   else:
      end_time = time.time() + 120
      while time.time() < end_time:
         print(adc.read_voltage())
         time.sleep(0.2)

   adc.close()

   if RGPIO:
      sbc.stop()

