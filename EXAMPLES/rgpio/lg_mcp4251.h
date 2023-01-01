#ifndef LG_MCP4251_H
#define LG_MCP4251_H

/*
lg_mcp4251.h
2021-01-20
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

typedef struct mcp4251_s mcp4251_t, *mcp4251_p;

mcp4251_p MCP4251_open(int sbc, int device, int channel, int speed, int flags);
mcp4251_p MCP4251_close(mcp4251_p s);

int MCP4251_set_wiper(mcp4251_p s, int value);
int MCP4251_get_wiper(mcp4251_p s);
int MCP4251_increment_wiper(mcp4251_p s);
int MCP4251_decrement_wiper(mcp4251_p s);

int MCP4251_set_enable(mcp4251_p s, callbk_t enable);

#endif

