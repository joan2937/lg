#!/usr/bin/env python
"""
chipline.py
2020-11-18
Public Domain

http://abyz.me.uk/lg/py_lgpio.html

./chipline.py
"""

import lgpio as sbc

h = sbc.gpiochip_open(0)

ci = sbc.gpio_get_chip_info(h)

print("lines={} name={} label={}".format(ci[1], ci[2], ci[3]))

for i in range(ci[1]):
   li = sbc.gpio_get_line_info(h, i)
   print("offset={} flags={} name={} user={}".format(li[1], li[2], li[3], li[4]))

sbc.gpiochip_close(h)

