#!/usr/bin/env python

import time
import lgpio

cinfo=lgpio.chip_info()
linfo=lgpio.line_info()

h = lgpio.gpiochip_open(0)

lgpio.get_chip_info(h, cinfo)
print(cinfo.lines, cinfo.name, cinfo.label)

for i in range(cinfo.lines):
   lgpio.get_line_info(h, i, linfo)
   print(linfo.offset, linfo.lFlags, linfo.name, linfo.user)

lgpio.gpiochip_close(h)

