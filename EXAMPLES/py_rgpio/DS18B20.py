#!/usr/bin/env python
"""
DS18B20.py
2020-11-18
Public Domain

http://abyz.me.uk/lg/py_rgpio.html

./DS18B20.py

This uses the file interface to access the remote file system.

In this case it is used to access the sysfs 1-wire bus interface
to read any connected DS18B20 temperature sensors.

If access control is enabled in the rgpiod daemon the permits
file must contain the following line in the [files] section to
grants read access to DS18B20 device files for the test1 user.

test1=/sys/bus/w1/devices/28*\/w1_slave r
"""

import time
import rgpio

sbc = rgpio.sbc()

if not sbc.connected:
   exit()

sbc.set_user("test1")

while True:

   """
   Get list of connected sensors, handle error rather than the
   default of raising exception if none found.
   """

   rgpio.exceptions = False
   c, files = sbc.file_list("/sys/bus/w1/devices/28-00*/w1_slave")
   rgpio.exceptions = True

   if c >= 0:

      for sensor in files[:-1].split("\n"):

         """
         Typical file name

         /sys/bus/w1/devices/28-000005d34cd2/w1_slave
         """

         devid = sensor.split("/")[5] # Fifth field is the device Id.

         h = sbc.file_open(sensor, rgpio.FILE_READ)
         c, data = sbc.file_read(h, 1000) # 1000 is plenty to read full file.
         sbc.file_close(h)

         """
         Typical file contents

         73 01 4b 46 7f ff 0d 10 41 : crc=41 YES
         73 01 4b 46 7f ff 0d 10 41 t=23187
         """

         if "YES" in data:
            (discard, sep, reading) = data.partition(' t=')
            t = float(reading) / 1000.0
            print("{} {:.1f}".format(devid, t))
         else:
            print("999.9")

   time.sleep(3.0)

