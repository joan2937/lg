"""
[http://abyz.me.uk/lg/py_rgpio.html]

rgpio is a Python module which allows remote control of the GPIO
and other functions of Linux SBCs running the rgpiod daemon.

The rgpiod daemon must be running on the SBCs you wish to control.

*Features*

o the rgpio Python module can run on Windows, Macs, or Linux
o controls one or more SBCs
o reading and writing GPIO singly and in groups
o software timed PWM and waves
o GPIO callbacks
o pipe notification of GPIO alerts
o I2C wrapper
o SPI wrapper
o serial link wrapper
o simple file handling
o creating and running scripts on the rgpiod daemon

*Exceptions*

By default a fatal exception is raised if you pass an invalid
argument to a rgpio function.

If you wish to handle the returned status yourself you should set
rgpio.exceptions to False.

You may prefer to check the returned status in only a few parts
of your code.  In that case do the following:

...
rgpio.exceptions = False

# Code where you want to test the error status.

rgpio.exceptions = True
...

*Usage*

The rgpiod daemon must be running on the SBCs whose GPIO
are to be manipulated.

The normal way to start rgpiod is during system start.

rgpiod &

Your Python program must import rgpio and create one or more
instances of the rgpio.sbc class.  This class gives access to
the specified SBC's GPIO.

...
sbc1 = rgpio.sbc()       # sbc1 accesses the local SBC's GPIO
sbc2 = rgpio.sbc('tom')  # sbc2 accesses tom's GPIO
sbc3 = rgpio.sbc('dick') # sbc3 accesses dick's GPIO
...

The later example code snippets assume that sbc is an instance of
the rgpio.sbc class.

*Licence*

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>

OVERVIEW

ESSENTIAL

rgpio.sbc                 Initialise sbc connection
stop                      Stop a sbc connection

FILES

file_open                 Opens a file
file_close                Closes a file

file_read                 Reads bytes from a file
file_write                Writes bytes to a file

file_seek                 Seeks to a position within a file

file_list                 List files which match a pattern

GPIO

gpiochip_open             Opens a gpiochip device
gpiochip_close            Closes a gpiochip device

gpio_get_chip_info        Get information about a gpiochip
gpio_get_line_info        Get information about a gpiochip line

gpio_get_mode             Gets the mode of a GPIO

gpio_claim_input          Claims a GPIO for input
gpio_claim_output         Claims a GPIO for output
gpio_claim_alert          Claims a GPIO for alerts
gpio_free                 Frees a GPIO

group_claim_input         Claims a group of GPIO for inputs
group_claim_output        Claims a group of GPIO for outputs
group_free                Frees a group of GPIO

gpio_read                 Reads a GPIO
gpio_write                Writes a GPIO

group_read                Reads a group of GPIO
group_write               Writes a group of GPIO

tx_pulse                  Starts pulses on a GPIO
tx_pwm                    Starts PWM on a GPIO
tx_servo                  Starts servo pulses on a GPIO
tx_wave                   Starts a wave on a group of GPIO
tx_busy                   See if tx is active on a GPIO or group
tx_room                   See if more room for tx on a GPIO or group

gpio_set_debounce_micros  Sets the debounce time for a GPIO
gpio_set_watchdog_micros  Sets the watchdog time for a GPIO

callback                  Starts a GPIO callback

I2C

i2c_open                  Opens an I2C device
i2c_close                 Closes an I2C device

i2c_write_quick           SMBus write quick

i2c_read_byte             SMBus read byte
i2c_write_byte            SMBus write byte

i2c_read_byte_data        SMBus read byte data
i2c_write_byte_data       SMBus write byte data

i2c_read_word_data        SMBus read word data
i2c_write_word_data       SMBus write word data

i2c_read_block_data       SMBus read block data
i2c_write_block_data      SMBus write block data

i2c_read_i2c_block_data   SMBus read I2C block data
i2c_write_i2c_block_data  SMBus write I2C block data

i2c_read_device           Reads the raw I2C device
i2c_write_device          Writes the raw I2C device

i2c_process_call          SMBus process call
i2c_block_process_call    SMBus block process call

i2c_zip                   Performs multiple I2C transactions

NOTIFICATIONS

notify_open               Request a notification handle
notify_close              Close a notification
notify_pause              Pause notifications
notify_resume             Resume notifications

SCRIPTS

script_store              Store a script
script_run                Run a stored script
script_update             Set a scripts parameters
script_status             Get script status and parameters
script_stop               Stop a running script
script_delete             Delete a stored script

SERIAL

serial_open               Opens a serial device
serial_close              Closes a serial device

serial_read_byte          Reads a byte from a serial device
serial_write_byte         Writes a byte to a serial device

serial_read               Reads bytes from a serial device
serial_write              Writes bytes to a serial device

serial_data_available     Returns number of bytes ready to be read

SHELL

shell                     Executes a shell command

SPI

spi_open                  Opens a SPI device
spi_close                 Closes a SPI device

spi_read                  Reads bytes from a SPI device
spi_write                 Writes bytes to a SPI device
spi_xfer                  Transfers bytes with a SPI device

UTILITIES

get_sbc_name              Get the SBC name

get_internal              Get an SBC configuration value
set_internal              Set an SBC configuration value

set_user                  Set the user (and associated permissions)
set_share_id              Set the share id for a resource
use_share_id              Use this share id when asking for a resource

rgpio.get_module_version  Get the rgpio Python module version
rgpio.error_text          Get the error text for an error code
"""

import sys
import socket
import struct
import time
import threading
import os
import atexit
import hashlib

RGPIO_PY_VERSION = 0x00020200

exceptions = True

MAGIC=1818715245

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
SET_PULL_UP = 32
SET_PULL_DOWN = 64
SET_PULL_NONE = 128

# GPIO event flags

RISING_EDGE = 1
FALLING_EDGE = 2
BOTH_EDGES = 3

# tx constants

TX_PWM = 0
TX_WAVE = 1

# script run status

SCRIPT_INITING = 0
SCRIPT_READY = 1
SCRIPT_RUNNING = 2
SCRIPT_WAITING = 3
SCRIPT_ENDED = 4
SCRIPT_HALTED = 5
SCRIPT_FAILED = 6

# notification flags

NTFY_FLAGS_ALIVE = (1 << 0)

FILE_READ = 1
FILE_WRITE = 2
FILE_RW = 3

FILE_APPEND = 4
FILE_CREATE = 8
FILE_TRUNC = 16

FROM_START = 0
FROM_CURRENT = 1
FROM_END = 2

SPI_MODE_0 = 0
SPI_MODE_1 = 1
SPI_MODE_2 = 2
SPI_MODE_3 = 3

_SOCK_CMD_LEN = 16

# rgpiod command numbers

_CMD_FO = 1
_CMD_FC = 2
_CMD_FR = 3
_CMD_FW = 4
_CMD_FS = 5
_CMD_FL = 6
_CMD_GO = 10
_CMD_GC = 11
_CMD_GSIX = 12
_CMD_GSOX = 13
_CMD_GSAX = 14
_CMD_GSF = 15
_CMD_GSGIX = 16
_CMD_GSGOX = 17
_CMD_GSGF = 18
_CMD_GR = 19
_CMD_GW = 20
_CMD_GGR = 21
_CMD_GGWX = 22
_CMD_GPX = 23
_CMD_PX = 24
_CMD_SX = 25
_CMD_GWAVE = 26
_CMD_GBUSY = 27
_CMD_GROOM = 28
_CMD_GDEB = 29
_CMD_GWDOG = 30
_CMD_GIC = 31
_CMD_GIL = 32
_CMD_GMODE = 33
_CMD_I2CO = 40
_CMD_I2CC = 41
_CMD_I2CRD = 42
_CMD_I2CWD = 43
_CMD_I2CWQ = 44
_CMD_I2CRS = 45
_CMD_I2CWS = 46
_CMD_I2CRB = 47
_CMD_I2CWB = 48
_CMD_I2CRW = 49
_CMD_I2CWW = 50
_CMD_I2CRK = 51
_CMD_I2CWK = 52
_CMD_I2CRI = 53
_CMD_I2CWI = 54
_CMD_I2CPC = 55
_CMD_I2CPK = 56
_CMD_I2CZ = 57
_CMD_NO = 70
_CMD_NC = 71
_CMD_NR = 72
_CMD_NP = 73
_CMD_PARSE = 80
_CMD_PROC = 81
_CMD_PROCD = 82
_CMD_PROCP = 83
_CMD_PROCR = 84
_CMD_PROCS = 85
_CMD_PROCU = 86
_CMD_SERO = 90
_CMD_SERC = 91
_CMD_SERRB = 92
_CMD_SERWB = 93
_CMD_SERR = 94
_CMD_SERW = 95
_CMD_SERDA = 96
_CMD_SPIO = 100
_CMD_SPIC = 101
_CMD_SPIR = 102
_CMD_SPIW = 103
_CMD_SPIX = 104
_CMD_MICS = 113
_CMD_MILS = 114
_CMD_CGI = 115
_CMD_CSI = 116
_CMD_NOIB = 117
_CMD_SHELL = 118
_CMD_SBC = 120
_CMD_FREE = 121
_CMD_SHARE = 130
_CMD_USER = 131
_CMD_PASSW = 132
_CMD_LCFG = 133
_CMD_SHRU = 134
_CMD_SHRS = 135
_CMD_PWD = 136
_CMD_PCD = 137
_CMD_LGV = 140
_CMD_TICK = 141

