import os
import socket
import struct
import sys
import threading
import time

LGPIO_PY_VERSION = 0x00010001

exceptions = True

# GPIO levels

OFF = 0
LOW = 0
CLEAR = 0

ON = 1
HIGH = 1
SET = 1

TIMEOUT = 2

GROUP_ALL = 0xffffffffffffffff

# GPIO line flags

SET_ACTIVE_LOW = 4
SET_OPEN_DRAIN = 8
SET_OPEN_SOURCE = 16
SET_BIAS_PULL_UP = 32
SET_BIAS_PULL_DOWN = 64
SET_BIAS_DISABLE = 128

# GPIO event flags

RISING_EDGE = 1
FALLING_EDGE = 2
BOTH_EDGES = 3

# tx constants

TX_PWM = 0
TX_WAVE = 1

SPI_MODE_0 = 0
SPI_MODE_1 = 1
SPI_MODE_2 = 2
SPI_MODE_3 = 3

# lgpio error numbers

OKAY = 0
INIT_FAILED = -1
BAD_MICROS = -2
BAD_PATHNAME = -3
NO_HANDLE = -4
BAD_HANDLE = -5
BAD_SOCKET_PORT = -6
NOT_PERMITTED = -7
SOME_PERMITTED = -8
BAD_SCRIPT = -9
BAD_TX_TYPE = -10
GPIO_IN_USE = -11
BAD_PARAM_NUM = -12
DUP_TAG = -13
TOO_MANY_TAGS = -14
BAD_SCRIPT_CMD = -15
BAD_VAR_NUM = -16
NO_SCRIPT_ROOM = -17
NO_MEMORY = -18
SOCK_READ_FAILED = -19
SOCK_WRIT_FAILED = -20
TOO_MANY_PARAM = -21
SCRIPT_NOT_READY = -22
BAD_TAG = -23
BAD_MICS_DELAY = -24
BAD_MILS_DELAY = -25
I2C_OPEN_FAILED = -26
SERIAL_OPEN_FAILED = -27
SPI_OPEN_FAILED = -28
BAD_I2C_BUS = -29
BAD_I2C_ADDR = -30
BAD_SPI_CHANNEL = -31
BAD_I2C_FLAGS = -32
BAD_SPI_FLAGS = -33
BAD_SERIAL_FLAGS = -34
BAD_SPI_SPEED = -35
BAD_SERIAL_DEVICE = -36
BAD_SERIAL_SPEED = -37
BAD_FILE_PARAM = -38
BAD_I2C_PARAM = -39
BAD_SERIAL_PARAM = -40
I2C_WRITE_FAILED = -41
I2C_READ_FAILED = -42
BAD_SPI_COUNT = -43
SERIAL_WRITE_FAILED = -44
SERIAL_READ_FAILED = -45
SERIAL_READ_NO_DATA = -46
UNKNOWN_COMMAND = -47
SPI_XFER_FAILED = -48
BAD_POINTER = -49
MSG_TOOBIG = -50
BAD_MALLOC_MODE = -51
TOO_MANY_SEGS = -52
BAD_I2C_SEG = -53
BAD_SMBUS_CMD = -54
BAD_I2C_WLEN = -55
BAD_I2C_RLEN = -56
BAD_I2C_CMD = -57
FILE_OPEN_FAILED = -58
BAD_FILE_MODE = -59
BAD_FILE_FLAG = -60
BAD_FILE_READ = -61
BAD_FILE_WRITE = -62
FILE_NOT_ROPEN = -63
FILE_NOT_WOPEN = -64
BAD_FILE_SEEK = -65
NO_FILE_MATCH = -66
NO_FILE_ACCESS = -67
FILE_IS_A_DIR = -68
BAD_SHELL_STATUS = -69
BAD_SCRIPT_NAME = -70
CMD_INTERRUPTED = -71
BAD_EVENT_REQUEST = -72
BAD_GPIO_NUMBER = -73
BAD_GROUP_SIZE = -74
BAD_LINEINFO_IOCTL = -75
BAD_READ = -76
BAD_WRITE = -77
CANNOT_OPEN_CHIP = -78
GPIO_BUSY = -79
GPIO_NOT_ALLOCATED = -80
NOT_A_GPIOCHIP = -81
NOT_ENOUGH_MEMORY = -82
POLL_FAILED = -83
TOO_MANY_GPIOS = -84
UNEGPECTED_ERROR = -85
BAD_PWM_MICROS = -86
NOT_GROUP_LEADER = -87
SPI_IOCTL_FAILED = -88
BAD_GPIOCHIP = -89
BAD_CHIPINFO_IOCTL = -90
BAD_CONFIG_FILE = -91
BAD_CONFIG_VALUE = -92
NO_PERMISSIONS = -93
BAD_USERNAME = -94
BAD_SECRET = -95
TX_QUEUE_FULL = -96
BAD_CONFIG_ID = -97
BAD_DEBOUNCE_MICS = -98
BAD_WATCHDOG_MICS = -99
BAD_SERVO_FREQ = -100
BAD_SERVO_WIDTH = -101
BAD_PWM_FREQ = -102
BAD_PWM_DUTY = -103
GPIO_NOT_AN_OUTPUT = -104
INVALID_GROUP_ALERT = -105

class error(Exception):
   """
   rgpio module exception
   """
   def __init__(self, value):
      self.value = value
   def __str__(self):
      return repr(self.value)

class pulse:
   """
   A class to store pulse information.
   """

   def __init__(self, group_bits, group_mask, pulse_delay):
      """
      Initialises a pulse.

      group_bits:= the levels to set if the corresponding bit in
                   group_mask is set.
      group_mask:= a mask indicating the group GPIO to be updated.
           delay:= the delay in microseconds before the next pulse.
      """
      self.group_bits = group_bits
      self.group_mask = group_mask
      self.pulse_delay = pulse_delay

def _tobuf(x):
   if isinstance(x, (bytes, bytearray)):
      return x
   elif isinstance(x, (str)):
      return x.encode('latin-1')
   elif isinstance(x, (list, tuple)):
      return bytearray(x)
   else:
      raise error("can't convert to bytes")

def u2i(uint32):
   """
   Converts a 32 bit unsigned number to signed.

   uint32:= an unsigned 32 bit number

   Returns a signed number.

   ...
   print(u2i(4294967272))
   -24
   print(u2i(37))
   37
   ...
   """
   mask = (2 ** 32) - 1
   if uint32 & (1 << 31):
      v = uint32 | ~mask
   else:
      v = uint32 & mask
   return v

def _u2i(status):
   """
   If the status is negative it indicates an error.  On error
   a lgpio exception will be raised if exceptions is True.
   """
   v = u2i(status)
   if v < 0:
      if exceptions:
         raise error(error_text(v))
   return v

def _u2i_list(lst):
   """
   Checks a returned list.  The first member is the status.
   If the status is negative it indicates an error.  On error
   a lgpio exception will be raised if exceptions is True.
   """
   lst[0] = u2i(lst[0])
   if lst[0] < 0:
      if exceptions:
         raise error(error_text(lst[0]))
   return lst

class _callback_ADT:
   """
   A class to hold callback information.
   """

   def __init__(self, gpiochip, gpio, edge, func):
      """
      Initialises a callback.

      gpiochip:= gpiochip device number.
          gpio:= gpio number in device.
          edge:= BOTH_EDGES, RISING_EDGE, or FALLING_EDGE.
          func:= a user function taking four arguments
                 (gpiochip, gpio, level, tick).
      """
      self.chip = gpiochip
      self.gpio = gpio
      self.edge = edge
      self.func = func

