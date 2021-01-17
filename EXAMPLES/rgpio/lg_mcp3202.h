#ifndef LG_MCP3202_H
#define LG_MCP3202_H

/*
lg_mcp3202.h
2021-01-17
Public Domain

http://abyz.me.uk/lg/lgpio.html
http://abyz.me.uk/lg/rgpio.html

MCP3202 2 ch 12-bit ADC

CS  1 o o 8 V+
CH0 2 o o 7 CLK
CH1 3 o o 6 DO
GND 5 o o 4 DI

Be aware that DO will be at the same voltage as V+.
*/

#include <lgpio.h>

typedef struct mcp3202_s mcp3202_t, *mcp3202_p;

mcp3202_p MCP3202_open(int sbc, int device, int channel, int speed, int flags);
mcp3202_p MCP3202_close(mcp3202_p s);

int MCP3202_read_single_ended(mcp3202_p s, int channel);
int MCP3202_read_differential_plus(mcp3202_p s);
int MCP3202_read_differential_minus(mcp3202_p s);

int MCP3202_set_enable(mcp3202_p s, callbk_t enable);

#endif

