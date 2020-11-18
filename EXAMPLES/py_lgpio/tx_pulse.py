#!/usr/bin/env python
"""
tx_pulse.py
2020-11-18
Public Domain

http://abyz.me.uk/lg/py_lgpio.html

./tx_pulse.py
"""

import time
import lgpio as sbc

OUT=21
LOOPS=120

h = sbc.gpiochip_open(0)

sbc.gpio_claim_output(h, OUT)

sbc.tx_pulse(h, OUT, 20000, 30000) # 20 Hz 40 % duty cycle

time.sleep(2)

sbc.tx_pulse(h, OUT, 20000, 5000, pulse_cycles=LOOPS) # 40 Hz 80 %

start = time.time()

while sbc.tx_busy(h, OUT, sbc.TX_PWM):
   time.sleep(0.01)

end = time.time()

print("{} cycles at 40 Hz took {:.1f} seconds".format(LOOPS, end-start))

sbc.gpiochip_close(h)