class _callback_thread(threading.Thread):
   """
   A class to encapsulate lgpio notification callbacks.
   """

   def __init__(self):
      """
      Initialises notifications.
      """
      threading.Thread.__init__(self)
      self._notify = _lgpio._notify_open()
      self._file = open('.lgd-nfy{}'.format(self._notify), 'rb')
      self.go = False
      self.daemon = True
      self.callbacks = []
      self.go = True
      self.start()

   def stop(self):
      """
      Stops notifications.
      """
      if self.go:
         self.go = False

   def append(self, callb):
      """
      Adds a callback to the notification thread.
      """
      self.callbacks.append(callb)

   def remove(self, callb):
      """
      Removes a callback from the notification thread.
      """
      if callb in self.callbacks:
         self.callbacks.remove(callb)

   def run(self):
      """
      Runs the notification thread.
      """

      RECV_SIZ = 16
      MSG_SIZ = 16 # 4 bytes of padding in each message

      buf = bytes()
      while self.go:

         buf += self._file.read(RECV_SIZ)
         offset = 0

         while self.go and (len(buf) - offset) >= MSG_SIZ:
            msgbuf = buf[offset:offset + MSG_SIZ]
            offset += MSG_SIZ
            tick, chip, gpio, level, flags, pad = (
               struct.unpack('QBBBBI', msgbuf))

            if flags == 0:
               for cb in self.callbacks:
                  if cb.chip == chip and cb.gpio == gpio:
                     cb.func(chip, gpio, level, tick)
            else: # no flags currently defined, ignore.
               pass

         buf = buf[offset:]

      self._file.close()

_notify_thread = _callback_thread()

class _callback:
   """
   A class to provide GPIO level change callbacks.
   """

   def __init__(self, chip, gpio, edge=RISING_EDGE, func=None):
      """
      Initialise a callback and adds it to the notification thread.
      """
      self.count=0
      self._reset = False
      if func is None:
         func=self._tally
      self.callb = _callback_ADT(chip, gpio, edge, func)
      _notify_thread.append(self.callb)

   def cancel(self):
      """
      Cancels a callback by removing it from the notification thread.
      """
      _notify_thread.remove(self.callb)

   def _tally(self, chip, gpio, level, tick):
      """
      Increment the callback called count.
      """
      if self._reset:
         self._reset = False
         self.count = 0
      self.count += 1

   def tally(self):
      """
      """
      return self.count

   def reset_tally(self):
      """
      """
      self._reset = True
      self.count = 0

def get_module_version():
   """
   Returns the version number of the lgpio Python module as a dotted
   quad.

   A.B.C.D
   
   A. API major version, changed if breaks previous API 
   B. API minor version, changed when new function added 
   C. bug fix 
   D. documentation change
   """
   return "lgpio.py_{}.{}.{}.{}".format(
      (LGPIO_PY_VERSION>>24)&0xff, (LGPIO_PY_VERSION>>16)&0xff,
      (LGPIO_PY_VERSION>>8)&0xff, LGPIO_PY_VERSION&0xff)

# GPIO

def gpiochip_open(gpiochip):
   """
   This returns a handle to a gpiochip device.

   gpiochip:= >= 0

   If OK returns a handle (>= 0).

   On failure returns a negative error code.

   ...
   h = gpiochip_open(0) # open /dev/gpiochip0
   if h >= 0:
      open okay
   else:
      open error
   ...
   """
   handle = u2i(_lgpio._gpiochip_open(gpiochip))
   if handle >= 0:
      handle = handle | (gpiochip << 16)
   return _u2i(handle)

def gpiochip_close(handle):
   """
   This closes a gpiochip device.

   handle:= >= 0 (as returned by [*gpiochip_open*]).

   If OK returns 0.

   On failure returns a negative error code.

   ...
   sbc.gpiochip_close(h)
   ...
   """
   return _u2i(_lgpio._gpiochip_close(handle&0xffff))

def gpio_get_chip_info(handle):
   """
   This returns summary information of an opened gpiochip.

   handle:= >= 0 (as returned by [*gpiochip_open*]).

   If OK returns a list of okay status, number of
   lines, name, and label.

   On failure returns a negative error code.
   """
   return _u2i_list(_lgpio._gpio_get_chip_info(handle&0xffff))


def gpio_get_line_info(handle, gpio):
   """
   This returns detailed information of a GPIO of
   an opened gpiochip.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
     gpio:= the GPIO.

   If OK returns a list of okay status, GPIO number,
   line flags, name, and user.

   On failure returns a negative error code.
   """
   return _u2i_list(_lgpio._gpio_get_line_info(handle&0xffff, gpio))


def gpio_get_mode(handle, gpio):
   """
   This returns the mode of a GPIO.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
     gpio:= the GPIO.

   If OK returns the mode of the GPIO.

   On failure returns a negative error code.

   Mode bit @ Value @ Meaning
   0        @  1    @ Kernel: In use by the kernel
   1        @  2    @ Kernel: Output
   2        @  4    @ Kernel: Active low
   3        @  8    @ Kernel: Open drain
   4        @ 16    @ Kernel: Open source
   5        @ 32    @ Kernel: Pulled up bias
   6        @ 64    @ Kernel: Pulled down bias
   7        @ 128   @ Kernel: No bias
   8        @ 256   @ LG: Input
   9        @ 512   @ LG: Output
   10       @ 1024  @ LG: Alert
   11       @ 2048  @ LG: Group
   12       @ 4096  @ LG: ---
   13       @ 8192  @ LG: ---
   14       @ 16384 @ LG: ---
   15       @ 32768 @ LG: ---
   """
   return _u2i(_lgpio._gpio_get_mode(handle&0xffff, gpio))


def gpio_claim_input(handle, gpio, lFlags=0):
   """
   This claims a GPIO for input.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
     gpio:= the GPIO to be claimed.
   lFlags:= line flags for the GPIO.

   If OK returns 0.

   On failure returns a negative error code.

   The line flags may be used to set the GPIO
   as active low, open drain, open source,
   or to enable or disable a bias on the pin.

   ...
   sbc.gpio_claim_input(h, 23) # open GPIO 23 for input.
   ...
   """
   return _u2i(_lgpio._gpio_claim_input(handle&0xffff, lFlags, gpio))

def gpio_claim_output(handle, gpio, level=0, lFlags=0):
   """
   This claims a GPIO for output.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
     gpio:= the GPIO to be claimed.
    level:= the initial value for the GPIO.
   lFlags:= line flags for the GPIO.

   If OK returns 0.

   On failure returns a negative error code.

   The line flags may be used to set the GPIO
   as active low, open drain, or open source.

   If level is zero the GPIO will be initialised low (0).  If any other
   value is used the GPIO will be initialised high (1).

   ...
   sbc.gpio_claim_output(h, 3) # open GPIO 3 for low output.
   ...
   """
   return _u2i(_lgpio._gpio_claim_output(handle&0xffff, lFlags, gpio, level))

def gpio_free(handle, gpio):
   """
   This frees a GPIO.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
     gpio:= the GPIO to be freed.

   If OK returns 0.

   On failure returns a negative error code.

   The GPIO may now be claimed by another user or for
   a different purpose.
   """
   return _u2i(_lgpio._gpio_free(handle&0xffff, gpio))

