#!/usr/bin/env python
"""
bench.py
2020-11-18
Public Domain

http://abyz.me.uk/lg/py_rgpio.html

./bench.py
"""

import time
import rgpio

OUT=21
LOOPS=2000

sbc = rgpio.sbc()
if not sbc.connected:
   exit()

h = sbc.gpiochip_open(0)

sbc.gpio_claim_output(h, OUT)

t0 = time.time()

for i in range(LOOPS):
   sbc.gpio_write(h, OUT, 0)
   sbc.gpio_write(h, OUT, 1)

t1 = time.time()

sbc.gpiochip_close(h)

print("{:.0f} toggles per second".format(LOOPS/(t1-t0)))

sbc.stop()

