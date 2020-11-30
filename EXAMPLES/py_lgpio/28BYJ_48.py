#!/usr/bin/env python
"""
28BYJ_48.py
2020-11-22
Public Domain

http://abyz.me.uk/lg/py_lgpio.html

./28BYJ_48.py [chip] gpio1 gpio2 gpio3 gpio4

E.g.

./28BYJ_48.py 20 21 22 23 # gpiochip=0 gpio1=20 gpio2=21 gpio3=22 gpio4=23

./28BYJ_48.py 2 7 5 11 3  # gpiochip=2 gpio1=7 gpio2=5 gpio3=11 gpio4=3
"""

class stepper:
   """
   A class to pulse a stepper.
   """

   on = [7, 3, 11, 9, 13, 12, 14, 6]

   def __init__(self, sbc, chip, GPIO):
      """
      """
      self._sbc = sbc
      self._chip = chip
      self._leader = GPIO[0]
      self._pos = 0

      sbc.group_claim_output(chip, GPIO)

   def move(self):

      if self._pos < 0:
         self._pos = 7
      elif self._pos > 7:
         self._pos = 0

      self._sbc.group_write(self._chip, self._leader, stepper.on[self._pos])

   def forward(self):
      self._pos += 1
      self.move()

   def backward(self):
      self._pos -= 1
      self.move()

   def stop(self):
      self._sbc.group_free(self._chip, self._leader)

if __name__ == "__main__":

   import time
   import sys
   import lgpio as sbc

   if len(sys.argv) == 6: # chip gpio1 gpio2 gpio3 gpio4
      chip = int(sys.argv[1])
      gpio1 = int(sys.argv[2])
      gpio2 = int(sys.argv[3])
      gpio3 = int(sys.argv[4])
      gpio4 = int(sys.argv[5])

   elif len(sys.argv) == 5: # gpio1 gpio2 gpio3 gpio4 (chip 0)
      chip = 0
      gpio1 = int(sys.argv[1])
      gpio2 = int(sys.argv[2])
      gpio3 = int(sys.argv[3])
      gpio4 = int(sys.argv[4])

   else:
      print("Usage: ./28BYJ_48.py [chip] gpio1 gpio2 gpio3 gpio4")
      exit()

   chip = sbc.gpiochip_open(0)

   s = stepper(sbc, chip, [gpio1, gpio2, gpio3, gpio4])

   for i in range(4096):
      time.sleep(0.0015)
      s.forward()

   for i in range(4096):
      time.sleep(0.0015)
      s.backward()

   s.stop()

   sbc.gpiochip_close(chip)