def group_claim_input(handle, gpio, lFlags=0):
   """
   This claims a group of GPIO for inputs.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
    gpios:= a list of GPIO to be claimed.
   lFlags:= line flags for the group of GPIO.

   If OK returns 0.

   On failure returns a negative error code.

   The line flags may be used to set the group
   as active low, open drain, open source,
   or to enable or disable a bias on the pin.

   gpio is a list of one or more GPIO.  The first GPIO in the
   list is called the group leader and is used to reference the
   group as a whole.

   """
   if len(gpio):
      GPIO = bytearray()
      for g in gpio:
         GPIO.extend(struct.pack("I", g))
      return _u2i(_lgpio._group_claim_input(handle&0xffff, lFlags, GPIO))
   else:
      return 0

def group_claim_output(handle, gpio, levels=[0], lFlags=0):
   """
   This claims a group of GPIO for outputs.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
     gpio:= a list of GPIO to be claimed.
   levels:= a list of the initial value for each GPIO.
   lFlags:= line flags for the group of GPIO.

   If OK returns 0.

   On failure returns a negative error code.

   The line flags may be used to set the group
   as active low, open drain, or open source.

   gpio is a list of one or more GPIO.  The first GPIO in the list is
   called the group leader and is used to reference the group as a whole.

   levels is a list of initialisation values for the GPIO. If a value is
   zero the corresponding GPIO will be initialised low (0).  If any other
   value is used the corresponding GPIO will be initialised high (1).

   """
   if len(gpio):
      diff = len(gpio)-len(levels)
      if diff > 0:
         levels = levels + [0]*diff

      GPIO = bytearray()
      for g in gpio:
         GPIO.extend(struct.pack("I", g))

      LEVELS = bytearray()
      for l in levels:
         LEVELS.extend(struct.pack("I", l))

      return _u2i(_lgpio._group_claim_output(
         handle&0xffff, lFlags, GPIO, LEVELS))
   else:
      return 0

def group_free(handle, gpio):
   """
   This frees all the GPIO associated with a group.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
     gpio:= the group leader.

   If OK returns 0.

   On failure returns a negative error code.

   The GPIO may now be claimed by another user or for a different purpose.

   """
   return _u2i(_lgpio._group_free(handle&0xffff, gpio))

def gpio_read(handle, gpio):
   """
   This returns the level of a GPIO.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
     gpio:= the GPIO to be read.

   If OK returns 0 (low) or 1 (high).

   On failure returns a negative error code.

   This command will work for any claimed GPIO (even if a member
   of a group).  For an output GPIO the value returned
   will be that last written to the GPIO.

   """
   return _u2i(_lgpio._gpio_read(handle&0xffff, gpio))

def gpio_write(handle, gpio, level):
   """
   This sets the level of an output GPIO.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
     gpio:= the GPIO to be written.
    level:= the value to write.

   If OK returns 0.

   On failure returns a negative error code.

   This command will work for any GPIO claimed as an output
   (even if a member of a group).

   If level is zero the GPIO will be set low (0).
   If any other value is used the GPIO will be set high (1).

   """
   return _u2i(_lgpio._gpio_write(handle&0xffff, gpio, level))


def group_read(handle, gpio):
   """
   This returns the levels read from a group.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
     gpio:= the group to be read.

   If OK returns a list of group size and levels.

   On failure returns a list of negative error code and a dummy.

   This command will work for an output group as well as an input
   group.  For an output group the value returned
   will be that last written to the group GPIO.

   Note that this command will also work on an individual GPIO claimed
   as an input or output as that is treated as a group with one member.

   After a successful read levels is set as follows.

   Bit 0 is the level of the group leader. 
   Bit 1 is the level of the second GPIO in the group. 
   Bit x is the level of GPIO x+1 of the group.

   """
   return _u2i_list(_lgpio._group_read(handle&0xffff, gpio))

def group_write(handle, gpio, group_bits, group_mask=GROUP_ALL):
   """
   This sets the levels of an output group.

       handle:= >= 0 (as returned by [*gpiochip_open*]).
         gpio:= the group to be written.
   group_bits:= the level to set if the corresponding bit in
                group_mask is set.
   group_mask:= a mask indicating the group GPIO to be updated.

   If OK returns 0.

   On failure returns a negative error code.

   The values of each GPIO of the group are set according to the bits 
   of group_bits.

   Bit 0 sets the level of the group leader. 
   Bit 1 sets the level of the second GPIO in the group. 
   Bit x sets the level of GPIO x+1 in the group.

   However this may be overridden by the group_mask.  A GPIO is only
   updated if the corresponding bit in the mask is 1.

   """
   return _u2i(_lgpio._group_write(
      handle&0xffff, gpio, group_bits, group_mask))


def tx_pulse(handle, gpio,
   pulse_on, pulse_off, pulse_offset=0, pulse_cycles=0):
   """
   This starts software timed pulses on an output GPIO.

         handle:= >= 0 (as returned by [*gpiochip_open*]).
           gpio:= the GPIO to be pulsed.
       pulse_on:= pulse high time in microseconds.
      pulse_off:= pulse low time in microsseconds.
   pulse_offset:= offset from nominal pulse start position.
   pulse_cycles:= the number of cycles to be sent, 0 for infinite.

   If OK returns the number of entries left in the PWM queue for the GPIO.

   On failure returns a negative error code.

   If both pulse_on and pulse_off are zero pulses will be
   switched off for that GPIO.  The active pulse, if any,
   will be stopped and any queued pulses will be deleted.

   Each successful call to this function consumes one PWM queue entry.

   pulse_cycles cycles are transmitted (0 means infinite).  Each
   cycle consists of pulse_on microseconds of GPIO high followed by
   pulse_off microseconds of GPIO low.

   PWM is characterised by two values, its frequency (number of cycles
   per second) and its dutycycle (percentage of high time per cycle).

   The set frequency will be 1000000 / (pulse_on + pulse_off) Hz.

   The set dutycycle will be pulse_on / (pulse_on + pulse_off) * 100 %.

   E.g. if pulse_on is 50 and pulse_off is 100 the frequency will be
   6666.67 Hz and the dutycycle will be 33.33 %.

   pulse_offset is a microsecond offset from the natural start of
   the pulse cycle.

   For instance if the PWM frequency is 10 Hz the natural start of each
   cycle is at seconds 0, then 0.1, 0.2, 0.3 etc.  In this case if
   the offset is 20000 microseconds the cycle will start at seconds
   0.02, 0.12, 0.22, 0.32 etc.

   Another pulse command may be issued to the GPIO before the last
   has finished.

   If the last pulse had infinite cycles (pulse_cycles of 0) then it
   will be replaced by the new settings at the end of the current
   cycle.  Otherwise it will be replaced by the new settings at
   the end of pulse_cycles cycles.

   Multiple pulse settings may be queued in this way.

   """
   return _u2i(_lgpio._tx_pulse(
      handle&0xffff, gpio, pulse_on, pulse_off, pulse_offset, pulse_cycles))


