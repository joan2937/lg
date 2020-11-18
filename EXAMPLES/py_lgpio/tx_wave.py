#!/usr/bin/env python
"""
tx_wave.py
2020-11-18
Public Domain

http://abyz.me.uk/lg/py_lgpio.html

./tx_wave.py
"""

import time
import lgpio as sbc

OUT=[20, 21, 22, 23, 24, 25]

PULSES=500

pulses = []
total = 0
delay = 1000

for i in range(PULSES):
   pulses.append(sbc.pulse(i, sbc.GROUP_ALL, delay))
   total += delay
   delay += 100

h = sbc.gpiochip_open(0)

sbc.group_claim_output(h, OUT)

sbc.tx_wave(h, OUT[0], pulses)

start = time.time()

while sbc.tx_busy(h, OUT[0], sbc.TX_WAVE):
   time.sleep(0.01)

end = time.time()

print("{} pulses took {:.1f} seconds (exp={:.1f})".
   format(PULSES, end-start, total/1e6))

sbc.gpiochip_close(h)

