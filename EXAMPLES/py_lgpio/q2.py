import lgpio
import time
import sys

def cbf(chip, gpio, value, tick):
   print("c={} g={} v={} t={}".format(chip, gpio, value, tick))

GPIO=20

if len(sys.argv) > 1:
   GPIO = int(sys.argv[1])

h = lgpio.gpiochip_open(0)

for i in range(20,28):
   lgpio.callback(h, i, lgpio.BOTH_EDGES, cbf)

lgpio.gpio_claim_alert(h, GPIO, lgpio.BOTH_EDGES)

time.sleep(600)