def tx_pwm(handle, gpio,
   pwm_frequency, pwm_duty_cycle, pulse_offset=0, pulse_cycles=0):
   """
   This starts software timed PWM on an output GPIO.

            handle:= >= 0 (as returned by [*gpiochip_open*]).
              gpio:= the GPIO to be pulsed.
     pwm_frequency:= PWM frequency in Hz (0=off, 0.1-10000).
    pwm_duty_cycle:= PWM duty cycle in % (0-100).
     pulse_offset:= offset from nominal pulse start position.
     pulse_cycles:= the number of cycles to be sent, 0 for infinite.

   If OK returns the number of entries left in the PWM queue for the GPIO.

   On failure returns a negative error code.

   Each successful call to this function consumes one PWM queue entry.

   pulse_cycles cycles are transmitted (0 means infinite).

   PWM is characterised by two values, its frequency (number of cycles
   per second) and its dutycycle (percentage of high time per cycle).

   pulse_offset is a microsecond offset from the natural start of
   the pulse cycle.

   For instance if the PWM frequency is 10 Hz the natural start of each
   cycle is at seconds 0, then 0.1, 0.2, 0.3 etc.  In this case if
   the offset is 20000 microseconds the cycle will start at seconds
   0.02, 0.12, 0.22, 0.32 etc.

   Another PWM command may be issued to the GPIO before the last
   has finished.

   If the last pulse had infinite cycles then it will be replaced by
   the new settings at the end of the current cycle. Otherwise it will
   be replaced by the new settings when all its cycles are complete.

   Multiple pulse settings may be queued in this way.

   """
   return _u2i(_lgpio._tx_pwm(
      handle&0xffff, gpio, pwm_frequency, pwm_duty_cycle,
      pulse_offset, pulse_cycles))


def tx_servo(handle, gpio, pulse_width,
   servo_frequency=50, pulse_offset=0, pulse_cycles=0):
   """
   This starts software timed servo pulses on an output GPIO.

   I would only use software timed servo pulses for testing
   purposes.  The timing jitter will cause the servo to fidget.
   This may cause it to overheat and wear out prematurely.

            handle:= >= 0 (as returned by [*gpiochip_open*]).
              gpio:= the GPIO to be pulsed.
       pulse_width:= pulse high time in microseconds (0=off, 500-2500).
   servo_frequency:= the number of pulses per second (40-500).
      pulse_offset:= offset from nominal pulse start position.
      pulse_cycles:= the number of cycles to be sent, 0 for infinite.

   If OK returns the number of entries left in the PWM queue for the GPIO.

   On failure returns a negative error code.

   Each successful call to this function consumes one PWM queue entry.

   pulse_cycles cycles are transmitted (0 means infinite).

   pulse_offset is a microsecond offset from the natural start of
   the pulse cycle.

   Another servo command may be issued to the GPIO before the last
   has finished.

   If the last pulse had infinite cycles then it will be replaced by
   the new settings at the end of the current cycle. Otherwise it will
   be replaced by the new settings when all its cycles are compete.

   Multiple servo settings may be queued in this way.

   """
   return _u2i(_lgpio._tx_servo(
      handle&0xffff, gpio, pulse_width, servo_frequency,
      pulse_offset, pulse_cycles)
)


def tx_wave(handle, gpio, pulses):
   """
   This starts a software timed wave on an output group.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
     gpio:= the group to be pulsed.
   pulses:= the pulses to transmit.

   If OK returns the number of entries left in the wave queue
   for the group.

   On failure returns a negative error code.

   Each successful call to this function consumes one wave queue entry.

   This command starts a wave of pulses.

   pulses is an array of pulses to be transmitted on the group.

   Each pulse is defined by the following triplet:

   bits:  the levels to set for the selected GPIO 
   mask:  the GPIO to select 
   delay: the delay in microseconds before the next pulse

   Another wave command may be issued to the group before the
   last has finished transmission. The new wave will start when
   the previous wave has competed.

   Multiple waves may be queued in this way.

   """
   if len(pulses):
      PULSES = bytearray()
      for p in pulses:
         PULSES.extend(struct.pack(
            "QQQ", p.group_bits, p.group_mask, p.pulse_delay))
      return _u2i(_lgpio._tx_wave(handle&0xffff, gpio, PULSES)
)
   else:
      return 0


def tx_busy(handle, gpio, kind):
   """
   This returns true if transmissions of the specified kind
   are active on the GPIO or group.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
     gpio:= the GPIO or group to be checked.
     kind:= TX_PWM or TX_WAVE.

   If OK returns 1 for busy and 0 for not busy.

   On failure returns a negative error code.

   """
   return _u2i(_lgpio._tx_busy(handle&0xffff, gpio, kind))

def tx_room(handle, gpio, kind):
   """
   This returns the number of slots there are to queue further
   transmissions of the specified kind on a GPIO or group.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
     gpio:= the GPIO or group to be checked.
     kind:= TX_PWM or TX_WAVE.

   If OK returns the number of free entries (0 for none).

   On failure returns a negative error code.

   """
   return _u2i(_lgpio._tx_room(handle&0xffff, gpio, kind))

def gpio_set_debounce_micros(handle, gpio, debounce_micros):
   """
   This sets the debounce time for a GPIO.

            handle:= >= 0 (as returned by [*gpiochip_open*]).
              gpio:= the GPIO to be configured.
   debounce_micros:= the value to set.

   If OK returns 0.

   On failure returns a negative error code.

   This only affects alerts.

   An alert will only be issued if the edge has been stable for
   at least debounce microseconds.

   Generally this is used to debounce mechanical switches
   (e.g. contact bounce).

   Suppose that a square wave at 5 Hz is being generated on a GPIO.
   Each edge will last 100000 microseconds.  If a debounce time
   of 100001 is set no alerts will be generated,  If a debounce
   time of 99999 is set 10 alerts will be generated per second.

   Note that level changes will be timestamped debounce microseconds
   after the actual level change.

   """
   return _u2i(_lgpio._gpio_set_debounce_micros(
      handle&0xffff, gpio, debounce_micros))


def gpio_set_watchdog_micros(handle, gpio, watchdog_micros):
   """
   This sets the watchdog time for a GPIO.

            handle:= >= 0 (as returned by [*gpiochip_open*]).
              gpio:= the GPIO to be configured.
   watchdog_micros:= the value to set.

   If OK returns 0.

   On failure returns a negative error code.

   This only affects alerts.

   A watchdog alert will be sent if no edge alert has been issued
   for that GPIO in the previous watchdog microseconds.

   Note that only one watchdog alert will be sent per stream of
   edge alerts.  The watchdog is reset by the sending of a new
   edge alert.

   The level is set to TIMEOUT (2) for a watchdog alert.
   """
   return _u2i(_lgpio._gpio_set_watchdog_micros(
      handle&0xffff, gpio, watchdog_micros))


def gpio_claim_alert(
   handle, gpio, eFlags, lFlags=0, notify_handle=None):
   """
   This claims a GPIO to be used as a source of alerts on level changes.

           handle:= >= 0 (as returned by [*gpiochip_open*]).
             gpio:= >= 0, as legal for the gpiochip.  
           eFlags:= event flags for the GPIO.
           lFlags:= line flags for the GPIO.
   notifiy_handle:= >=0 (as returned by [*notify_open*]).

   If OK returns 0.

   On failure returns a negative error code.

   The event flags are used to generate alerts for a rising edge,
   falling edge, or both edges.

   The line flags may be used to set the GPIO
   as active low, open drain, open source,
   or to enable or disable a bias on the pin.

   Use the default notification handle of None unless you plan
   to read the alerts from a notification pipe you have opened.

   """
   if notify_handle is None:
      notify_handle = _notify_thread._notify
   return _u2i(_lgpio._gpio_claim_alert(
      handle&0xffff, lFlags, eFlags, gpio, notify_handle))

