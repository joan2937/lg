#!/usr/bin/env python

import time
import lgpio

IN=20
OUT=21

h = lgpio.gpiochip_open(0)

lgpio.gpio_claim_input(h, 0, IN)
lgpio.gpio_claim_output(h, 0, OUT, 1)

for i in range(1000):
   v = lgpio.gpio_read(h, IN)
   lgpio.gpio_write(h, OUT, v)
   print(v)
   time.sleep(0.1)

lgpio.gpiochip_close(h)

