#!/usr/bin/env python
"""
testbed.py
2020-12-31
Public Domain

http://abyz.me.uk/lg/py_lgpio.html

./testbed.py
"""

import time
import lgpio as sbc

MCP23017_1=0x20
MCP23017_2=0x21
NANO=0x2c

DAC_CS=8   # spidev 0.0
ADC_CS=25  # spidev 0.1
NANO_CS=24 # spidev 0.1

chip = sbc.gpiochip_open(0)
sbc.gpio_claim_output(chip, ADC_CS, 1)
sbc.gpio_claim_output(chip, NANO_CS, 1)

dac = sbc.spi_open(0, 0, 50000)
others = sbc.spi_open(0, 1, 50000)

nano_i2c = sbc.i2c_open(1, NANO)

nano_serial = sbc.serial_open("serial0", 115200)

inc = True

potpos = 0

while True:

   while True:

      sbc.spi_write(dac, [0, potpos])

      for i in range(8):
         sbc.gpio_write(chip, ADC_CS, 0)
         (b, d) = sbc.spi_xfer(others, [1, 0x80+(i<<4), 0])
         sbc.gpio_write(chip, ADC_CS, 1)

         if b == 3:
            c1 = d[1] & 0x03
            c2 = d[2]
            ch0 = (c1<<8)+c2
         else:
            ch0 = -1

         print("ADC{}={:4d} pot={}".format(i, ch0, potpos))

      potpos += 1
      if potpos > 129:
         potpos = 0

      sbc.i2c_write_device(nano_i2c, "Hello world!")

      time.sleep(0.1)

      (b, d) = sbc.serial_read(nano_serial, 1000)

      print(d)

      sbc.serial_write(nano_serial, "0random chars\n9")

      time.sleep(0.2)

      (b, d) = sbc.serial_read(nano_serial, 1000)

      print(d)

      sbc.gpio_write(chip, NANO_CS, 0)
      (b, d) = sbc.spi_xfer(others, "A message to SPI\n")
      sbc.gpio_write(chip, NANO_CS, 1)

      time.sleep(0.2)

      (b, d) = sbc.serial_read(nano_serial, 1000)

      print(d)