def callback(handle, gpio, edge=RISING_EDGE, func=None):
   """
   Calls a user supplied function (a callback) whenever the
   specified GPIO edge is detected.

   handle:= >= 0 (as returned by [*gpiochip_open*]).
     gpio:= >= 0, as legal for the gpiochip.  
     edge:= BOTH_EDGES, RISING_EDGE (default), or FALLING_EDGE.
     func:= user supplied callback function.

   Returns a callback instance.

   The user supplied callback receives four parameters, the chip,
   the GPIO, the level, and the timestamp.

   The reported level will be one of

   0: change to low (a falling edge) 
   1: change to high (a rising edge) 
   2: no level change (a watchdog timeout)

   The timestamp is when the change happened reported as the
   number of nanoseconds since the epoch (start of 1970).

   If a user callback is not specified a default tally callback is
   provided which simply counts edges.  The count may be retrieved
   by calling the callback instance's tally() method.  The count may
   be reset to zero by calling the callback instance's reset_tally()
   method.

   The callback may be cancelled by calling the callback
   instance's cancel() method.

   A GPIO may have multiple callbacks (although I can't think of
   a reason to do so).

   If you want to track the level of more than one GPIO do so by
   maintaining the state in the callback.  Do not use [*gpio_read*].
   Remember the alert that triggered the callback may have
   happened several milliseconds before and the GPIO may have
   changed level many times since then.

   ...
   def cbf(chip, gpio, level, timestamp):
      print(chip, gpio, level, timestamp)

   cb1 = sbc.callback(0, 22, lgpio.BOTH_EDGES, cbf)

   cb2 = sbc.callback(0, 4, lgpio.BOTH_EDGES)

   cb3 = sbc.callback(0, 17)

   print(cb3.tally())

   cb3.reset_tally()

   cb1.cancel() # To cancel callback cb1.
   ...
   """
   return _callback(handle>>16, gpio, edge, func)


# I2C

def i2c_open(i2c_bus, i2c_address, i2c_flags=0):
   """
   Returns a handle (>= 0) for the device at the I2C bus address.

       i2c_bus:= >= 0.
   i2c_address:= 0-0x7F.
     i2c_flags:= 0, no flags are currently defined.

   If OK returns a handle (>= 0).

   On failure returns a negative error code.

   For the SMBus commands the low level transactions are shown
   at the end of the function description.  The following
   abbreviations are used:

   . .
   S     (1 bit) : Start bit
   P     (1 bit) : Stop bit
   Rd/Wr (1 bit) : Read/Write bit. Rd equals 1, Wr equals 0.
   A, NA (1 bit) : Accept and not accept bit.
   Addr  (7 bits): I2C 7 bit address.
   reg   (8 bits): Command byte, which often selects a register.
   Data  (8 bits): A data byte.
   Count (8 bits): A byte defining the length of a block operation.

   [..]: Data sent by the device.
   . .

   ...
   h = sbc.i2c_open(1, 0x53) # open device at address 0x53 on bus 1
   ...
   """
   return _u2i(_lgpio._i2c_open(i2c_bus, i2c_address, i2c_flags))

def i2c_close(handle):
   """
   Closes the I2C device.

   handle:= >= 0 (as returned by [*i2c_open*]).

   If OK returns 0.

   On failure returns a negative error code.

   ...
   sbc.i2c_close(h)
   ...
   """
   return _u2i(_lgpio._i2c_close(handle))

def i2c_write_quick(handle, bit):
   """
   Sends a single bit to the device.

   handle:= >= 0 (as returned by [*i2c_open*]).
      bit:= 0 or 1, the value to write.

   If OK returns 0.

   On failure returns a negative error code.

   SMBus 2.0 5.5.1 - Quick command.
   . .
   S Addr bit [A] P
   . .

   ...
   sbc.i2c_write_quick(0, 1) # send 1 to handle 0
   sbc.i2c_write_quick(3, 0) # send 0 to handle 3
   ...
   """
   return _u2i(_lgpio._i2c_write_quick(handle, bit))

def i2c_write_byte(handle, byte_val):
   """
   Sends a single byte to the device.

     handle:= >= 0 (as returned by [*i2c_open*]).
   byte_val:= 0-255, the value to write.

   If OK returns 0.

   On failure returns a negative error code.

   SMBus 2.0 5.5.2 - Send byte.
   . .
   S Addr Wr [A] byte_val [A] P
   . .

   ...
   sbc.i2c_write_byte(1, 17)   # send byte   17 to handle 1
   sbc.i2c_write_byte(2, 0x23) # send byte 0x23 to handle 2
   ...
   """
   return _u2i(_lgpio._i2c_write_byte(handle, byte_val))

def i2c_read_byte(handle):
   """
   Reads a single byte from the device.

   handle:= >= 0 (as returned by [*i2c_open*]).

   If OK returns the read byte (0-255).

   On failure returns a negative error code.

   SMBus 2.0 5.5.3 - Receive byte.
   . .
   S Addr Rd [A] [Data] NA P
   . .

   ...
   b = sbc.i2c_read_byte(2) # read a byte from handle 2
   ...
   """
   return _u2i(_lgpio._i2c_read_byte(handle))

def i2c_write_byte_data(handle, reg, byte_val):
   """
   Writes a single byte to the specified register of the device.

     handle:= >= 0 (as returned by [*i2c_open*]).
        reg:= >= 0, the device register.
   byte_val:= 0-255, the value to write.

   If OK returns 0.

   On failure returns a negative error code.

   SMBus 2.0 5.5.4 - Write byte.
   . .
   S Addr Wr [A] reg [A] byte_val [A] P
   . .

   ...
   sbc.i2c_write_byte_data(1, 2, 0xC5)

   sbc.i2c_write_byte_data(2, 4, 9)
   ...
   """
   return _u2i(_lgpio._i2c_write_byte_data(handle, reg, byte_val))

def i2c_write_word_data(handle, reg, word_val):
   """
   Writes a single 16 bit word to the specified register of the
   device.

     handle:= >= 0 (as returned by [*i2c_open*]).
        reg:= >= 0, the device register.
   word_val:= 0-65535, the value to write.

   If OK returns 0.

   On failure returns a negative error code.

   SMBus 2.0 5.5.4 - Write word.
   . .
   S Addr Wr [A] reg [A] word_val_Low [A] word_val_High [A] P
   . .

   ...
   sbc.i2c_write_word_data(4, 5, 0xA0C5)

   sbc.i2c_write_word_data(5, 2, 23)
   ...
   """
   return _u2i(_lgpio._i2c_WriteWordData(handle, reg, word_val))

def i2c_read_byte_data(handle, reg):
   """
   Reads a single byte from the specified register of the device.

   handle:= >= 0 (as returned by [*i2c_open*]).
      reg:= >= 0, the device register.

   If OK returns the read byte (0-255).

   On failure returns a negative error code.

   SMBus 2.0 5.5.5 - Read byte.
   . .
   S Addr Wr [A] reg [A] S Addr Rd [A] [Data] NA P
   . .

   ...
   b = sbc.i2c_read_byte_data(2, 17)

   b = sbc.i2c_read_byte_data(0, 1)
   ...
   """
   return _u2i(_lgpio._i2c_read_byte_data(handle, reg))

def i2c_read_word_data(handle, reg):
   """
   Reads a single 16 bit word from the specified register of the
   device.

   handle:= >= 0 (as returned by [*i2c_open*]).
      reg:= >= 0, the device register.

   If OK returns the read word (0-65535).

   On failure returns a negative error code.

   SMBus 2.0 5.5.5 - Read word.
   . .
   S Addr Wr [A] reg [A] S Addr Rd [A] [DataLow] A [DataHigh] NA P
   . .

   ...
   w = sbc.i2c_read_word_data(3, 2)

   w = sbc.i2c_read_word_data(2, 7)
   ...
   """
   return _u2i(_lgpio._i2c_read_word_data(handle, reg))

