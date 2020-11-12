#!/usr/bin/env python

import time
import rgpio

OUT=[20, 21, 22, 23, 24, 25]

PULSES=500

sbc = rgpio.sbc()
if not sbc.connected:
   exit()

pulses = []
total = 0
delay = 1000

for i in range(PULSES):
   pulses.append(rgpio.pulse(i, rgpio.GROUP_ALL, delay))
   total += delay
   delay += 100

h = sbc.gpiochip_open(0)

sbc.group_claim_output(h, OUT)

sbc.tx_wave(h, OUT[0], pulses)

start = time.time()

while sbc.tx_busy(h, OUT[0], rgpio.TX_WAVE):
   time.sleep(0.01)

end = time.time()

print("{} pulses took {:.1f} seconds (exp={:.1f})".
   format(PULSES, end-start, total/1e6))

sbc.gpiochip_close(h)

sbc.stop()