# rgpiod error numbers

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

# rgpiod error text

_errors=[
   [OKAY,  "No error"],
   [INIT_FAILED,  "initialisation failed"],
   [BAD_MICROS,  "micros not 0-999999"],
   [BAD_PATHNAME,  "can not open pathname"],
   [NO_HANDLE,  "no handle available"],
   [BAD_HANDLE,  "unknown handle"],
   [BAD_SOCKET_PORT,  "socket port not 1024-32000"],
   [NOT_PERMITTED,  "GPIO operation not permitted"],
   [SOME_PERMITTED,  "one or more GPIO not permitted"],
   [BAD_SCRIPT,  "invalid script"],
   [BAD_TX_TYPE,  "bad tx type for GPIO and group"],
   [GPIO_IN_USE,  "GPIO already in use"],
   [BAD_PARAM_NUM,  "script parameter id not 0-9"],
   [DUP_TAG,  "script has duplicate tag"],
   [TOO_MANY_TAGS,  "script has too many tags"],
   [BAD_SCRIPT_CMD,  "illegal script command"],
   [BAD_VAR_NUM,  "script variable id not 0-149"],
   [NO_SCRIPT_ROOM,  "no more room for scripts"],
   [NO_MEMORY,  "can not allocate temporary memory"],
   [SOCK_READ_FAILED,  "socket read failed"],
   [SOCK_WRIT_FAILED,  "socket write failed"],
   [TOO_MANY_PARAM,  "too many script parameters (> 10)"],
   [SCRIPT_NOT_READY,  "script initialising"],
   [BAD_TAG,  "script has unresolved tag"],
   [BAD_MICS_DELAY,  "bad MICS delay (too large)"],
   [BAD_MILS_DELAY,  "bad MILS delay (too large)"],
   [I2C_OPEN_FAILED,  "can not open I2C device"],
   [SERIAL_OPEN_FAILED,  "can not open serial device"],
   [SPI_OPEN_FAILED,  "can not open SPI device"],
   [BAD_I2C_BUS,  "bad I2C bus"],
   [BAD_I2C_ADDR,  "bad I2C address"],
   [BAD_SPI_CHANNEL,  "bad SPI channel"],
   [BAD_I2C_FLAGS,  "bad I2C open flags"],
   [BAD_SPI_FLAGS,  "bad SPI open flags"],
   [BAD_SERIAL_FLAGS,  "bad serial open flags"],
   [BAD_SPI_SPEED,  "bad SPI speed"],
   [BAD_SERIAL_DEVICE,  "bad serial device name"],
   [BAD_SERIAL_SPEED,  "bad serial baud rate"],
   [BAD_FILE_PARAM,  "bad file parameter"],
   [BAD_I2C_PARAM,  "bad I2C parameter"],
   [BAD_SERIAL_PARAM,  "bad serial parameter"],
   [I2C_WRITE_FAILED,  "i2c write failed"],
   [I2C_READ_FAILED,  "i2c read failed"],
   [BAD_SPI_COUNT,  "bad SPI count"],
   [SERIAL_WRITE_FAILED,  "ser write failed"],
   [SERIAL_READ_FAILED,  "ser read failed"],
   [SERIAL_READ_NO_DATA,  "ser read no data available"],
   [UNKNOWN_COMMAND,  "unknown command"],
   [SPI_XFER_FAILED,  "spi xfer/read/write failed"],
   [BAD_POINTER,  "bad (NULL) pointer"],
   [MSG_TOOBIG,  "socket/pipe message too big"],
   [BAD_MALLOC_MODE,  "bad memory allocation mode"],
   [TOO_MANY_SEGS,  "too many I2C transaction segments"],
   [BAD_I2C_SEG,  "an I2C transaction segment failed"],
   [BAD_SMBUS_CMD,  "SMBus command not supported by driver"],
   [BAD_I2C_WLEN,  "bad I2C write length"],
   [BAD_I2C_RLEN,  "bad I2C read length"],
   [BAD_I2C_CMD,  "bad I2C command"],
   [FILE_OPEN_FAILED,  "file open failed"],
   [BAD_FILE_MODE,  "bad file mode"],
   [BAD_FILE_FLAG,  "bad file flag"],
   [BAD_FILE_READ,  "bad file read"],
   [BAD_FILE_WRITE,  "bad file write"],
   [FILE_NOT_ROPEN,  "file not open for read"],
   [FILE_NOT_WOPEN,  "file not open for write"],
   [BAD_FILE_SEEK,  "bad file seek"],
   [NO_FILE_MATCH,  "no files match pattern"],
   [NO_FILE_ACCESS,  "no permission to access file"],
   [FILE_IS_A_DIR,  "file is a directory"],
   [BAD_SHELL_STATUS,  "bad shell return status"],
   [BAD_SCRIPT_NAME,  "bad script name"],
   [CMD_INTERRUPTED,  "Python socket command interrupted"],
   [BAD_EVENT_REQUEST,  "bad event request"],
   [BAD_GPIO_NUMBER,  "bad GPIO number"],
   [BAD_GROUP_SIZE,  "bad group size"],
   [BAD_LINEINFO_IOCTL,  "bad lineinfo IOCTL"],
   [BAD_READ,  "bad GPIO read"],
   [BAD_WRITE,  "bad GPIO write"],
   [CANNOT_OPEN_CHIP,  "can not open gpiochip"],
   [GPIO_BUSY,  "GPIO busy"],
   [GPIO_NOT_ALLOCATED,  "GPIO not allocated"],
   [NOT_A_GPIOCHIP,  "not a gpiochip"],
   [NOT_ENOUGH_MEMORY,  "not enough memory"],
   [POLL_FAILED,  "GPIO poll failed"],
   [TOO_MANY_GPIOS,  "too many GPIO"],
   [UNEGPECTED_ERROR,  "unexpected error"],
   [BAD_PWM_MICROS,  "bad PWM micros"],
   [NOT_GROUP_LEADER,  "GPIO not the group leader"],
   [SPI_IOCTL_FAILED,  "SPI iOCTL failed"],
   [BAD_GPIOCHIP,  "bad gpiochip"],
   [BAD_CHIPINFO_IOCTL,  "bad chipinfo IOCTL"],
   [BAD_CONFIG_FILE,  "bad configuration file"],
   [BAD_CONFIG_VALUE,  "bad configuration value"],
   [NO_PERMISSIONS,  "no permission to perform action"],
   [BAD_USERNAME,  "bad user name"],
   [BAD_SECRET,  "bad secret for user"],
   [TX_QUEUE_FULL,  "TX queue full"],
   [BAD_CONFIG_ID,  "bad configuration id"],
   [BAD_DEBOUNCE_MICS,  "bad debounce microseconds"],
   [BAD_WATCHDOG_MICS,  "bad watchdog microseconds"],
   [BAD_SERVO_FREQ,  "bad servo frequency"],
   [BAD_SERVO_WIDTH,  "bad servo pulsewidth"],
   [BAD_PWM_FREQ,  "bad PWM frequency"],
   [BAD_PWM_DUTY,  "bad PWM dutycycle"],
   [GPIO_NOT_AN_OUTPUT,  "GPIO not set as an output"],
   [INVALID_GROUP_ALERT,  "can not set a group to alert"],
]

_except_a = "############################################################\n{}"

_except_z = "############################################################"

_except_1 = """
Did you start the rgpiod daemon? E.g. rgpiod &

Did you specify the correct host/port in the environment
variables LG_ADDR and/or LG_PORT?
E.g. export LG_ADDR=soft, export LG_PORT=8889

Did you specify the correct host/port in the
rgpio.sbc() function? E.g. rgpio.sbc('soft', 8889)"""

_except_2 = """
Do you have permission to access the rgpiod daemon?
Perhaps it was started with rgpiod -nlocalhost"""

_except_3 = """
Can't create callback thread.
Perhaps too many simultaneous rgpiod connections."""

class _socklock:
   """
   A class to store socket and lock.
   """
   def __init__(self):
      self.s = None
      self.l = threading.Lock()

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


# A couple of hacks to cope with different string handling
# between various Python versions
# 3 != 2.7.8 != 2.7.3

if sys.hexversion < 0x03000000:
   def _b(x):
      return x
else:
   def _b(x):
      return x.encode('latin-1')

if sys.hexversion < 0x02070800:
   def _str(x):
      return buffer(x)