def i2c_process_call(handle, reg, word_val):
   """
   Writes 16 bits of data to the specified register of the device
   and reads 16 bits of data in return.

     handle:= >= 0 (as returned by [*i2c_open*]).
        reg:= >= 0, the device register.
   word_val:= 0-65535, the value to write.

   If OK returns the read word (0-65535).

   On failure returns a negative error code.

   SMBus 2.0 5.5.6 - Process call.
   . .
   S Addr Wr [A] reg [A] word_val_Low [A] word_val_High [A]
      S Addr Rd [A] [DataLow] A [DataHigh] NA P
   . .

   ...
   r = sbc.i2c_process_call(h, 4, 0x1231)
   r = sbc.i2c_process_call(h, 6, 0)
   ...
   """
   return _u2i(_lgpio._i2c_process_call(handle, reg, word_val))

def i2c_write_block_data(handle, reg, data):
   """
   Writes up to 32 bytes to the specified register of the device.

   handle:= >= 0 (as returned by [*i2c_open*]).
      reg:= >= 0, the device register.
     data:= the bytes to write.

   If OK returns 0.

   On failure returns a negative error code.

   SMBus 2.0 5.5.7 - Block write.
   . .
   S Addr Wr [A] reg [A] len(data) [A] data0 [A] data1 [A] ... [A]
      datan [A] P
   . .

   ...
   sbc.i2c_write_block_data(4, 5, b'hello')

   sbc.i2c_write_block_data(4, 5, "data bytes")

   sbc.i2c_write_block_data(5, 0, b'\\x00\\x01\\x22')

   sbc.i2c_write_block_data(6, 2, [0, 1, 0x22])
   ...
   """
   return _u2i(_lgpio._i2c_write_block_data(handle, reg, _tobuf(data)))

def i2c_read_block_data(handle, reg):
   """
   Reads a block of up to 32 bytes from the specified register of
   the device.

   handle:= >= 0 (as returned by [*i2c_open*]).
      reg:= >= 0, the device register.

   If OK returns a list of the number of bytes read and a
   bytearray containing the bytes.

   On failure returns a list of a negative error code and
   a null string.

   The amount of returned data is set by the device.

   SMBus 2.0 5.5.7 - Block read.
   . .
   S Addr Wr [A] reg [A]
      S Addr Rd [A] [Count] A [Data] A [Data] A ... A [Data] NA P
   . .

   ...
   (b, d) = sbc.i2c_read_block_data(h, 10)
   if b >= 0:
      process data
   else:
      process read failure
   ...
   """
   return _u2i_list(_lgpio._i2c_read_block_data(handle, reg))

def i2c_block_process_call(handle, reg, data):
   """
   Writes data bytes to the specified register of the device
   and reads a device specified number of bytes of data in return.

   handle:= >= 0 (as returned by [*i2c_open*]).
      reg:= >= 0, the device register.
     data:= the bytes to write.

   If OK returns a list of the number of bytes read and a
   bytearray containing the bytes.

   On failure returns a list of a negative error code and
   a null string.

   The SMBus 2.0 documentation states that a minimum of 1 byte may
   be sent and a minimum of 1 byte may be received.  The total
   number of bytes sent/received must be 32 or less.

   SMBus 2.0 5.5.8 - Block write-block read.
   . .
   S Addr Wr [A] reg [A] len(data) [A] data0 [A] ... datan [A]
      S Addr Rd [A] [Count] A [Data] ... A P
   . .

   ...
   (b, d) = sbc.i2c_block_process_call(h, 10, b'\\x02\\x05\\x00')

   (b, d) = sbc.i2c_block_process_call(h, 10, b'abcdr')

   (b, d) = sbc.i2c_block_process_call(h, 10, "abracad")

   (b, d) = sbc.i2c_block_process_call(h, 10, [2, 5, 16])
   ...
   """
   return _u2i_list(_lgpio._i2c_block_process_call(handle, reg, _tobuf(data)))

def i2c_write_i2c_block_data(handle, reg, data):
   """
   Writes data bytes to the specified register of the device.
   1-32 bytes may be written.

   handle:= >= 0 (as returned by [*i2c_open*]).
      reg:= >= 0, the device register.
     data:= the bytes to write.

   If OK returns 0.

   On failure returns a negative error code.

   . .
   S Addr Wr [A] reg [A] data0 [A] data1 [A] ... [A] datan [NA] P
   . .

   ...
   sbc.i2c_write_i2c_block_data(4, 5, 'hello')

   sbc.i2c_write_i2c_block_data(4, 5, b'hello')

   sbc.i2c_write_i2c_block_data(5, 0, b'\\x00\\x01\\x22')

   sbc.i2c_write_i2c_block_data(6, 2, [0, 1, 0x22])
   ...
   """
   return _u2i(_lgpio._i2c_write_i2c_block_data(
      handle, reg, _tobuf(data)))

def i2c_read_i2c_block_data(handle, reg, count):
   """
   Reads count bytes from the specified register of the device.
   The count may be 1-32.

   handle:= >= 0 (as returned by [*i2c_open*]).
      reg:= >= 0, the device register.
    count:= >0, the number of bytes to read.

   If OK returns a list of the number of bytes read and a
   bytearray containing the bytes.

   On failure returns a list of a negative error code and
   a null string.

   . .
   S Addr Wr [A] reg [A]
      S Addr Rd [A] [Data] A [Data] A ... A [Data] NA P
   . .

   ...
   (b, d) = sbc.i2c_read_i2c_block_data(h, 4, 32)
   if b >= 0:
      process data
   else:
      process read failure
   ...
   """
   return _u2i_list(_lgpio._i2c_read_i2c_block_data(handle, reg, count))

def i2c_read_device(handle, count):
   """
   Returns count bytes read from the raw device associated
   with handle.

   handle:= >= 0 (as returned by [*i2c_open*]).
    count:= >0, the number of bytes to read.

   If OK returns a list of the number of bytes read and a
   bytearray containing the bytes.

   On failure returns a list of a negative error code and
   a null string.

   . .
   S Addr Rd [A] [Data] A [Data] A ... A [Data] NA P
   . .

   ...
   (count, data) = sbc.i2c_read_device(h, 12)
   ...
   """
   return _u2i_list(_lgpio._i2c_read_device(handle, count))

def i2c_write_device(handle, data):
   """
   Writes the data bytes to the raw device.

   handle:= >= 0 (as returned by [*i2c_open*]).
     data:= the bytes to write.

   If OK returns 0.

   On failure returns a negative error code.

   . .
   S Addr Wr [A] data0 [A] data1 [A] ... [A] datan [A] P
   . .

   ...
   sbc.i2c_write_device(h, b"\\x12\\x34\\xA8")

   sbc.i2c_write_device(h, b"help")

   sbc.i2c_write_device(h, 'help')

   sbc.i2c_write_device(h, [23, 56, 231])
   ...
   """
   return _u2i(_lgpio._i2c_write_device(handle, _tobuf(data)))


