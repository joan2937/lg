#!/usr/bin/env python
"""
motor_sync.py
2020-11-30
Public Domain

http://abyz.me.uk/lg/py_rgpio.html

Defines a class to synchronise GPIO devices like motors, servos,
and LEDs.
"""

import time
import threading
import rgpio

class sync:
   """
   A class to send synchronised outputs to output devices.

   Unipolar steppers and servos are specifically supported.

   PWM is supported.

   An adhoc method allows for setting the levels of one or
   more GPIO at set times.
   """

   class _transmit_daemon(threading.Thread):
      """
      A class to buffer waves to be transmitted and
      send them when space becomes available.
      """

      def __init__(self, sbc, chip, leader):
         threading.Thread.__init__(self)
         self._sbc = sbc
         self._chip = chip
         self._leader = leader
         self._pulses = []
         self.daemon = True
         self._busy = True
         self.start()

      def batch(self, pulses):
         self._busy = True
         self._pulses.append(pulses)

      def busy(self):
         return self._busy

      def run(self):
         pulses = []
         while True:
            if len(pulses) > 0:
               while len(pulses) > 0:
                  if self._sbc.tx_room(
                     self._chip, self._leader, rgpio.TX_WAVE) > 0:
                     self._sbc.tx_wave(
                        self._chip, self._leader, pulses[:2700])
                     pulses = pulses[2700:]
                  else:
                     time.sleep(0.2)
            elif len(self._pulses) > 0:
               self._busy = True
               pulses = self._pulses.pop(0)
            else:
               time.sleep(0.2)
               self._busy = False

   class _build_daemon(threading.Thread):
      """
      A class to generate waves from a series of waypoints.
      """
      def __init__(self, devices, sender):
         threading.Thread.__init__(self)
         self.daemon = True
         self._devices = devices
         self._sender = sender
         self._busy = False
         self.start()

      def batch(self):
         self._busy = True

      def busy(self):
         return self._busy

      def run(self):
         gbits = 0
         last_event_time = None
         while True:
            if self._busy:
               pulses = []
               while True:
                  last_next_time = None
                  last_device = []
                  for d in self._devices:
                     next_time  = d.get_next_event_time()
                     if next_time is not None:
                        if last_next_time is not None:
                           if next_time < last_next_time:
                              last_next_time = next_time
                              last_device = [d]
                           elif next_time == last_next_time:
                              last_device.append(d)
                        else:
                           last_next_time = next_time
                           last_device = [d]
                  if last_next_time is None:
                     break
                  if last_event_time is not None:
                     pulses.append(
                        rgpio.pulse(gbits, rgpio.GROUP_ALL,
                           last_next_time - last_event_time))
                  last_event_time = last_next_time
                  for d in last_device:
                     gbits = d.get_next_event(gbits) # or in new bits

               if last_event_time is not None:
                  pulses.append(rgpio.pulse(gbits, rgpio.GROUP_ALL, 0))

               self._sender.batch(pulses)

               last_event_time = None
               self._busy = False
            else:
               time.sleep(0.2)

   class group:
      """
      A class to create a group from all the GPIO needed
      as output.
      """
      def __init__(self):
         self._group = []

      def add(self, GPIO):
         shift = len(self._group)
         mask = (2**len(GPIO))-1
         self._group += GPIO
         return shift, mask

      def group(self):
         return self._group

      def leader(self):
         return self._group[0]

   class adhoc:
      """
      A class to output adhoc timed bits.
      """

      def __init__(self, group, GPIO):
         self._next_event_micros = 1
         self._waypoint_end_micros = 0
         self._waypoints = []
         self._bits = 0
         self._shift, self._mask = group.add(GPIO)

      def get_next_event_time(self):
         if self._next_event_micros <= self._waypoint_end_micros:
            return self._next_event_micros
         if len(self._waypoints) == 0: # reset times for new batch
            self._next_event_micros = 1
            self._waypoint_end_micros = 0
            return None
         micros, self._bits = self._waypoints.pop(0)
         self._waypoint_end_micros += micros
         self._next_event_micros = self._waypoint_end_micros
         return self._next_event_micros

      def get_next_event(self, gbits):
         self._next_event_micros += 1
         return (gbits & ~(self._mask<<self._shift)) | (self._bits<<self._shift)

      def waypoint(self, micros, bits):
         """
         Emit bits on the output at time micros.
         """
         assert micros > 1
         assert bits >= 0 and isinstance(bits, (int))
         self._waypoints.append((int(micros+0.5), bits))      

   class unipolar:
      """
      A class to half step a unipolar stepper.
      """

      on = [9, 8, 12, 4, 6, 2, 3, 1]

      def __init__(self, group, GPIO):
         self._pos = 0
         self._next_event_micros = 1
         self._waypoint_end_micros = 0
         self._waypoints = []
         self._shift, self._mask = group.add(GPIO)

      def get_next_event_time(self):
         if self._next_event_micros <= self._waypoint_end_micros:
            return int(self._next_event_micros+0.5)
         if len(self._waypoints) == 0: # reset times for new batch
            self._next_event_micros = 1
            self._waypoint_end_micros = 0
            return None
         micros, steps = self._waypoints.pop(0)
         if steps < 0:
            self._way = -1
            steps = - steps
         else:
            self._way = 1
         if steps > 0:
            self._inc = 1.0 * micros / steps
            self._next_event_micros = self._waypoint_end_micros + (self._inc / 2.0)
            self._waypoint_end_micros += micros
         else:
            self._waypoint_end_micros += micros
            self._next_event_micros = self._waypoint_end_micros
         return int(self._next_event_micros+0.5)

      def get_next_event(self, gbits):
         if self._next_event_micros < self._waypoint_end_micros:
            self._pos += self._way
            self._next_event_micros += self._inc
            bits = sync.unipolar.on[self._pos%8]
            return (gbits & ~(self._mask<<self._shift)) | (bits<<self._shift)
         else: # consume sleep waypoint
            self._next_event_micros += 1
            return gbits

      def waypoint(self, micros, steps):
         """
         Move steps steps in micros microseconds.
         """
         assert micros > 1
         assert isinstance(steps, (int))
         self._waypoints.append((int(micros+0.5), steps))      

   class servo:
      """
      A class to send servo pulses.
      """

      def __init__(self, group, GPIO, frequency):
         self._pos = 0
         self._next_event_micros = 1
         self._waypoint_end_micros = 0
         self._waypoints = []
         self._period = 1e6 / frequency
         self._width = 0
         self._low = True
         self._shift, self._mask = group.add(GPIO)

      def get_next_event_time(self):
         if self._next_event_micros <= self._waypoint_end_micros:
            return int(self._next_event_micros+0.5)
         if len(self._waypoints) == 0: # reset times for new batch
            self._next_event_micros = 1
            self._waypoint_end_micros = 0
            return None
         micros, width = self._waypoints.pop(0)
         self._waypoint_end_micros += micros
         if width > 0:
            self._width = width
         else:
            self._next_event_micros = self._waypoint_end_micros
         return int(self._next_event_micros+0.5)

      def get_next_event(self, gbits):
         if self._next_event_micros < self._waypoint_end_micros:
            if self._low:
               if self._width:
                  self._low = False
                  bits = 1
                  self._next_event_micros += self._width
               else:
                  bits = 0
                  self._next_event_micros = self._waypoint_end_micros
            else:
               self._low = True
               bits = 0
               self._next_event_micros += (self._period - self._width)
            return (
               gbits & ~(self._mask<<self._shift)) | (bits<<self._shift)
         else: # consume sleep waypoint
            self._next_event_micros += 1
            return gbits

      def waypoint(self, micros, width):
         """
         Generate servo pulses width micros long for
         micros microseconds.
         """
         assert micros > 1
         assert width == 0 or (500 <= width <= 2500)
         self._waypoints.append((int(micros+0.5), int(width+0.5)))      

   class PWM:
      """
      A class to send PWM pulses.
      """

      def __init__(self, group, GPIO, frequency, dutycycle):
         self._pos = 0
         self._next_event_micros = 0.5
         self._waypoint_end_micros = 0
         self._waypoints = []
         self._frequency = frequency
         self._dutycycle = dutycycle
         if frequency:
            self._period = 1e6 / frequency
            self._width = self._period * dutycycle / 100.0
         else:
            self._period = 0
            self._width = 0
         self._low = True
         self._shift, self._mask = group.add(GPIO)

      def get_next_event_time(self):
         if self._next_event_micros <= self._waypoint_end_micros:
            return int(self._next_event_micros+0.5)
         if len(self._waypoints) == 0: # reset times for new batch
            self._next_event_micros = 0.5
            self._waypoint_end_micros = 0
            return None
         micros, frequency, dutycycle = self._waypoints.pop(0)
         if frequency:
            self._period = 1e6 / frequency
            self._width = self._period * dutycycle / 100.0
         else:
            self._width = 0
         self._waypoint_end_micros += micros
         if self._width < 1:
            self._next_event_micros = self._waypoint_end_micros
         return int(self._next_event_micros+0.5)

      def get_next_event(self, gbits):
         if self._next_event_micros < self._waypoint_end_micros:
            if self._low:
               if self._width:
                  self._low = False
                  bits = 1
                  self._next_event_micros += self._width
               else:
                  bits = 0
                  self._next_event_micros = self._waypoint_end_micros
            else:
               self._low = True
               bits = 0
               self._next_event_micros += (self._period - self._width)
            return (
               gbits & ~(self._mask<<self._shift)) | (bits<<self._shift)
         else: # consume sleep waypoint
            self._next_event_micros += 1
            return gbits

      def waypoint(self, micros, frequency, dutycycle):
         """
         Generate PWM pulses at frequency and dutycycle for
         micros microseconds.
         """
         assert micros > 1
         assert 0.0 <= frequency <= 100000.0
         assert 0.0 <= dutycycle <= 100.0
         self._waypoints.append((int(micros+0.5), frequency, dutycycle))      

   def __init__(self, sbc, gpiochip=0):
      """
      Create a sync machine.

      The following steps are required.

      1. sync = motor_sync.sync(sbc)

      2. call one or more setup_() functions to define the
         devices and the GPIO to use.

      3. call setup_complete() when all devices have been
         allocated.

      4. add waypoints for each device to be moved in the
         next period.

      5. call batch() to start transmission

      6. wait until batching() is False (all movements calculated).

      7. If more movements are desired repeat from step 4.

      8. wait till busy() is False (all movements completed).

      9. call finish() to release resources.
      """
      self._sbc = sbc
      self._chip = sbc.gpiochip_open(gpiochip)
      self._group = sync.group()
      self._pulses = []
      self._devices = []

   def setup_unipolar_stepper(self, GPIO):
      """
      Add a unipolar stepper.  Need the four GPIO controlling the
      coils.

      waypoint(micros, steps)

      Move steps steps in micros microseconds (steps may be
      negative).
      """
      self._devices.append(sync.unipolar(self._group, GPIO))
      return self._devices[-1]

   def setup_servo(self, GPIO, frequency=50):
      """
      Add a servo.  Need the GPIO connected to the
      control line.  The pulse frequency may be given
      (default 50 Hz).

      waypoint(micros, width)

      Generate servo pulses width micros long for
      micros microseconds.
      """
      self._devices.append(sync.servo(self._group, [GPIO], frequency))
      return self._devices[-1]

   def setup_PWM(self, GPIO, frequency=0, dutycycle=0):
      """
      Add a PWM output.  Need the GPIO connected to the device.
      The frequency and dutycycle may be given (default to zero).

      waypoint(micros, frequency, dutycycle)

      Generate PWM pulses at frequency and dutycycle for
      micros microseconds.
      """
      self._devices.append(sync.PWM(self._group, [GPIO], frequency, dutycycle))
      return self._devices[-1]

   def setup_adhoc(self, GPIO):
      """
      Add one or more GPIO.  The GPIO will be switched as a unit.

      waypoint(micros, bits)

      Emit bits on the GPIO at time micros.
      """
      if not isinstance(GPIO, (list, tuple)):
         GPIO = [GPIO]
      self._devices.append(sync.adhoc(self._group, GPIO))
      return self._devices[-1]

   def setup_complete(self):
      """
      Call when all the needed GPIO have been assigned to devices
      in the setup_() functions.
      """
      self._sbc.group_claim_output(self._chip, self._group.group())
      self._transmit = sync._transmit_daemon(
         self._sbc, self._chip, self._group.leader())
      self._build = sync._build_daemon(self._devices, self._transmit)

   def batch(self):
      """
      Commits the current waypoints and starts transmission.
      """
      self._build.batch()

   def batching(self):
      """
      Returns True if the current set of waypoints are still being
      processed.
      """
      return self._build.busy()

   def busy(self):
      """
      Returns True if waypoints are still being transmitted.
      """
      return self._build.busy() or self._transmit.busy() or self._sbc.tx_busy(
         self._chip, self._group.leader(), rgpio.TX_WAVE)

   def finish(self):
      """
      Releases resources.
      """
      self._sbc.group_free(self._chip, self._group.leader())
      self._sbc.gpiochip_close(self._chip)