else:
   def _str(x):
      return x

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
   a rgpio exception will be raised if exceptions is True.
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
   a rgpio exception will be raised if exceptions is True.
   """
   lst[0] = u2i(lst[0])
   if lst[0] < 0:
      if exceptions:
         raise error(error_text(lst[0]))
   return lst

def _lg_command(sl, cmd, Q=0, L=0, H=0):
   """
   """
   status = CMD_INTERRUPTED
   with sl.l:
      sl.s.send(struct.pack('IIHHHH', MAGIC, 0, cmd, Q, L, H))
      status, dummy = struct.unpack('I12s', sl.s.recv(_SOCK_CMD_LEN))
   return status

def _lg_command_nolock(sl, cmd, Q=0, L=0, H=0):
   """
   """
   status = CMD_INTERRUPTED
   sl.s.send(struct.pack('IIHHHH', MAGIC, 0, cmd, Q, L, H))
   status, dummy = struct.unpack('I12s', sl.s.recv(_SOCK_CMD_LEN))
   return status

def _lg_command_ext(sl, cmd, p3, extents, Q=0, L=0, H=0):
   """
   """
   ext = bytearray(struct.pack('IIHHHH', MAGIC, p3, cmd, Q, L, H))
   for x in extents:
      if type(x) == type(""):
         ext.extend(_b(x))
      else:
         ext.extend(x)
   status = CMD_INTERRUPTED
   with sl.l:
      sl.s.sendall(ext)
      status, dummy = struct.unpack('I12s', sl.s.recv(_SOCK_CMD_LEN))
   return status

def _lg_command_ext_nolock(sl, cmd, p3, extents, Q=0, L=0, H=0):
   """
   """
   status = CMD_INTERRUPTED
   ext = bytearray(struct.pack('IIHHHH', MAGIC, p3, cmd, Q, L, H))
   for x in extents:
      if type(x) == type(""):
         ext.extend(_b(x))
      else:
         ext.extend(x)
   sl.s.sendall(ext)
   status, dummy = struct.unpack('I12s', sl.s.recv(_SOCK_CMD_LEN))
   return status

class _callback_ADT:
   """
   An ADT class to hold callback information.
   """

   def __init__(self, gpiochip, gpio, edge, func):
      """
      Initialises a callback ADT.

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
   A class to encapsulate rgpio notification callbacks.
   """

   def __init__(self, control, host, port):
      """
      Initialises notifications.
      """
      threading.Thread.__init__(self)
      self.control = control
      self.sl = _socklock()
      self.go = False
      self.daemon = True
      self.monitor = 0
      self.callbacks = []
      self.sl.s = socket.create_connection((host, port), None)
      self.lastLevel = 0
      self.handle = _u2i(_lg_command(self.sl, _CMD_NOIB))
      self.go = True
      self.start()

   def stop(self):
      """
      Stops notifications.
      """
      if self.go:
         self.go = False
         ext = [struct.pack("I", self.handle)]
         _lg_command_ext(self.control, _CMD_NC, 4, ext, L=1)

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

      lastLevel = self.lastLevel
      RECV_SIZ = 4096
      MSG_SIZ = 16 # 4 bytes of padding in each message

      buf = bytes()
      while self.go:

         buf += self.sl.s.recv(RECV_SIZ)
         offset = 0

         while self.go and (len(buf) - offset) >= MSG_SIZ:
            msgbuf = buf[offset:offset + MSG_SIZ]
            offset += MSG_SIZ
            tick, chip, gpio, level, flags, pad = (
               struct.unpack('QBBBBI', msgbuf))

            if flags == 0:
               for cb in self.callbacks:
                  if cb.gpio == gpio:
                     cb.func(chip, gpio, level, tick)
            else: # no flags currently defined, ignore.
               pass

         buf = buf[offset:]

      self.sl.s.close()

class _callback:
   """
   A class to provide GPIO level change callbacks.
   """

   def __init__(self, notify, chip, gpio, edge=RISING_EDGE, func=None):
      """
      Initialise a callback and adds it to the notification thread.
      """
      self._notify = notify
      self.count=0
      self._reset = False
      if func is None:
         func=self._tally
      self.callb = _callback_ADT(chip, gpio, edge, func)
      self._notify.append(self.callb)

   def cancel(self):
      """
      Cancels a callback by removing it from the notification thread.
      """
      self._notify.remove(self.callb)

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
      Provides a count of how many times the default tally
      callback has triggered.

      The count will be zero if the user has supplied their own
      callback function.
      """
      return self.count

   def reset_tally(self):
      """
      Resets the tally count to zero.
      """
      self._reset = True
      self.count = 0

def error_text(errnum):
   """
   Returns a description of an error number.

   errnum:= <0, the error number

   ...
   print(rgpio.error_text(-5))
   level not 0-1
   ...
   """
   for e in _errors:
      if e[0] == errnum:
         return e[1]
   return "unknown error"

def get_module_version():
   """
   Returns the version number of the rgpio Python module as a dotted
   quad.

   A.B.C.D
   
   A. API major version, changed if breaks previous API 
   B. API minor version, changed when new function added 
   C. bug fix 
   D. documentation changegi
   """
   return "rgpio.py_{}.{}.{}.{}".format(
      (RGPIO_PY_VERSION>>24)&0xff, (RGPIO_PY_VERSION>>16)&0xff,
      (RGPIO_PY_VERSION>>8)&0xff, RGPIO_PY_VERSION&0xff)