def i2c_zip(handle, data):
   """
   This function executes a sequence of I2C operations.  The
   operations to be performed are specified by the contents of data
   which contains the concatenated command codes and associated data.

   handle:= >= 0 (as returned by [*i2c_open*]).
     data:= the concatenated I2C commands, see below

   If OK returns a list of the number of bytes read and a
   bytearray containing the bytes.

   On failure returns a list of a negative error code and
   a null string.

   ...
   (count, data) = sbc.i2c_zip(h, [4, 0x53, 7, 1, 0x32, 6, 6, 0])
   ...

   The following command codes are supported:

   Name    @ Cmd & Data @ Meaning
   End     @ 0          @ No more commands
   Escape  @ 1          @ Next P is two bytes
   Address @ 2 P        @ Set I2C address to P
   Flags   @ 3 lsb msb  @ Set I2C flags to lsb + (msb << 8)
   Read    @ 4 P        @ Read P bytes of data
   Write   @ 5 P ...    @ Write P bytes of data

   The address, read, and write commands take a parameter P.
   Normally P is one byte (0-255).  If the command is preceded by
   the Escape command then P is two bytes (0-65535, least significant
   byte first).

   The address defaults to that associated with the handle.
   The flags default to 0.  The address and flags maintain their
   previous value until updated.

   Any read I2C data is concatenated in the returned bytearray.

   ...
   Set address 0x53, write 0x32, read 6 bytes
   Set address 0x1E, write 0x03, read 6 bytes
   Set address 0x68, write 0x1B, read 8 bytes
   End

   2 0x53  5 1 0x32  4 6
   2 0x1E  5 1 0x03  4 6
   2 0x68  5 1 0x1B  4 8
   0
   ...
   """
   return _u2i_list(_lgpio._i2c_zip(handle, _tobuf(data)))

# NOTIFICATIONS

def notify_open():
   """
   Opens a notification pipe.

   If OK returns a handle (>= 0).

   On failure returns a negative error code.

   A notification is a method for being notified of GPIO
   alerts via a pipe.

   Pipes are only accessible from the local machine so this
   function serves no purpose if you are using Python from a
   remote machine.  The in-built (socket) notifications
   provided by [*callback*] should be used instead.

   The pipes are created in the library's working directory.

   Notifications for handle x will be available at the pipe
   named .lgd-nfyx (where x is the handle number).

   E.g. if the function returns 15 then the notifications must be
   read from .lgd-nfy15.

   Notifications have the following structure:

   . .
   Q timestamp
   B chip
   B gpio
   B level
   B flags
   . .

   timestamp: the number of nanoseconds since the epoch (start of 1970). 
   chip: the gpiochip device number (NOT the handle). 
   gpio: the GPIO. 
   level: indicates the level of the GPIO (0=low, 1=high, 2=timeout). 
   flags: no flags are currently defined.

   ...
   h = sbc.notify_open()
   if h >= 0:
      sbc.notify_resume(h)
   ...
   """
   return _u2i(_lgpio._notify_open())

def notify_pause(handle):
   """
   Pauses notifications on a handle.

   handle:= >= 0 (as returned by [*notify_open*])

   If OK returns 0.

   On failure returns a negative error code.

   Notifications for the handle are suspended until
   [*notify_resume*] is called.

   ...
   h = sbc.notify_open()
   if h >= 0:
      sbc.notify_resume(h)
      ...
      sbc.notify_pause(h)
      ...
      sbc.notify_resume(h)
      ...
   ...
   """
   return _u2i(_lgpio._notify_pause(handle))

def notify_resume(handle):
   """
   Resumes notifications on a handle.

   handle:= >= 0 (as returned by [*notify_open*])

   If OK returns 0.

   On failure returns a negative error code.

   ...
   h = sbc.notify_open()
   if h >= 0:
      sbc.notify_resume(h)
   ...
   """
   return _u2i(_lgpio._notify_resume(handle))

def notify_close(handle):
   """
   Stops notifications on a handle and frees the handle for reuse.

   handle:= >= 0 (as returned by [*notify_open*])

   If OK returns 0.

   On failure returns a negative error code.

   ...
   h = sbc.notify_open()
   if h >= 0:
      sbc.notify_resume(h)
      ...
      sbc.notify_close(h)
      ...
   ...
   """
   return _u2i(_lgpio._notify_close(handle))

# SERIAL

def serial_open(tty, baud, ser_flags=0):
   """
   Returns a handle for the serial tty device opened
   at baud bits per second.  The device muse be in /dev.

         tty:= the serial device to open.
        baud:= baud rate in bits per second, see below.
   ser_flags:= 0, no flags are currently defined.

   If OK returns a handle (>= 0).

   On failure returns a negative error code.

   The baud rate must be one of 50, 75, 110, 134, 150,
   200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200,
   38400, 57600, 115200, or 230400.

   ...
   h1 = sbc.serial_open("ttyAMA0", 300)

   h2 = sbc.serial_open("ttyUSB1", 19200, 0)

   h3 = sbc.serial_open("serial0", 9600)
   ...
   """
   return _u2i(_lgpio._serial_open(tty, baud, ser_flags))

def serial_close(handle):
   """
   Closes the serial device.

   handle:= >= 0 (as returned by [*serial_open*]).

   If OK returns 0.

   On failure returns a negative error code.

   ...
   sbc.serial_close(h1)
   ...
   """
   return _u2i(_lgpio._serial_close(handle))

def serial_read_byte(handle):
   """
   Returns a single byte from the device.

   handle:= >= 0 (as returned by [*serial_open*]).

   If OK returns the read byte (0-255).

   On failure returns a negative error code.

   ...
   b = sbc.serial_read_byte(h1)
   ...
   """
   return _u2i(_lgpio._serial_read_byte(handle))

def serial_write_byte(handle, byte_val):
   """
   Writes a single byte to the device.

     handle:= >= 0 (as returned by [*serial_open*]).
   byte_val:= 0-255, the value to write.

   If OK returns 0.

   On failure returns a negative error code.

   ...
   sbc.serial_write_byte(h1, 23)

   sbc.serial_write_byte(h1, ord('Z'))
   ...
   """
   return _u2i(_lgpio._serial_write_byte(handle, byte_val))

def serial_read(handle, count=1000):
   """
   Reads up to count bytes from the device.

   handle:= >= 0 (as returned by [*serial_open*]).
    count:= >0, the number of bytes to read (defaults to 1000).

   If OK returns a list of the number of bytes read and
   a bytearray containing the bytes.

   On failure returns a list of negative error code and
   a null string.

   If no data is ready a bytes read of zero is returned.

   ...
   (b, d) = sbc.serial_read(h2, 100)
   if b > 0:
      process read data
   ...
   """
   return _u2i_list(_lgpio._serial_read(handle, count))

def serial_write(handle, data):
   """
   Writes the data bytes to the device.

   handle:= >= 0 (as returned by [*serial_open*]).
     data:= the bytes to write.

   If OK returns 0.

   On failure returns a negative error code.

   ...
   sbc.serial_write(h1, b'\\x02\\x03\\x04')

   sbc.serial_write(h2, b'help')

   sbc.serial_write(h2, "hello")

   sbc.serial_write(h1, [2, 3, 4])
   ...
   """
   return _u2i(_lgpio._serial_write(handle, _tobuf(data)))

def serial_data_available(handle):
   """
   Returns the number of bytes available to be read from the
   device.

   handle:= >= 0 (as returned by [*serial_open*]).

   If OK returns the count of bytes available (>= 0).

   On failure returns a negative error code.

   ...
   rdy = sbc.serial_data_available(h1)

   if rdy > 0:
      (b, d) = sbc.serial_read(h1, rdy)
   ...
   """
   return _u2i(_lgpio._serial_data_available(handle))


# SPI

def spi_open(spi_device, spi_channel, baud, spi_flags=0):
   """
   Returns a handle for the SPI device on the channel.  Data
   will be transferred at baud bits per second.  The flags
   may be used to modify the default behaviour.

    spi_device:= >= 0.
   spi_channel:= >= 0.
          baud:= speed to use.
     spi_flags:= see below.

   If OK returns a handle (>= 0).

   On failure returns a negative error code.

   spi_flags consists of the least significant 2 bits.

   . .
   1  0
   m  m
   . .

   mm defines the SPI mode.

   . .
   Mode POL PHA
    0    0   0
    1    0   1
    2    1   0
    3    1   1
   . .


   The other bits in flags should be set to zero.

   ...
   h = sbc.spi_open(1, 50000, 3)
   ...
   """
   return _u2i(_lgpio._spi_open(spi_device, spi_channel, baud, spi_flags))

