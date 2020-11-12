
lgpio is a library for Linux Single Board Computers (SBC) which allows control of the General Purpose Input Outputs (GPIO).

## Features

* reading and writing GPIO singly and in groups
* software timed PWM and waves
* callbacks on GPIO level change
* notifications via pipe on GPIO level change
* I2C wrapper
* SPI wrapper
* serial link wrapper
* daemon interface
* permission control (daemon interface)
* file handling (daemon interface)
* creating and running scripts (daemon interface)
* network access (daemon interface)

## Interfaces

The library provides a number of control interfaces
* the C function interface,
* the socket interface (used by the Python module).

## Utilities

A number of utility programs are provided:
* the rgpiod daemon,
* the Python modules,
* the rgs command line utility,

## Documentation

See http://abyz.me.uk/lg/

## Example programs

See http://abyz.me.uk/lg/examples.html

## GPIO

ALL GPIO are identified by their gpiochip line number.

