#if defined(SWIGPYTHON)

%define lgpio_docstr
"
[http://abyz.me.uk/lg/py_lgpio.html]

lgpio is a Python module which allows control of the GPIO
of a Linux SBC.

*Features*

o reading and writing GPIO singly and in groups
o software timed PWM and waves
o GPIO callbacks
o pipe notification of GPIO alerts
o I2C wrapper
o SPI wrapper
o serial link wrapper

*Exceptions*

By default a fatal exception is raised if you pass an invalid
argument to a lgpio function.

If you wish to handle the returned status yourself you should set
lgpio.exceptions to False.

You may prefer to check the returned status in only a few parts
of your code.  In that case do the following:

...
lgpio.exceptions = False

# Code where you want to test the error status

lgpio.exceptions = True
...

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

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>

OVERVIEW

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

SERIAL

serial_open               Opens a serial device
serial_close              Closes a serial device

serial_read_byte          Reads a byte from a serial device
serial_write_byte         Writes a byte to a serial device

serial_read               Reads bytes from a serial device
serial_write              Writes bytes to a serial device

serial_data_available     Returns number of bytes ready to be read

SPI

spi_open                  Opens a SPI device
spi_close                 Closes a SPI device

spi_read                  Reads bytes from a SPI device
spi_write                 Writes bytes to a SPI device
spi_xfer                  Transfers bytes with a SPI device

UTILITIES

get_internal              Get an internal configuration value
set_internal              Set an internal configuration value

get_module_version        Get the lgpio Python module version
error_text                Get the error text for an error code
"
%enddef

%module (docstring = lgpio_docstr) lgpio

%{
#include "lgpio.h"
%}

%include "typemaps.i"
%include "stdint.i"
%include "pybuffer.i"

%pythoncode "lgpio_extra.py"

// lgGroupClaimInput
// lgGroupClaimOutput
%typemap(in) (int count, const int *gpios)
{
   int res;
   Py_buffer view;

   if (!PyObject_CheckBuffer($input))
   {
      PyErr_SetString(PyExc_ValueError, "Expecting a buffer object");
      SWIG_fail;
   }

   res = PyObject_GetBuffer($input, &view, PyBUF_CONTIG_RO);
   $1 = view.len/4;
   $2 = view.buf;
   PyBuffer_Release(&view);

   if (res < 0)
   {
      PyErr_SetString(PyExc_ValueError, "Odd buffer object");
      SWIG_fail;
   }

   if (($1 < 1) || ($1 > 64))
   {
      PyErr_SetString(PyExc_ValueError,"Expecting 1-64 GPIO");
      SWIG_fail;
   }
}

// lgGroupClaimOutput
%typemap(in) (const int *levels)
{
   int res;
   Py_buffer view;

   if (!PyObject_CheckBuffer($input))
   {
      PyErr_SetString(PyExc_ValueError, "Expecting a buffer object");
      SWIG_fail;
   }

   res = PyObject_GetBuffer($input, &view, PyBUF_CONTIG_RO);
   $1 = view.buf;
   PyBuffer_Release(&view);

   if (res < 0)
   {
      PyErr_SetString(PyExc_ValueError, "Odd buffer object");
      SWIG_fail;
   }
}


// lgTxWave
%typemap(in) (int count, lgPulse_p pulses)
{
   int res;
   Py_buffer view;

   if (!PyObject_CheckBuffer($input))
   {
      PyErr_SetString(PyExc_ValueError, "Expecting a buffer object");
      SWIG_fail;
   }

   res = PyObject_GetBuffer($input, &view, PyBUF_CONTIG_RO);
   $1 = view.len/24;
   $2 = view.buf;
   PyBuffer_Release(&view);

   if (res <0)
   {
      PyErr_SetString(PyExc_ValueError, "Odd buffer object");
      SWIG_fail;
   }
}

// lgI2cWriteBlockData
// lgI2cWriteI2CBlockData
// lgI2cWriteDevice
// lgSerialWrite
// lgSpiWrite
%typemap(in) (const char *txBuf, int count)
{
   int res;
   Py_buffer view;

   if (!PyObject_CheckBuffer($input))
   {
      PyErr_SetString(PyExc_ValueError, "Expecting a buffer object");
      SWIG_fail;
   }

   res = PyObject_GetBuffer($input, &view, PyBUF_CONTIG_RO);
   $1 = view.buf;
   $2 = view.len;
   PyBuffer_Release(&view);

   if (res <0)
   {
      PyErr_SetString(PyExc_ValueError, "Odd buffer object");
      SWIG_fail;
   }
}

// lgI2cReadI2CBlockData
// lgI2cReadDevice
// lgSerialRead
// lgSpiRead
%typemap(in) (char *rxBuf, int count)
{
   if (!PyInt_Check($input))
   {
      PyErr_SetString(PyExc_ValueError, "Expecting an integer");
      SWIG_fail;
   }
   $2 = PyInt_AsLong($input);
   if ($2 < 0)
   {
      PyErr_SetString(PyExc_ValueError, "Positive integer expected");
      SWIG_fail;
   }
   $1 = (void *) malloc($2);
}

// lgI2cReadI2CBlockData
// lgI2cReadDevice
// lgSerialRead
// lgSpiRead
%typemap(argout) (char *rxBuf, int count)
{
   PyObject *o1, *o2;
   Py_XDECREF($result);   /* Blow away any previous result */
   $result = PyList_New(2);
   o1 = SWIG_From_int((int)(result));
   PyList_SetItem($result, 0, o1);
   if (result > 0) o2 = PyByteArray_FromStringAndSize($1, result);
   else o2 = PyByteArray_FromStringAndSize("", 0);
   PyList_SetItem($result, 1, o2);
   free($1);
}

// lgSpiXfer
%typemap(in) (const char *txBuf, char *rxBuf, int count)
{
   int res;
   Py_buffer view;

   if (!PyObject_CheckBuffer($input))
   {
      PyErr_SetString(PyExc_ValueError, "Expecting a buffer object");
      SWIG_fail;
   }

   res = PyObject_GetBuffer($input, &view, PyBUF_CONTIG_RO);
   $1 = view.buf;
   $3 = view.len;
   PyBuffer_Release(&view);

   if (res <0)
   {
      PyErr_SetString(PyExc_ValueError, "Odd buffer object");
      SWIG_fail;
   }

   $2 = (void *) malloc($3);
}

// lgSpiXfer
%typemap(argout) (const char *txBuf, char *rxBuf, int count)
{
   PyObject *o1, *o2;
   Py_XDECREF($result);   /* Blow away any previous result */

   $result = PyList_New(2);
   o1 = PyInt_FromLong(result);
   PyList_SetItem($result, 0, o1);

   if (result > 0) o2 = PyByteArray_FromStringAndSize($2, result);
   else o2 = PyByteArray_FromStringAndSize("", 0);
   PyList_SetItem($result, 1, o2);

   free($2);
}

// lgI2cBlockProcessCall
%typemap(in) (char *ioBuf, int count) (char rx32Buf[32])
{
   int res;
   char *buf;
   int len;
   int i;
   Py_buffer view;

   if (!PyObject_CheckBuffer($input))
   {
      PyErr_SetString(PyExc_ValueError, "Expecting a buffer object");
      SWIG_fail;
   }

   res = PyObject_GetBuffer($input, &view, PyBUF_CONTIG_RO);
   buf = view.buf;
   len = view.len;
   PyBuffer_Release(&view);

   if (res < 0)
   {
      PyErr_SetString(PyExc_ValueError, "Odd buffer object");
      SWIG_fail;
   }

   if (len > 32) len = 32;
   for (i=0; i<len; i++) rx32Buf[i] = buf[i];
   $1 = &rx32Buf[0];
   $2 = len;
}

// lgI2cBlockProcessCall
%typemap(argout) (char *ioBuf, int count)
{
   PyObject *o1, *o2;
   Py_XDECREF($result);   /* Blow away any previous result */
   $result = PyList_New(2);
   o1 = PyInt_FromLong(result);
   PyList_SetItem($result, 0, o1);
   if (result > 0) o2 = PyByteArray_FromStringAndSize($1, result);
   else o2 = PyByteArray_FromStringAndSize("", 0);
   PyList_SetItem($result, 1, o2);
}

// lgI2cReadBlockData
%typemap(in, numinputs=0) (char *rx32Buf) (char rx32Buf[32])
{
   $1 = &rx32Buf[0];
}

// lgI2cReadBlockData
%typemap(argout) (char *rx32Buf)
{
   PyObject *o1, *o2;
   Py_XDECREF($result);   /* Blow away any previous result */
   $result = PyList_New(2);

   o1 = PyInt_FromLong(result);
   PyList_SetItem($result, 0, o1);

   if (result > 0) o2 = PyByteArray_FromStringAndSize($1, result);
   else o2 = PyByteArray_FromStringAndSize("", 0);
   PyList_SetItem($result, 1, o2);
}

// lgI2cZip
%typemap(in) (const char *txBuf, int txCount, char *rxBuf, int rxCount)
{
   int res;
   Py_buffer view;

   if (!PyObject_CheckBuffer($input))
   {
      PyErr_SetString(PyExc_ValueError, "Expecting a buffer object");
      SWIG_fail;
   }

   res = PyObject_GetBuffer($input, &view, PyBUF_CONTIG_RO);
   $1 = view.buf;
   $2 = view.len;
   PyBuffer_Release(&view);

   if (res < 0)
   {
      PyErr_SetString(PyExc_ValueError, "Odd buffer object");
      SWIG_fail;
   }

   $3 = (void *) malloc(1000);
   $4 = 1000;
}

// lgI2cZip
%typemap(argout) (const char *txBuf, int txCount, char *rxBuf, int rxCount)
{
   PyObject *o1, *o2;
   Py_XDECREF($result);   /* Blow away any previous result */
   $result = PyList_New(2);
   o1 = SWIG_From_int((int)(result));
   PyList_SetItem($result, 0, o1);
   if (result > 0) o2 = PyByteArray_FromStringAndSize($3, result);
   else o2 = PyByteArray_FromStringAndSize("", 0);
   PyList_SetItem($result, 1, o2);
   free($3);
}

// lgGpioGetChipInfo
%typemap(in, numinputs=0) (lgChipInfo_p chipInfp) (lgChipInfo_t chipInf)
{
   $1 = &chipInf;
}

// lgGpioGetChipInfo
%typemap(argout) (lgChipInfo_p chipInfp)
{
   PyObject *o1, *o2, *o3, *o4;
   Py_XDECREF($result);   /* Blow away any previous result */
   $result = PyList_New(4);

   if (result >= 0)
   {
      result = 0;

      o2 = PyInt_FromLong(chipInf2.lines);
      o3 = PyString_FromString(chipInf2.name);
      o4 = PyString_FromString(chipInf2.label);
   }
   else
   {
      o2 = PyInt_FromLong(0);
      o3 = PyString_FromString("");
      o4 = PyString_FromString("");
   }

   o1 = PyInt_FromLong(result);

   PyList_SetItem($result, 0, o1);
   PyList_SetItem($result, 1, o2);
   PyList_SetItem($result, 2, o3);
   PyList_SetItem($result, 3, o4);
}

// lgGpioGetLineInfo
%typemap(in, numinputs=0) (lgLineInfo_p lineInfp) (lgLineInfo_t lineInf)
{
   $1 = &lineInf;
}

// lgGpioGetLineInfo
%typemap(argout) (lgLineInfo_p lineInfp)
{
   PyObject *o1, *o2, *o3, *o4, *o5;
   Py_XDECREF($result);   /* Blow away any previous result */
   $result = PyList_New(5);

   if (result >= 0)
   {
      result = 0;

      o2 = PyInt_FromLong(lineInf3.offset);
      o3 = PyInt_FromLong(lineInf3.lFlags);
      o4 = PyString_FromString(lineInf3.name);
      o5 = PyString_FromString(lineInf3.user);
   }
   else
   {
      o2 = PyInt_FromLong(0);
      o3 = PyInt_FromLong(0);
      o4 = PyString_FromString("");
      o5 = PyString_FromString("");
   }

   o1 = PyInt_FromLong(result);

   PyList_SetItem($result, 0, o1);
   PyList_SetItem($result, 1, o2);
   PyList_SetItem($result, 2, o3);
   PyList_SetItem($result, 3, o4);
   PyList_SetItem($result, 4, o5);
}

#else
  #warning no typemaps defined
#endif

%rename(_gpiochip_open) lgGpiochipOpen;
extern int lgGpiochipOpen(int gpioDev);

%rename(_gpiochip_close) lgGpiochipClose;
extern int lgGpiochipClose(int handle);

%rename(_gpio_get_chip_info) lgGpioGetChipInfo;
extern int lgGpioGetChipInfo(int handle, lgChipInfo_p chipInfp);

%rename(_gpio_get_line_info) lgGpioGetLineInfo;
extern int lgGpioGetLineInfo(int handle, int gpio, lgLineInfo_p lineInfp);

%rename(_gpio_get_mode) lgGpioGetMode;
extern int lgGpioGetMode(int handle, int gpio);

%rename(_gpio_claim_input) lgGpioClaimInput;
extern int lgGpioClaimInput(int handle, int lFlags, int gpio);

%rename(_gpio_claim_output) lgGpioClaimOutput;
extern int lgGpioClaimOutput(int handle, int lFlags, int gpio, int level);

%rename(_gpio_claim_alert) lgGpioClaimAlert;
extern int lgGpioClaimAlert(int handle, int lFlags, int eFlags, int gpio, int nfyHandle);

%rename(_gpio_free) lgGpioFree;
extern int lgGpioFree(int handle, int gpio);

%rename(_group_claim_input) lgGroupClaimInput;
extern int lgGroupClaimInput(int handle, int lFlags, int count, const int *gpios);

%rename(_group_claim_output) lgGroupClaimOutput;
extern int lgGroupClaimOutput(int handle, int lFlags, int count, const int *gpios, const int *levels);

%rename(_group_free) lgGroupFree;
extern int lgGroupFree(int handle, int gpio);

%rename(_gpio_read) lgGpioRead;
extern int lgGpioRead(int handle, int gpio);

%rename(_gpio_write) lgGpioWrite;
extern int lgGpioWrite(int handle, int gpio, int level);

%rename(_group_read) lgGroupRead;
extern int lgGroupRead(int handle, int gpio, uint64_t *OUTPUT);

%rename(_group_write) lgGroupWrite;
extern int lgGroupWrite(int handle, int gpio, uint64_t groupBits, uint64_t groupMask);

%rename(_tx_pulse) lgTxPulse;
extern int lgTxPulse(int handle, int gpio, int pulseOn, int pulseOff, int pulseOffset, int pulseCycles);

%rename(_tx_pwm) lgTxPwm;
extern int lgTxPwm(int handle, int gpio, float pwmFrequency, float pwmDutyCycle, int pwmOffset, int pwmCycles);

%rename(_tx_servo) lgTxServo;
extern int lgTxServo(int handle, int gpio, int pulseWidth, int servoFrequency,
   int servoOffset, int servoCycles);

%rename(_tx_wave) lgTxWave;
extern int lgTxWave(int handle, int gpio, int count, lgPulse_p pulses);

%rename(_tx_busy) lgTxBusy;
extern int lgTxBusy(int handle, int gpio, int kind);

%rename(_tx_room) lgTxRoom;
extern int lgTxRoom(int handle, int gpio, int kind);

%rename(_gpio_set_debounce_micros) lgGpioSetDebounce;
extern int lgGpioSetDebounce(int handle, int gpio, int debounce_us);

%rename(_gpio_set_watchdog_micros) lgGpioSetWatchdog;
extern int lgGpioSetWatchdog(int handle, int gpio, int watchdog_us);

%rename(_notify_open) lgNotifyOpen;
extern int lgNotifyOpen(void);

%rename(_notify_resume) lgNotifyResume;
extern int lgNotifyResume(int handle);

%rename(_notify_pause) lgNotifyPause;
extern int lgNotifyPause(int handle);

%rename(_notify_close) lgNotifyClose;
extern int lgNotifyClose(int handle);

%rename(_i2c_open) lgI2cOpen;
extern int lgI2cOpen(int i2cDev, int i2cAddr, int i2cFlags);

%rename(_i2c_close) lgI2cClose;
extern int lgI2cClose(int handle);

%rename(_i2c_write_quick) lgI2cWriteQuick;
extern int lgI2cWriteQuick(int handle, int bitVal);

%rename(_i2c_write_byte) lgI2cWriteByte;
extern int lgI2cWriteByte(int handle, int byteVal);

%rename(_i2c_read_byte) lgI2cReadByte;
extern int lgI2cReadByte(int handle);

%rename(_i2c_write_byte_data) lgI2cWriteByteData;
extern int lgI2cWriteByteData(int handle, int i2cReg, int byteVal);

%rename(_i2c_WriteWordData) lgI2cWriteWordData;
extern int lgI2cWriteWordData(int handle, int i2cReg, int wordVal);

%rename(_i2c_read_byte_data) lgI2cReadByteData;
extern int lgI2cReadByteData(int handle, int i2cReg);

%rename(_i2c_read_word_data) lgI2cReadWordData;
extern int lgI2cReadWordData(int handle, int i2cReg);

%rename(_i2c_process_call) lgI2cProcessCall;
extern int lgI2cProcessCall(int handle, int i2cReg, int wordVal);


%rename(_i2c_write_block_data) lgI2cWriteBlockData;
extern int lgI2cWriteBlockData(int handle, int i2cReg, const char *txBuf, int count);

%rename(_i2c_read_block_data) lgI2cReadBlockData;
extern int lgI2cReadBlockData(int handle, int i2cReg, char *rx32Buf);

%rename(_i2c_block_process_call) lgI2cBlockProcessCall;
extern int lgI2cBlockProcessCall(int handle, int i2cReg, char *ioBuf, int count);

%rename(_i2c_read_i2c_block_data) lgI2cReadI2CBlockData;
extern int lgI2cReadI2CBlockData(int handle, int i2cReg, char *rxBuf, int count);

%rename(_i2c_write_i2c_block_data) lgI2cWriteI2CBlockData;
extern int lgI2cWriteI2CBlockData(int handle, int i2cReg, const char *txBuf, int count);

%rename(_i2c_read_device) lgI2cReadDevice;
extern int lgI2cReadDevice(int handle, char *rxBuf, int count);

%rename(_i2c_write_device) lgI2cWriteDevice;
extern int lgI2cWriteDevice(int handle, const char *txBuf, int count);

%rename(_i2c_segments) lgI2cSegments;
extern int lgI2cSegments(int handle, lgI2cMsg_t *segs, int count);

%rename(_i2c_zip) lgI2cZip;
extern int lgI2cZip(int handle, const char *txBuf, int txCount, char *rxBuf, int rxCount);

%rename(_serial_open) lgSerialOpen;
extern int lgSerialOpen(const char *serDev, int serBaud, int serFlags);

%rename(_serial_close) lgSerialClose;
extern int lgSerialClose(int handle);

%rename(_serial_write_byte) lgSerialWriteByte;
extern int lgSerialWriteByte(int handle, int byteVal);

%rename(_serial_read_byte) lgSerialReadByte;
extern int lgSerialReadByte(int handle);

%rename(_serial_write) lgSerialWrite;
extern int lgSerialWrite(int handle, const char *txBuf, int count);

%rename(_serial_read) lgSerialRead;
extern int lgSerialRead(int handle, char *rxBuf, int count);

%rename(_serial_data_available) lgSerialDataAvailable;
extern int lgSerialDataAvailable(int handle);

%rename(_spi_open) lgSpiOpen;
extern int lgSpiOpen(int spiDev, int spiChan, int spiBaud, int spiFlags);

%rename(_spi_close) lgSpiClose;
extern int lgSpiClose(int handle);

%rename(_spi_read) lgSpiRead;
extern int lgSpiRead(int handle, char *rxBuf, int count);

%rename(_spi_write) lgSpiWrite;
extern int lgSpiWrite(int handle, const char *txBuf, int count);

%rename(_spi_xfer) lgSpiXfer;
extern int lgSpiXfer(int handle, const char *txBuf, char *rxBuf, int count);

%rename(_get_lg_version) lguVersion;
extern int lguVersion(void);

%rename(_get_internal) lguGetInternal;
extern int lguGetInternal(int cfgId, uint64_t *OUTPUT);

%rename(_set_internal) lguSetInternal;
extern int lguSetInternal(int cfgId, uint64_t cfgVal);

%rename(_error_text) lguErrorText;
extern const char *lguErrorText(int error);