def spi_close(handle):
   """
   Closes the SPI device.

   handle:= >= 0 (as returned by [*spi_open*]).

   If OK returns 0.

   On failure returns a negative error code.

   ...
   sbc.spi_close(h)
   ...
   """
   return _u2i(_lgpio._spi_close(handle))

def spi_read(handle, count):
   """
   Reads count bytes from the SPI device.

   handle:= >= 0 (as returned by [*spi_open*]).
    count:= >0, the number of bytes to read.

   If OK returns a list of the number of bytes read and a
   bytearray containing the bytes.

   On failure returns a list of negative error code and
   a null string.

   ...
   (b, d) = sbc.spi_read(h, 60) # read 60 bytes from handle h
   if b == 60:
      process read data
   else:
      error path
   ...
   """
   return _u2i_list(_lgpio._spi_read(handle, count))

def spi_write(handle, data):
   """
   Writes the data bytes to the SPI device.

   handle:= >= 0 (as returned by [*spi_open*]).
     data:= the bytes to write.

   If OK returns 0.

   On failure returns a negative error code.

   ...
   sbc.spi_write(0, b'\\x02\\xc0\\x80') # write 3 bytes to handle 0

   sbc.spi_write(0, b'defgh')        # write 5 bytes to handle 0

   sbc.spi_write(0, "def")           # write 3 bytes to handle 0

   sbc.spi_write(1, [2, 192, 128])   # write 3 bytes to handle 1
   ...
   """
   return _u2i(_lgpio._spi_write(handle, _tobuf(data)))

def spi_xfer(handle, data):
   """
   Writes the data bytes to the SPI device,
   returning the data bytes read from the device.

   handle:= >= 0 (as returned by [*spi_open*]).
     data:= the bytes to write.

   If OK returns a list of the number of bytes read and a
   bytearray containing the bytes.

   On failure returns a list of negative error code and
   a null string.

   ...
   (count, rx_data) = sbc.spi_xfer(h, b'\\x01\\x80\\x00')

   (count, rx_data) = sbc.spi_xfer(h, [1, 128, 0])

   (count, rx_data) = sbc.spi_xfer(h, b"hello")

   (count, rx_data) = sbc.spi_xfer(h, "hello")
   ...
   """
   return _u2i_list(_lgpio._spi_xfer(handle, _tobuf(data)))


# UTILITIES

def get_internal(config_id):
   """
   Returns the value of a configuration item.

   If OK returns a list of 0 (OK) and the item's value.

   On failure returns a list of negative error code and None.

   config_id:= the configuration item.

   ...
   cfg = sbc.get_internal(0)
   print(cfg)
   ...
   """
   return _u2i_list(_lgpio._get_internal(config_id))

def set_internal(config_id, config_value):
   """
   Sets the value of a configuration item.

      config_id:= the configuration item.
   config_value:= the value to set.

   If OK returns 0.

   On failure returns a negative error code.

   ...
   sbc.set_internal(0, 255)
   cfg = sbc.get_internal()
   print(cfg)
   ...
   """
   return _u2i(_lgpio._set_internal(config_id, config_value))

def error_text(errnum):
   """
   Returns a description of an error number.

   errnum:= <0, the error number

   ...
   print(sbc.error_text(-5))
   level not 0-1
   ...
   """
   return _lgpio._error_text(errnum)

def xref():
   """
   baud:
   The speed of serial communication (I2C, SPI, serial link)
   in bits per second.

   bit: 0-1
   A value of 0 or 1.

   byte_val: 0-255
   A whole number.

   config_id:
   A number identifying a configuration item.

   . .
   CFG_ID_DEBUG_LEVEL 0
   CFG_ID_MIN_DELAY   1
   . .

   config_value:
   The value of a configurtion item.

   count:
   The number of bytes of data to be transferred.

   data:
   Data to be transmitted, a series of bytes.

   debounce_micros:
   The debounce time in microseconds.

   edge:
   . .
   RISING_EDGE
   FALLING_EDGE
   BOTH_EDGES
   . .

   eFlags:
   Alert request flags for the GPIO.

   The following values may be or'd to form the value.

   . .
   RISING_EDGE
   FALLING_EDGE
   BOTH_EDGES
   . .

   errnum: <0
   Indicates an error.  Use [*lgpio.error_text*] for the error text.

   func:
   A user supplied callback function.

   gpio:
   The 0 based offset of a GPIO from the start of a gpiochip.

   gpiochip: >= 0
   The number of a gpiochip device.

   group_bits:
   A 64-bit value used to set the levels of a group.

   Set bit x to set GPIO x of the group high.

   Clear bit x to set GPIO x of the group low.

   group_mask:
   A 64-bit value used to determine which members of a group
   should be updated.

   Set bit x to update GPIO x of the group.

   Clear bit x to leave GPIO x of the group unaltered.

   handle: >= 0
   A number referencing an object opened by one of the following

   [*gpiochip_open*] 
   [*i2c_open*] 
   [*notify_open*] 
   [*serial_open*] 
   [*spi_open*]

   i2c_address: 0-0x7F
   The address of a device on the I2C bus.

   i2c_bus: >= 0
   An I2C bus number.

   i2c_flags: 0
   No I2C flags are currently defined.

   kind: TX_PWM or TX_WAVE
   A type of transmission.

   level: 0 or 1
   A GPIO level.

   levels:
   A list of GPIO levels.

   lFlags:
   Line modifiers for the GPIO.

   The following values may be or'd to form the value.

   . .
   SET_ACTIVE_LOW
   SET_OPEN_DRAIN
   SET_OPEN_SOURCE
   SET_BIAS_PULL_UP
   SET_BIAS_PULL_DOWN
   SET_BIAS_DISABLE
   . .

   notify_handle:
   This associates a notification with a GPIO alert.

   pulse_cycles: >= 0
   The number of pulses to generate.  A value of 0 means infinite.

   pulse_delay:
   The delay in microseconds before the next wave pulse.

   pulse_off: >= 0
   The off period for a pulse in microseconds.

   pulse_offset: >= 0
   The offset in microseconds from the nominal pulse start.

   pulse_on: >= 0
   The on period for a pulse in microseconds.

   pulse_width: 0, 500-2500 microseconds
   Servo pulse width

   pulses:
   pulses is a list of pulse objects.  A pulse object is a container
   class with the following members.

   group_bits - the levels to set if the corresponding bit in
   group_mask is set. 
   group_mask - a mask indicating the group GPIO to be updated. 
   pulse_delay - the delay in microseconds before the next pulse.

   pwm_duty_cycle: 0-100 %
   PWM duty cycle %

   pwm_frequency: 0.1-10000 Hz
   PWM frequency

   reg: 0-255
   An I2C device register.  The usable registers depend on the
   actual device.

   ser_flags: 32 bit
   No serial flags are currently defined.

   servo_frequency:: 40-500 Hz
   Servo pulse frequency

   spi_channel: >= 0
   A SPI channel.

   spi_device: >= 0
   A SPI device.

   spi_flags: 32 bit
   See [*spi_open*].

   tty:
   A serial device, e.g. ttyAMA0, ttyUSB0

   uint32:
   An unsigned 32 bit number.

   watchdog_micros:
   The watchdog time in microseconds.

   word_val: 0-65535
   A whole number.
   """
   pass