if __name__ == "__main__":

   import time
   import sys
   import rgpio
   import motor_sync

   sbc = rgpio.sbc()
   if not sbc.connected:
      exit()

   sync = motor_sync.sync(sbc) # sbc

   sa = sync.setup_unipolar_stepper([17, 15, 14,  4])
   #sb = sync.setup_unipolar_stepper([18, 27, 22, 23])
   #sc = sync.setup_unipolar_stepper([25,  9, 10, 24])
   #sd = sync.setup_unipolar_stepper([21, 20, 26, 16])
   #se = sync.setup_unipolar_stepper([ 6, 12, 13, 19])

   s1 = sync.setup_servo(5)

   s2 = sync.setup_PWM(7)

   s3 = sync.setup_adhoc([ 2, 3, 8, 11])

   sync.setup_complete() # outputs specified

   for i in range(1):

      # servo
      for j in range(50):
         s1.waypoint(1e6, 500+(j*33))

      s1.waypoint(10e6, 0)

      # PWM

      for j in range(40):
         s2.waypoint(1e6, (j+1)*10, j+10)

      s2.waypoint(20e6, 0, 0)

      # adhoc
      for j in range(60):
         s3.waypoint(1e6, j)

      # unipolar
      sa.waypoint(10e6, +4096) # +4096 steps in 10 seconds
      sa.waypoint(10e6, -4096) # -4096 steps in 10 seconds
      sa.waypoint(20e6, +4096) # +4096 steps in 20 seconds
      sa.waypoint(20e6, -4096) # -4096 steps in 20 seconds

      """
      # unipolar
      sb.waypoint(10e6, -4096) # -4096 steps in 10 seconds
      sb.waypoint(10e6, +4096) # +4096 steps in 10 seconds
      sb.waypoint(20e6, -4096) # -4096 steps in 20 seconds
      sb.waypoint(20e6, +4096) # +4096 steps in 20 seconds

      # unipolar
      for j in range(60):
         sc.waypoint(1e6, j*6)

      # unipolar
      for j in range(60):
         sd.waypoint(1e6, -(j*6))

      # unipolar
      for j in range(30):
         se.waypoint(1e6, j*12)
         se.waypoint(1e6, -(j*12))
      """

      t0 = time.time()

      sync.batch() # batch up the waypoints for output

      while sync.batching(): # don't add new waypoints while batching
         time.sleep(0.001)

      t1 = time.time()

      print("batch took {:.2f} seconds".format(t1-t0))

   while sync.busy(): # keep running while data being written
      time.sleep(0.5)

   sync.finish() # tidy up sync

   sbc.stop() # tidy up rgpio

   print("finished")

