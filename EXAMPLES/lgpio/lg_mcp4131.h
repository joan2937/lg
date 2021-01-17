#ifndef LG_MCP4131_H
#define LG_MCP4131_H

/*
lg_mcp4131.h
2021-01-17
Public Domain

http://abyz.me.uk/lg/lgpio.html
http://abyz.me.uk/lg/rgpio.html

DIG POT

CS      1 o o 8 V+
SCLK    2 o o 7 B
SDI/SDO 3 o o 6 W
GND     4 o o 5 A

For this module nothing is read from the chip so the SBC's
MISO line need not be connected.

For safety put a resistor in series between MOSI and SDI/SDO.
*/

#include <lgpio.h>

typedef struct mcp4131_s mcp4131_t, *mcp4131_p;

mcp4131_p MCP4131_open(int sbc, int device, int channel, int speed, int flags);
mcp4131_p MCP4131_close(mcp4131_p s);

int MCP4131_set_wiper(mcp4131_p s, int value);
int MCP4131_get_wiper(mcp4131_p s);
int MCP4131_increment_wiper(mcp4131_p s);
int MCP4131_decrement_wiper(mcp4131_p s);

int MCP4131_set_enable(mcp4131_p s, callbk_t enable);

#endif

