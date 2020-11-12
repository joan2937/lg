#!/usr/bin/env python

import time
import lgpio

OUT=21
LOOPS=100000

h = lgpio.gpiochip_open(0)

lgpio.gpio_claim_output(h, OUT)

t0 = time.time()

for i in range(LOOPS):
   lgpio.gpio_write(h, OUT, 0)
   lgpio.gpio_write(h, OUT, 1)

t1 = time.time()

lgpio.gpiochip_close(h)

print("{:.0f} toggles per second".format(LOOPS/(t1-t0)))