class sbc():

   def _rxbuf(self, count):
      """
      Returns count bytes from the command socket.
      """
      ext = bytearray(self.sl.s.recv(count))
      while len(ext) < count:
         ext.extend(self.sl.s.recv(count - len(ext)))
      return ext

   def __repr__(self):
      """
      Returns details of the sbc connection.
      """
      return "<rgpio.sbc host={} port={}>".format(self._host, self._port)

   # ESSENTIAL

   def __init__(self,
                host = os.getenv("LG_ADDR", 'localhost'),
                port = os.getenv("LG_PORT", 8889),
                show_errors = True):
      """
      Establishes a connection to the rgpiod daemon running on a SBC.

      host:= the host name of the SBC on which the rgpiod daemon is
             running.  The default is localhost unless overridden by
             the LG_ADDR environment variable.
      port:= the port number on which the rgpiod daemon is listening.
             The default is 8889 unless overridden by the LG_PORT
             environment variable.  The rgpiod daemon must have been
             started with the same port number.

      This connects to the rgpiod daemon and reserves resources
      to be used for sending commands and receiving notifications.

      An instance attribute [*connected*] may be used to check the
      success of the connection.  If the connection is established
      successfully [*connected*] will be True, otherwise False.

      If the LG_USER environment variable exists that user will be
      "logged in" using [*set_user*].  This only has an effect if
      the rgpiod daemon is running with access control enabled.

      ...
      sbc = rgpio.sbc()             # use defaults
      sbc = rgpio.sbc('mypi')       # specify host, default port
      sbc = rgpio.sbc('mypi', 7777) # specify host and port

      sbc = rgpio.sbc()             # exit script if no connection
      if not sbc.connected:
         exit()
      ...
      """
      self.connected = True

      self.sl = _socklock()
      self._notify  = None

      port = int(port)

      if host == '':
         host = "localhost"

      self._host = host
      self._port = port

      try:
         self.sl.s = socket.create_connection((host, port), None)

         # Disable the Nagle algorithm.
         self.sl.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

         self._notify = _callback_thread(self.sl, host, port)

      except socket.error:
         exception = 1

      except struct.error:
         exception = 2

      except error:
         # assumed to be no handle available
         exception = 3

      else:
         exception = 0
         atexit.register(self.stop)

      if exception != 0:

         self.connected = False

         if self.sl.s is not None:
            self.sl.s = None

         if show_errors:

            s = "Can't connect to rgpiod at {}({})".format(host, str(port))


            print(_except_a.format(s))
            if exception == 1:
                print(_except_1)
            elif exception == 2:
                print(_except_2)
            else:
                print(_except_3)
            print(_except_z)

      else: # auto login if LG_USER exists

         user = os.getenv("LG_USER", '')

         if len(user) > 0:
            self.set_user(user)

   def stop(self):
      """
      Disconnects from the rgpiod daemon and releases any used resources.

      ...
      sbc.stop()
      ...
      """

      self.connected = False

      if self._notify is not None:
         self._notify.stop()
         self._notify = None

      if self.sl.s is not None:
         # Free all resources allocated to this connection
         _lg_command(self.sl, _CMD_FREE)
         self.sl.s.close()
         self.sl.s = None

   # FILES

   def file_open(self, file_name, file_mode):
      """
      This function returns a handle to a file opened in a specified mode.

      This is a privileged command. See [+Permits+].

      file_name:= the file to open.
      file_mode:= the file open mode.

      If OK returns a handle (>= 0).

      On failure returns a negative error code.

      Mode

      The mode may have the following values:

      Constant   @ Value @ Meaning
      FILE_READ  @   1   @ open file for reading
      FILE_WRITE @   2   @ open file for writing
      FILE_RW    @   3   @ open file for reading and writing

      The following values may be or'd into the mode:

      Name        @ Value @ Meaning
      FILE_APPEND @ 4     @ All writes append data to the end of the file
      FILE_CREATE @ 8     @ The file is created if it doesn't exist
      FILE_TRUNC  @ 16    @ The file is truncated

      Newly created files are owned by the user who launched the daemon.
      They will have permissions owner read and write.

      ...
      #!/usr/bin/env python

      import rgpio

      sbc = rgpio.sbc()

      if not sbc.connected:
         exit()

      handle = sbc.file_open("/ram/lg.c", rgpio.FILE_READ)

      done = False

      while not done:
         c, d = sbc.file_read(handle, 60000)
         if c > 0:
            print(d)
         else:
            done = True

      sbc.file_close(handle)

      sbc.stop()
      ...
      """
      ext = [struct.pack("I", file_mode)] + [file_name]
      return _u2i(_lg_command_ext(
         self.sl, _CMD_FO, 4+len(file_name), ext, L=1))

   def file_close(self, handle):
      """
      Closes a file.

      handle:= >= 0 (as returned by [*file_open*]).

      If OK returns 0.

      On failure returns a negative error code.

      ...
      sbc.file_close(handle)
      ...
      """
      ext = [struct.pack("I", handle)]
      return _u2i(_lg_command_ext(self.sl, _CMD_FC, 4, ext, L=1))

   def file_read(self, handle, count):
      """
      Reads up to count bytes from the file.

      handle:= >= 0 (as returned by [*file_open*]).
       count:= >0, the number of bytes to read.

      If OK returns a list of the number of bytes read and a
      bytearray containing the bytes.

      On failure returns a list of a negative error code and an
      empty string.

      ...
      (b, d) = sbc.file_read(h2, 100)
      if b > 0:
         # process read data
      ...
      """
      bytes = CMD_INTERRUPTED
      ext = [struct.pack("II", handle, count)]
      rdata = ""
      with self.sl.l:
         bytes = u2i(
            _lg_command_ext_nolock(self.sl, _CMD_FR, 8, ext, L=2))
         if bytes > 0:
            rdata = self._rxbuf(bytes)
      return _u2i_list([bytes, rdata])

   def file_write(self, handle, data):
      """
      Writes the data bytes to the file.

      handle:= >= 0 (as returned by [*file_open*]).
        data:= the bytes to write.

      If OK returns 0.

      On failure returns a negative error code.

      ...
      sbc.file_write(h1, b'\\x02\\x03\\x04')

      sbc.file_write(h2, b'help')

      sbc.file_write(h2, "hello")

      sbc.file_write(h1, [2, 3, 4])
      ...
      """
      ext = [struct.pack("I", handle)] + [data]
      return _u2i(_lg_command_ext(self.sl, _CMD_FW, 4+len(data), ext, L=1))

   def file_seek(self, handle, seek_offset, seek_from):
      """
      Seeks to a position relative to the start, current position,
      or end of the file.  Returns the new position.

           handle:= >= 0 (as returned by [*file_open*]).
      seek_offset:= byte offset.
        seek_from:= FROM_START, FROM_CURRENT, or FROM_END.

      If OK returns the new file position.

      On failure returns a negative error code.

      ...
      new_pos = sbc.file_seek(h, 100, rgpio.FROM_START)

      cur_pos = sbc.file_seek(h, 0, rgpio.FROM_CURRENT)

      file_size = sbc.file_seek(h, 0, rgpio.FROM_END)
      ...
      """
      ext = [struct.pack("IiI", handle, seek_offset, seek_from)]
      return _u2i(_lg_command_ext(self.sl, _CMD_FS, 12, ext, L=3))

   def file_list(self, fpattern):
      """
      Returns a list of files which match a pattern.

      This is a privileged command. See [+Permits+].

      fpattern:= file pattern to match.

      If OK returns a list of the number of bytes read and a
      bytearray containing the matching filenames (the filenames
      are separated by newline characters).

      On failure returns a list of a negative error code and an
      empty string.

      ...
      #!/usr/bin/env python

      import rgpio

      sbc = rgpio.sbc()

      if not sbc.connected:
         exit()

      c, d = sbc.file_list("/ram/p*.c")
      if c > 0:
         print(d)

      sbc.stop()
      ...
      """
      bytes = CMD_INTERRUPTED
      ext = [struct.pack("I", 60000)] + [fpattern]
      rdata = ""
      with self.sl.l:
         bytes = u2i(_lg_command_ext_nolock(
            self.sl, _CMD_FL, 4+len(fpattern), ext, L=1))
         if bytes > 0:
            rdata = self._rxbuf(bytes)
      return _u2i_list([bytes, rdata])

   # GPIO

   def gpiochip_open(self, gpiochip):
      """
      This returns a handle to a gpiochip device.

      This is a privileged command.  See [+permits+].

      gpiochip:= >= 0

      If OK returns a handle (>= 0).

      On failure returns a negative error code.

      ...
      h = gpiochip_open(0) # open /dev/gpiochip0
      if h >= 0:
         # open okay
      else:
         # open error
      ...
      """
      ext = [struct.pack("I", gpiochip)]
      handle = u2i(_lg_command_ext(self.sl, _CMD_GO, 4, ext, L=1))
      if handle >= 0:
         handle = handle | (gpiochip << 16)

      return _u2i(handle)

   def gpiochip_close(self, handle):
      """
      This closes a gpiochip device.

      handle:= >= 0 (as returned by [*gpiochip_open*]).

      If OK returns 0.

      On failure returns a negative error code.

      ...
      sbc.gpiochip_close(h)
      ...
      """
      ext = [struct.pack("I", handle&0xffff)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GC, 4, ext, L=1))

   def gpio_get_chip_info(self, handle):
      """
      This returns summary information of an opened gpiochip.

      handle:= >= 0 (as returned by [*gpiochip_open*]).

      If OK returns a list of okay status, number of
      lines, name, and label.

      On failure returns a negative error code.
      """
      bytes = CMD_INTERRUPTED
      ext = [struct.pack("I", handle&0xffff)]
      rdata = ""
      with self.sl.l:
         bytes = u2i(
            _lg_command_ext_nolock(self.sl, _CMD_GIC, 4, ext, L=1))
         if bytes > 0:
            rdata = self._rxbuf(bytes)
            lines, name, label = struct.unpack("I32s32s", rdata)
            bytes = OKAY
         else:
            lines, name, label = 0, "", ""
      return _u2i_list([bytes, lines,
         name.decode().rstrip('\0'), label.decode().rstrip('\0')])


   def gpio_get_line_info(self, handle, gpio):
      """
      This returns detailed information of a GPIO of
      an opened gpiochip.

      handle:= >= 0 (as returned by [*gpiochip_open*]).
        gpio:= the GPIO.

      If OK returns a list of okay status, offset,
      line flags, name, and user.

      The meaning of the line flags bits are as given for the mode
      by [*gpio_get_mode*].

      On failure returns a negative error code.
      """
      bytes = CMD_INTERRUPTED
      ext = [struct.pack("II", handle&0xffff, gpio)]
      rdata = ""
      with self.sl.l:
         bytes = u2i(
            _lg_command_ext_nolock(self.sl, _CMD_GIL, 8, ext, L=2))
         if bytes > 0:
            rdata = self._rxbuf(bytes)
            offset, flags, name, user = struct.unpack("II32s32s", rdata)
            bytes = OKAY
         else:
            offset, flags, name, user = 0, 0, "", ""
      return _u2i_list(
         [bytes, offset, flags,
            name.decode().rstrip('\0'), user.decode().rstrip('\0')])

   def gpio_get_mode(self, handle, gpio):
      """
      This returns the mode of a GPIO.

      handle:= >= 0 (as returned by [*gpiochip_open*]).
        gpio:= the GPIO.

      If OK returns the mode of the GPIO.

      On failure returns a negative error code.

      Bit @ Value @ Meaning
      0   @  1    @ Kernel: In use by the kernel
      1   @  2    @ Kernel: Output
      2   @  4    @ Kernel: Active low
      3   @  8    @ Kernel: Open drain
      4   @ 16    @ Kernel: Open source
      5   @ 32    @ Kernel: Pull up set
      6   @ 64    @ Kernel: Pull down set
      7   @ 128   @ Kernel: Pulls off set
      8   @ 256   @ LG: Input
      9   @ 512   @ LG: Output
      10  @ 1024  @ LG: Alert
      11  @ 2048  @ LG: Group
      12  @ 4096  @ LG: ---
      13  @ 8192  @ LG: ---
      14  @ 16384 @ LG: ---
      15  @ 32768 @ LG: ---
      16  @ 65536 @ Kernel: Input
      17  @ 1<<17 @ Kernel: Rising edge alert
      18  @ 1<<18 @ Kernel: Falling edge alert
      19  @ 1<<19 @ Kernel: Realtime clock alert

      The LG bits are only set if the query was made by the process
      that owns the GPIO.
      """
      ext = [struct.pack("II", handle&0xffff, gpio)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GMODE, 8, ext, L=2))

   def gpio_claim_input(self, handle, gpio, lFlags=0):
      """
      This claims a GPIO for input.

      handle:= >= 0 (as returned by [*gpiochip_open*]).
        gpio:= the GPIO to be claimed.
      lFlags:= line flags for the GPIO.

      If OK returns 0.

      On failure returns a negative error code.

      The line flags may be used to set the GPIO
      as active low, open drain, open source,
      pull up, pull down, pull off.

      ...
      sbc.gpio_claim_input(h, 23) # open GPIO 23 for input.
      ...
      """
      ext = [struct.pack("III", handle&0xffff, lFlags, gpio)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GSIX, 12, ext, L=3))

   def gpio_claim_output(self, handle, gpio, level=0, lFlags=0):
      """
      This claims a GPIO for output.

      handle:= >= 0 (as returned by [*gpiochip_open*]).
        gpio:= the GPIO to be claimed.
       level:= the initial value for the GPIO.
      lFlags:= line flags for the GPIO.

      If OK returns 0.

      On failure returns a negative error code.

      The line flags may be used to set the GPIO
      as active low, open drain, open source,
      pull up, pull down, pull off.

      If level is zero the GPIO will be initialised low (0).  If any other
      value is used the GPIO will be initialised high (1).

      ...
      sbc.gpio_claim_output(h, 3) # open GPIO 3 for low output.
      ...
      """
      ext = [struct.pack("IIII", handle&0xffff, lFlags, gpio, level)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GSOX, 16, ext, L=4))

   def gpio_free(self, handle, gpio):
      """
      This frees a GPIO.

      handle:= >= 0 (as returned by [*gpiochip_open*]).
        gpio:= the GPIO to be freed.

      If OK returns 0.

      On failure returns a negative error code.

      The GPIO may now be claimed by another user or for
      a different purpose.
      """
      ext = [struct.pack("II", handle&0xffff, gpio)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GSF, 8, ext, L=2))

   def group_claim_input(self, handle, gpio, lFlags=0):
      """
      This claims a group of GPIO for inputs.

      handle:= >= 0 (as returned by [*gpiochip_open*]).
       gpios:= a list of GPIO to be claimed.
      lFlags:= line flags for the group of GPIO.

      If OK returns 0.

      On failure returns a negative error code.

      The line flags may be used to set the group
      as active low, open drain, open source,
      pull up, pull down, pull off.

      gpio is a list of one or more GPIO.  The first GPIO in the
      list is called the group leader and is used to reference the
      group as a whole.

      """
      if len(gpio):
         ext = bytearray()
         ext.extend(struct.pack("II", handle&0xffff, lFlags))
         for g in gpio:
            ext.extend(struct.pack("I", g))
         return _u2i(_lg_command_ext(
            self.sl, _CMD_GSGIX, (len(gpio)+2)*4, [ext], L=len(gpio)+2))
      else:
         return 0

   def group_claim_output(self, handle, gpio, levels=[0], lFlags=0):
      """
      This claims a group of GPIO for outputs.

      handle:= >= 0 (as returned by [*gpiochip_open*]).
        gpio:= a list of GPIO to be claimed.
      levels:= a list of the initial value for each GPIO.
      lFlags:= line flags for the group of GPIO.

      If OK returns 0.

      On failure returns a negative error code.

      The line flags may be used to set the group
      as active low, open drain, open source,
      pull up, pull down, pull off.

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
         ext = bytearray()
         ext.extend(struct.pack("II", handle&0xffff, lFlags))
         for g in gpio:
            ext.extend(struct.pack("I", g))
         for v in range(len(gpio)):
            ext.extend(struct.pack("I", levels[v]))
         return _u2i(_lg_command_ext(
            self.sl, _CMD_GSGOX,
            (2+(len(gpio)*2))*4, [ext], L=2+(len(gpio)*2)))
      else:
         return 0

   def group_free(self, handle, gpio):
      """
      This frees all the GPIO associated with a group.

      handle:= >= 0 (as returned by [*gpiochip_open*]).
        gpio:= the group leader.

      If OK returns 0.

      On failure returns a negative error code.

      The GPIO may now be claimed by another user or for a different purpose.

      """
      ext = [struct.pack("II", handle&0xffff, gpio)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GSGF, 8, ext, L=2))

   def gpio_read(self, handle, gpio):
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
      ext = [struct.pack("II", handle&0xffff, gpio)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GR, 8, ext, L=2))

   def gpio_write(self, handle, gpio, level):
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
      ext = [struct.pack("III", handle&0xffff, gpio, level)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GW, 12, ext, L=3))


   def group_read(self, handle, gpio):
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
      ext = [struct.pack("II", handle&0xffff, gpio)]
      status = CMD_INTERRUPTED
      levels = 0
      with self.sl.l:
         bytes = u2i(
            _lg_command_ext_nolock(self.sl, _CMD_GGR, 8, ext, L=2))
         if bytes > 0:
            data = self._rxbuf(bytes)
            levels, status = struct.unpack('QI', _str(data))
         else:
            status = bytes
      return _u2i_list([status, levels])

   def group_write(self, handle, gpio, group_bits, group_mask=GROUP_ALL):
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
      ext = [struct.pack(
         "QQII", group_bits, group_mask, handle&0xffff, gpio)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GGWX, 24, ext, Q=2, L=2))


   def tx_pulse(self, handle, gpio,
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
      ext = [struct.pack("IIIIII", handle&0xffff, gpio,
         pulse_on, pulse_off, pulse_offset, pulse_cycles)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GPX, 24, ext, L=6))


   def tx_pwm(self, handle, gpio,
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
      ext = [struct.pack("IIIIII", handle&0xffff, gpio,
         int(pwm_frequency*1000), int(pwm_duty_cycle*1000),
         pulse_offset, pulse_cycles)]
      return _u2i(_lg_command_ext(self.sl, _CMD_PX, 24, ext, L=6))


   def tx_servo(self, handle, gpio, pulse_width,
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
      ext = [struct.pack("IIIIII", handle&0xffff, gpio,
         pulse_width, servo_frequency, pulse_offset, pulse_cycles)]
      return _u2i(_lg_command_ext(self.sl, _CMD_SX, 24, ext, L=6))


   def tx_wave(self, handle, gpio, pulses):
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
         q = 3 * len(pulses)
         l = 2
         size = (q*8) + (l*4)
         ext1 = bytearray()
         for p in pulses:
            ext1.extend(struct.pack(
               "QQQ", p.group_bits, p.group_mask, p.pulse_delay))
         ext2 = struct.pack("II", handle&0xffff, gpio)
         ext = [ext1, ext2]
         return _u2i(_lg_command_ext(self.sl, _CMD_GWAVE, size, ext, Q=q, L=l))
      else:
         return 0


   def tx_busy(self, handle, gpio, kind):
      """
      This returns true if transmissions of the specified kind
      are active on the GPIO or group.

      handle:= >= 0 (as returned by [*gpiochip_open*]).
        gpio:= the GPIO or group to be checked.
        kind:= TX_PWM or TX_WAVE.

      If OK returns 1 for busy and 0 for not busy.

      On failure returns a negative error code.

      """
      ext = [struct.pack("III", handle&0xffff, gpio, kind)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GBUSY, 12, ext, L=3))

   def tx_room(self, handle, gpio, kind):
      """
      This returns the number of slots there are to queue further
      transmissions of the specified kind on a GPIO or group.

      handle:= >= 0 (as returned by [*gpiochip_open*]).
        gpio:= the GPIO or group to be checked.
        kind:= TX_PWM or TX_WAVE.

      If OK returns the number of free entries (0 for none).

      On failure returns a negative error code.

      """
      ext = [struct.pack("III", handle&0xffff, gpio, kind)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GROOM, 12, ext, L=3))

   def gpio_set_debounce_micros(self, handle, gpio, debounce_micros):
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
      ext = [struct.pack("III", handle&0xffff, gpio, debounce_micros)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GDEB, 12, ext, L=3))


   def gpio_set_watchdog_micros(self, handle, gpio, watchdog_micros):
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
      ext = [struct.pack("III", handle&0xffff, gpio, watchdog_micros)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GWDOG, 12, ext, L=3))


   def gpio_claim_alert(
      self, handle, gpio, eFlags, lFlags=0, notify_handle=None):
      """
      This claims a GPIO to be used as a source of alerts on level changes.

              handle:= >= 0 (as returned by [*gpiochip_open*]).
                gpio:= >= 0, as legal for the gpiochip.  
              eFlags:= event flags for the GPIO.
              lFlags:= line flags for the GPIO.
      notifiy_handle: >=0 (as returned by [*notify_open*]).

      If OK returns 0.

      On failure returns a negative error code.

      The line flags may be used to set the GPIO
      as active low, open drain, open source,
      pull up, pull down, pull off.

      The event flags are used to generate alerts for a rising edge,
      falling edge, or both edges.

      Use the default notification handle of None unless you plan
      to read the alerts from a notification pipe you have opened.

      """
      if notify_handle is None:
         notify_handle = self._notify.handle
      ext = [struct.pack(
         "IIIII", handle&0xffff, lFlags, eFlags, gpio, notify_handle)]
      return _u2i(_lg_command_ext(self.sl, _CMD_GSAX, 20, ext, L=5))



   def callback(self, handle, gpio, edge=RISING_EDGE, func=None):
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

      Early kernels used to provide a timestamp as the number of nanoseconds
      since the Epoch (start of 1970).  Later kernels use the number of
      nanoseconds since boot.  It's probably best not to make any assumption
      as to the timestamp origin.

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

      cb1 = sbc.callback(0, 22, rgpio.BOTH_EDGES, cbf)

      cb2 = sbc.callback(0, 4, rgpio.BOTH_EDGES)

      cb3 = sbc.callback(0, 17)

      print(cb3.tally())

      cb3.reset_tally()

      cb1.cancel() # To cancel callback cb1.
      ...
      """
      return _callback(self._notify, handle>>16, gpio, edge, func)


   # I2C

   def i2c_open(self, i2c_bus, i2c_address, i2c_flags=0):
      """
      Returns a handle (>= 0) for the device at the I2C bus address.

      This is a privileged command. See [+Permits+].

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
      ext = [struct.pack("III", i2c_bus, i2c_address, i2c_flags)]
      return _u2i(_lg_command_ext(self.sl, _CMD_I2CO, 12, ext, L=3))

   def i2c_close(self, handle):
      """
      Closes the I2C device.

      handle:= >= 0 (as returned by [*i2c_open*]).

      If OK returns 0.

      On failure returns a negative error code.

      ...
      sbc.i2c_close(h)
      ...
      """
      ext = [struct.pack("I", handle)]
      return _u2i(_lg_command_ext(self.sl, _CMD_I2CC, 4, ext, L=1))

   def i2c_write_quick(self, handle, bit):
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
      ext = [struct.pack("II", handle, bit)]
      return _u2i(_lg_command_ext(self.sl, _CMD_I2CWQ, 8, ext, L=2))

   def i2c_write_byte(self, handle, byte_val):
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
      ext = [struct.pack("II", handle, byte_val)]
      return _u2i(_lg_command_ext(self.sl, _CMD_I2CWS, 8, ext, L=2))

   def i2c_read_byte(self, handle):
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
      ext = [struct.pack("I", handle)]
      return _u2i(_lg_command_ext(self.sl, _CMD_I2CRS, 4, ext, L=1))

   def i2c_write_byte_data(self, handle, reg, byte_val):
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
      # send byte 0xC5 to reg 2 of handle 1
      sbc.i2c_write_byte_data(1, 2, 0xC5)

      # send byte 9 to reg 4 of handle 2
      sbc.i2c_write_byte_data(2, 4, 9)
      ...
      """
      ext = [struct.pack("III", handle, reg, byte_val)]
      return _u2i(_lg_command_ext(self.sl, _CMD_I2CWB, 12, ext, L=3))

   def i2c_write_word_data(self, handle, reg, word_val):
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
      # send word 0xA0C5 to reg 5 of handle 4
      sbc.i2c_write_word_data(4, 5, 0xA0C5)

      # send word 2 to reg 2 of handle 5
      sbc.i2c_write_word_data(5, 2, 23)
      ...
      """
      ext = [struct.pack("III", handle, reg, word_val)]
      return _u2i(_lg_command_ext(self.sl, _CMD_I2CWW, 12, ext, L=3))

   def i2c_read_byte_data(self, handle, reg):
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
      # read byte from reg 17 of handle 2
      b = sbc.i2c_read_byte_data(2, 17)

      # read byte from reg  1 of handle 0
      b = sbc.i2c_read_byte_data(0, 1)
      ...
      """
      ext = [struct.pack("II", handle, reg)]
      return _u2i(_lg_command_ext(self.sl, _CMD_I2CRB, 8, ext, L=2))

   def i2c_read_word_data(self, handle, reg):
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
      # read word from reg 2 of handle 3
      w = sbc.i2c_read_word_data(3, 2)

      # read word from reg 7 of handle 2
      w = sbc.i2c_read_word_data(2, 7)
      ...
      """
      ext = [struct.pack("II", handle, reg)]
      return _u2i(_lg_command_ext(self.sl, _CMD_I2CRW, 8, ext, L=2))

   def i2c_process_call(self, handle, reg, word_val):
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
      ext = [struct.pack("III", handle, reg, word_val)]
      return _u2i(_lg_command_ext(self.sl, _CMD_I2CPC, 12, ext, L=3))

   def i2c_write_block_data(self, handle, reg, data):
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
      ext = [struct.pack("II", handle, reg)] + [data]
      return _u2i(_lg_command_ext(self.sl, _CMD_I2CWK, 8+len(data), ext, L=2))

   def i2c_read_block_data(self, handle, reg):
      """
      Reads a block of up to 32 bytes from the specified register of
      the device.

      handle:= >= 0 (as returned by [*i2c_open*]).
         reg:= >= 0, the device register.

      If OK returns a list of the number of bytes read and a
      bytearray containing the bytes.

      On failure returns a list of a negative error code and
      a null string.

      SMBus 2.0 5.5.7 - Block read.
      . .
      S Addr Wr [A] reg [A]
         S Addr Rd [A] [Count] A [Data] A [Data] A ... A [Data] NA P
      . .

      The amount of returned data is set by the device.

      ...
      (b, d) = sbc.i2c_read_block_data(h, 10)
      if b >= 0:
         # process data
      else:
         # process read failure
      ...
      """
      bytes = CMD_INTERRUPTED
      rdata = ""
      ext = [struct.pack("II", handle, reg)]
      with self.sl.l:
         bytes = u2i(_lg_command_ext_nolock(self.sl, _CMD_I2CRK, 8, ext, L=2))
         if bytes > 0:
            rdata = self._rxbuf(bytes)
      return _u2i_list([bytes, rdata])

   def i2c_block_process_call(self, handle, reg, data):
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
      bytes = CMD_INTERRUPTED
      rdata = ""
      ext = [struct.pack("II", handle, reg)] + [data]
      with self.sl.l:
         bytes = u2i(_lg_command_ext_nolock(self.sl, _CMD_I2CPK, 8+len(data), ext, L=2))
         if bytes > 0:
            rdata = self._rxbuf(bytes)
      return _u2i_list([bytes, rdata])

   def i2c_write_i2c_block_data(self, handle, reg, data):
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
      ext = [struct.pack("II", handle, reg)] + [data]
      return _u2i(_lg_command_ext(self.sl, _CMD_I2CWI, 8+len(data), ext, L=2))

   def i2c_read_i2c_block_data(self, handle, reg, count):
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
         # process data
      else:
         # process read failure
      ...
      """
      bytes = CMD_INTERRUPTED
      rdata = ""
      ext = [struct.pack("III", handle, reg, count)]
      with self.sl.l:
         bytes = u2i(_lg_command_ext_nolock(self.sl, _CMD_I2CRI, 12, ext, L=3))
         if bytes > 0:
            rdata = self._rxbuf(bytes)
      return _u2i_list([bytes, rdata])

   def i2c_read_device(self, handle, count):
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
      bytes = CMD_INTERRUPTED
      rdata = ""
      ext = [struct.pack("II", handle, count)]
      with self.sl.l:
         bytes = u2i(
            _lg_command_ext_nolock(self.sl, _CMD_I2CRD, 8, ext, L=2))
         if bytes > 0:
            rdata = self._rxbuf(bytes)
      return _u2i_list([bytes, rdata])

   def i2c_write_device(self, handle, data):
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
      ext = [struct.pack("I", handle)] + [data]
      return _u2i(_lg_command_ext(self.sl, _CMD_I2CWD, 4+len(data), ext, L=1))


   def i2c_zip(self, handle, data):
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
      bytes = CMD_INTERRUPTED
      rdata = ""
      ext = [struct.pack("I", handle)] + [data]
      with self.sl.l:
         bytes = u2i(_lg_command_ext_nolock(
            self.sl, _CMD_I2CZ, 4+len(data), ext, L=1))
         if bytes > 0:
            rdata = self._rxbuf(bytes)
      return _u2i_list([bytes, rdata])

   # NOTIFICATIONS

   def notify_open(self):
      """
      Opens a notification pipe.

      This is a privileged command. See [+Permits+].

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

      timestamp: the number of nanoseconds since a kernel dependent origin.

      Early kernels used to provide a timestamp as the number of nanoseconds
      since the Epoch (start of 1970).  Later kernels use the number of
      nanoseconds since boot.  It's probably best not to make any assumption
      as to the timestamp origin.

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
      return _u2i(_lg_command(self.sl, _CMD_NO))

   def notify_pause(self, handle):
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
      ext = [struct.pack("I", handle)]
      return _u2i(_lg_command_ext(self.sl, _CMD_NP, 4, ext, L=1))

   def notify_resume(self, handle):
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
      ext = [struct.pack("I", handle)]
      return _u2i(_lg_command_ext(self.sl, _CMD_NR, 4, ext, L=1))

   def notify_close(self, handle):
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
      ext = [struct.pack("I", handle)]
      return _u2i(_lg_command_ext(self.sl, _CMD_NC, 4, ext, L=1))

   # SCRIPTS

   def script_store(self, script):
      """
      Store a script for later execution.

      This is a privileged command. See [+Permits+].

      script:= the script text as a series of bytes.

      If OK returns a handle (>= 0).

      On failure returns a negative error code.

      ...
      h = sbc.script_store(
         b'tag 0 w 22 1 mils 100 w 22 0 mils 100 dcr p0 jp 0')
      ...
      """
      if len(script):
         return _u2i(_lg_command_ext(
            self.sl, _CMD_PROC, len(script)+1, [script+'\0']))
      else:
         return 0

   def script_run(self, handle, params=None):
      """
      Runs a stored script.

      handle:= >=0 (as returned by [*script_store*]).
      params:= up to 10 parameters required by the script.

      If OK returns 0.

      On failure returns a negative error code.

      ...
      s = sbc.script_run(h, [par1, par2])

      s = sbc.script_run(h)

      s = sbc.script_run(h, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
      ...
      """
      ext = struct.pack("I", handle)
      nump = 1
      if params is not None:
         for p in params:
            ext += struct.pack("I", p)
         nump = 1 + len(params)
      return _u2i(_lg_command_ext(self.sl, _CMD_PROCR, nump*4, [ext], L=nump))

   def script_update(self, handle, params=None):
      """
      Sets the parameters of a script.  The script may or
      may not be running.  The parameters of the script are
      overwritten with the new values.

      handle:= >=0 (as returned by [*script_store*]).
      params:= up to 10 parameters required by the script.

      If OK returns 0.

      On failure returns a negative error code.

      ...
      s = sbc.script_update(h, [par1, par2])

      s = sbc.script_update(h, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
      ...
      """
      ext = struct.pack("I", handle)
      nump = 1
      if params is not None:
         for p in params:
            ext += struct.pack("I", p)
         nump = 1 + len(params)
      return _u2i(_lg_command_ext(self.sl, _CMD_PROCU, nump*4, [ext], L=nump))

   def script_status(self, handle):
      """
      Returns the run status of a stored script as well as the
      current values of parameters 0 to 9.

      handle:= >=0 (as returned by [*script_store*]).

      If OK returns a list of the run status and a list of
      the 10 parameters.

      On failure returns a negative error code and a null list.

      The run status may be

      . .
      SCRIPT_INITING
      SCRIPT_READY
      SCRIPT_RUNNING
      SCRIPT_WAITING
      SCRIPT_ENDED
      SCRIPT_HALTED
      SCRIPT_FAILED
      . .

      ...
      (s, pars) = sbc.script_status(h)
      ...
      """
      status = CMD_INTERRUPTED
      params = ()
      ext = [struct.pack("I", handle)]
      with self.sl.l:
         bytes = u2i(
            _lg_command_ext_nolock(self.sl, _CMD_PROCP, 4, ext, L=1))
         if bytes > 0:
            data = self._rxbuf(bytes)
            pars = struct.unpack('11i', _str(data))
            status = pars[0]
            params = pars[1:]
         else:
            status = bytes
      return _u2i_list([status, params])

   def script_stop(self, handle):
      """
      Stops a running script.

      handle:= >=0 (as returned by [*script_store*]).

      If OK returns 0.

      On failure returns a negative error code.

      ...
      status = sbc.script_stop(h)
      ...
      """
      ext = [struct.pack("I", handle)]
      return _u2i(_lg_command_ext(self.sl, _CMD_PROCS, 4, ext, L=1))

   def script_delete(self, handle):
      """
      Deletes a stored script.

      handle:= >=0 (as returned by [*script_store*]).

      If OK returns 0.

      On failure returns a negative error code.

      ...
      status = sbc.script_delete(h)
      ...
      """
      ext = [struct.pack("I", handle)]
      return _u2i(_lg_command_ext(self.sl, _CMD_PROCD, 4, ext, L=1))

   # SERIAL

   def serial_open(self, tty, baud, ser_flags=0):
      """
      Returns a handle for the serial tty device opened
      at baud bits per second.

      This is a privileged command. See [+Permits+].

            tty:= the serial device to open.
           baud:= baud rate in bits per second, see below.
      ser_flags:= 0, no flags are currently defined.

      If OK returns a handle (>= 0).

      On failure returns a negative error code.

      The baud rate must be one of 50, 75, 110, 134, 150,
      200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200,
      38400, 57600, 115200, or 230400.

      ...
      h1 = sbc.serial_open("/dev/ttyAMA0", 300)

      h2 = sbc.serial_open("/dev/ttyUSB1", 19200, 0)

      h3 = sbc.serial_open("/dev/serial0", 9600)
      ...
      """
      ext = [struct.pack("II", baud, ser_flags)] + [tty]
      return _u2i(_lg_command_ext(self.sl, _CMD_SERO, 8+len(tty), ext, L=2))

   def serial_close(self, handle):
      """
      Closes the serial device.

      handle:= >= 0 (as returned by [*serial_open*]).

      If OK returns 0.

      On failure returns a negative error code.

      ...
      sbc.serial_close(h1)
      ...
      """
      ext = [struct.pack("I", handle)]
      return _u2i(_lg_command_ext(self.sl, _CMD_SERC, 4, ext, L=1))

   def serial_read_byte(self, handle):
      """
      Returns a single byte from the device.

      handle:= >= 0 (as returned by [*serial_open*]).

      If OK returns the read byte (0-255).

      On failure returns a negative error code.

      ...
      b = sbc.serial_read_byte(h1)
      ...
      """
      ext = [struct.pack("I", handle)]
      return _u2i(_lg_command_ext(self.sl, _CMD_SERRB, 4, ext, L=1))

   def serial_write_byte(self, handle, byte_val):
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
      ext = [struct.pack("II", handle, byte_val)]
      return _u2i(
         _lg_command_ext(self.sl, _CMD_SERWB, 8, ext, L=2))

   def serial_read(self, handle, count=1000):
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
         # process read data
      ...
      """
      bytes = CMD_INTERRUPTED
      rdata = ""
      ext = [struct.pack("II", handle, count)]
      with self.sl.l:
         bytes = u2i(
            _lg_command_ext_nolock(self.sl, _CMD_SERR, 8, ext, L=2))
         if bytes > 0:
            rdata = self._rxbuf(bytes)
      return _u2i_list([bytes, rdata])

   def serial_write(self, handle, data):
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
      ext = [struct.pack("I", handle)] + [data]
      return _u2i(_lg_command_ext(self.sl, _CMD_SERW, 4+len(data), ext, L=1))

   def serial_data_available(self, handle):
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
      ext = [struct.pack("I", handle)]
      return _u2i(_lg_command_ext(self.sl, _CMD_SERDA, 4, ext, L=1))


   # SHELL

   def shell(self, shellscr, pstring=""):
      """
      This function uses the system call to execute a shell script
      with the given string as its parameter.

      This is a privileged command. See [+Permits+].

      shellscr:= the name of the script, only alphanumerics,
                    '-' and '_' are allowed in the name
      pstring := the parameter string to pass to the script

      If OK returns the exit status of the system call.

      On failure returns a negative error code.

      shellscr must exist in a directory named cgi in the daemon's
      configuration directory and must be executable.

      The returned exit status is normally 256 times that set by
      the shell script exit function.  If the script can't be
      found 32512 will be returned.

      The following table gives some example returned statuses:

      Script exit status @ Returned system call status
      1                  @ 256
      5                  @ 1280
      10                 @ 2560
      200                @ 51200
      script not found   @ 32512

      ...
      // pass two parameters, hello and world
      status = sbc.shell("scr1", "hello world");

      // pass three parameters, hello, string with spaces, and world
      status = sbc.shell("scr1", "hello 'string with spaces' world");

      // pass one parameter, hello string with spaces world
      status = sbc.shell("scr1", "\\"hello string with spaces world\\"");
      ...
      """
      ls = len(shellscr)+1
      lp = len(pstring)+1
      ext = [struct.pack("I", ls)] + [shellscr+'\x00'+pstring+'\x00']
      return _u2i(_lg_command_ext(self.sl, _CMD_SHELL, 4+ls+lp, ext, L=1))

   # SPI

   def spi_open(self, spi_device, spi_channel, baud, spi_flags=0):
      """
      Returns a handle for the SPI device on the channel.  Data
      will be transferred at baud bits per second.  The flags
      may be used to modify the default behaviour.

      This is a privileged command. See [+Permits+].

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
      # open SPI device on channel 1 in mode 3 at 50000 bits per second

      h = sbc.spi_open(1, 50000, 3)
      ...
      """
      ext = [struct.pack("IIII", spi_device, spi_channel, baud, spi_flags)]
      return _u2i(_lg_command_ext(self.sl, _CMD_SPIO, 16, ext, L=4))

   def spi_close(self, handle):
      """
      Closes the SPI device.

      handle:= >= 0 (as returned by [*spi_open*]).

      If OK returns 0.

      On failure returns a negative error code.

      ...
      sbc.spi_close(h)
      ...
      """
      ext = [struct.pack("I", handle)]
      return _u2i(_lg_command_ext(self.sl, _CMD_SPIC, 4, ext, L=1))

   def spi_read(self, handle, count):
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
         # process read data
      else:
         # error path
      ...
      """
      bytes = CMD_INTERRUPTED
      rdata = ""
      ext = [struct.pack("II", handle, count)]
      with self.sl.l:
         bytes = u2i(_lg_command_ext_nolock(self.sl, _CMD_SPIR, 8, ext, L=2))
         if bytes > 0:
            rdata = self._rxbuf(bytes)
      return _u2i_list([bytes, rdata])

   def spi_write(self, handle, data):
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
      # I p1 handle
      # I p2 0
      # I p3 len
      ## extension ##
      # s len data bytes
      ext = [struct.pack("I", handle)] + [data]
      return _u2i(_lg_command_ext(self.sl, _CMD_SPIW, 4+len(data), ext, L=1))

   def spi_xfer(self, handle, data):
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
      # I p1 handle
      # I p2 0
      # I p3 len
      ## extension ##
      # s len data bytes

      bytes = CMD_INTERRUPTED
      rdata = ""
      ext = [struct.pack("I", handle)] + [data]
      with self.sl.l:
         bytes = u2i(_lg_command_ext_nolock(
            self.sl, _CMD_SPIX, 4+len(data), ext, L=1))
         if bytes > 0:
            rdata = self._rxbuf(bytes)
      return _u2i_list([bytes, rdata])


   # UTILITIES

   def get_sbc_name(self):
      """
      Returns the name of the sbc running the rgpiod daemon.

      If OK returns the SBC host name.

      On failure returns a null string.

      ...
      server = sbc.get_sbc_name()
      print(server)
      ...
      """
      bytes = CMD_INTERRUPTED
      rdata = ""
      with self.sl.l:
         bytes = u2i(
            _lg_command_nolock(self.sl, _CMD_SBC))
         if bytes > 0:
            rdata = self._rxbuf(bytes)
         else:
            rdata = ""
      return rdata

   def set_user(self, user="default",
      secretsFile=os.path.expanduser("~/.lg_secret")):
      """
      Sets the rgpiod daemon user.  The user then has the
      associated permissions.

             user:= the user to set (defaults to the default user).
      secretsFile:= the path to the shared secret file (defaults to
                    .lg_secret in the users home directory).

      If OK returns True if the user was set, False if not.

      On failure returns a negative error code.

      The returned value is True if permission is granted.

      ...
      if sbc.set_user("gpio"):
         print("using user gpio permissions")
      else:
         print("using default permissions")
      ...
      """

      user = user.strip()

      if user == "":
         user = "default"

      secret = bytearray()

      with open(secretsFile) as f:
         for line in f:
            l = line.split("=")
            if len(l) == 2:
               if l[0].strip() == user:
                  secret = bytearray(l[1].strip().encode('utf-8'))
                  break

      bytes = CMD_INTERRUPTED

      with self.sl.l:

         salt1 = "{:015x}".format((int(time.time()*1e7))&0xfffffffffffffff)
         ext = salt1 + '.' + user
         bytes = u2i(_lg_command_ext_nolock(
            self.sl, _CMD_USER, len(ext), [ext]))

         if bytes < 0:
            return bytes

         salt1 = bytearray(salt1.encode('utf-8'))
         salt2 = self._rxbuf(bytes)[:15]

         pwd=""

         h = hashlib.md5()
         h.update(salt1 + secret + salt2)
         pwd = h.hexdigest()

         res = u2i(_lg_command_ext_nolock(
            self.sl, _CMD_PASSW, len(pwd), [pwd]))

      return res

   def set_share_id(self, handle, share_id):
      """
      Starts or stops sharing of an object.

        handle:= >=0
      share_id:= >= 0, 0 stops sharing.

      If OK returns 0.

      On failure returns a negative error code.

      Normally objects associated with a handle are only accessible
      to the Python script which created them (and are automatically
      deleted when the script ends).

      If a non-zero share is set the object is accessible to any
      software which knows the share (and are not automatically
      deleted when the script ends).

      ...
      sbc.share_set(h, 23)
      ...
      """
      ext = [struct.pack("II", handle, share_id)]
      return _u2i(_lg_command_ext(self.sl, _CMD_SHRS, 8, ext, L=2))

   def use_share_id(self, share_id):
      """
      Starts or stops sharing of an object.

      share_id:= >= 0, 0 stops sharing.

      If OK returns 0.

      On failure returns a negative error code.

      Normally objects associated with a handle are only accessible
      to the Python script which created them (and are automatically
      deleted when the script ends).

      If a non-zero share is set the object is accessible to any
      software which knows the share and the object handle.

      ...
      sbc.share_use(23)
      ...
      """
      ext = [struct.pack("I", share_id)]
      return _u2i(_lg_command_ext(self.sl, _CMD_SHRU, 4, ext, L=1))

   def get_internal(self, config_id):
      """
      Returns the value of a configuration item.

      This is a privileged command. See [+Permits+].

      If OK returns a list of 0 (OK) and the item's value.

      On failure returns a list of negative error code and None.

      config_id:= the configuration item.

      ...
      cfg = sbc.get_internal(0)
      print(cfg)
      ...
      """
      ext = [struct.pack("I", config_id)]
      status = CMD_INTERRUPTED
      config_value = None
      with self.sl.l:
         bytes = u2i(
            _lg_command_ext_nolock(self.sl, _CMD_CGI, 4, ext, L=1))
         if bytes > 0:
            data = self._rxbuf(bytes)
            config_value = struct.unpack('Q', _str(data))[0]
            status = OKAY
         else:
            status = bytes
      return _u2i_list([status, config_value])

   def set_internal(self, config_id, config_value):
      """
      Sets the value of a sbc internal.

      This is a privileged command. See [+Permits+].

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
      ext = [struct.pack("QI", config_value, config_id)]
      return _u2i(_lg_command_ext(self.sl, _CMD_CSI, 12, ext, Q=1, L=1))


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


   connected:
   True if a connection was established, False otherwise.

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
   Indicates an error.  Use [*rgpio.error_text*] for the error text.

   file_mode:
   The mode may have the following values

   . .
   FILE_READ   1
   FILE_WRITE  2
   FILE_RW     3
   . .

   The following values can be or'd into the file open mode

   . .
   FILE_APPEND 4
   FILE_CREATE 8
   FILE_TRUNC  16
   . .

   file_name:
   A full file path.  To be accessible the path must match
   an entry in the [files] section of the permits file.

   fpattern:
   A file path which may contain wildcards.  To be accessible the path
   must match an entry in the [files] section of the permits file.

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

   [*file_open*] 
   [*gpiochip_open*] 
   [*i2c_open*] 
   [*notify_open*] 
   [*serial_open*] 
   [*script_store*] 
   [*spi_open*]

   host:
   The name or IP address of the sbc running the rgpiod daemon.

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
   SET_PULL_UP
   SET_PULL_DOWN
   SET_PULL_NONE
   . .

   notify_handle:
   This associates a notification with a GPIO alert.

   params: 32 bit number
   When scripts are started they can receive up to 10 parameters
   to define their operation.

   port:
   The port used by the rgpiod daemon, defaults to 8889.

   pstring:
   The string to be passed to a [*shell*] script to be executed.

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

   script:
   The text of a script to store on the rgpiod daemon.

   secretsFile:
   The file containing the shared secret for a user.  If the shared
   secret for a user matches that known by the rgpiod daemon the user can
   "log in" to the daemon.

   seek_from: 0-2
   Direction to seek for [*file_seek*].

   . .
   FROM_START=0
   FROM_CURRENT=1
   FROM_END=2
   . .

   seek_offset:
   The number of bytes to move forward (positive) or backwards
   (negative) from the seek position (start, current, or end of file).

   ser_flags: 32 bit
   No serial flags are currently defined.

   servo_frequency:: 40-500 Hz
   Servo pulse frequency

   share_id:
   Objects created with a non-zero share_id are persistent and may be
   used by other software which knows the share_id.

   shellscr:
   The name of a shell script.  The script must exist
   in the cgi directory of the rgpiod daemon's configuration
   directory and must be executable.

   show_errors:
   Controls the display of rgpiod daemon connection failures.
   The default of True prints the probable failure reasons to
   standard output.

   spi_channel: >= 0
   A SPI channel.

   spi_device: >= 0
   A SPI device.

   spi_flags: 32 bit
   See [*spi_open*].

   tty:
   A serial device, e.g. /dev/ttyAMA0, /dev/ttyUSB0

   uint32:
   An unsigned 32 bit number.

   user:
   A name known by the rgpiod daemon and associated with a set of user
   permissions.

   watchdog_micros:
   The watchdog time in microseconds.

   word_val: 0-65535
   A whole number.
   """
   pass

