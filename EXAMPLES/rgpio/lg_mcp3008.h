#ifndef LG_MCP3008_H
#define LG_MCP3008_H

/*
lg_mcp3008.h
2021-01-09
Public Domain

http://abyz.me.uk/lg/lgpio.html
http://abyz.me.uk/lg/rgpio.html

MCP3008 8 ch 10-bit ADC

CH0     1 o o 16 V+
CH1     2 o o 15 Vref
CH2     3 o o 14 AGND
CH3     4 o o 13 SCLK
CH4     5 o o 12 SDO 
CH5     6 o o 11 SDI 
CH6     7 o o 10 CS/SHDN
CH7     8 o o  9 DGND

Be aware that SDO will be at the same voltage as V+.
*/

#include <lgpio.h>

typedef struct
{
   int sbc;     // sbc connection
   int device;  // SPI device
   int channel; // SPI channel
   int speed;   // SPI bps
   int flags;   // SPI flags
   int spih;    // SPI handle
   int value;   // wiper value
   callbk_t chip_select;
   callbk_t chip_deselect;
} mcp3008_t, *mcp3008_p;

mcp3008_p MCP3008_open(int sbc, int device, int channel, int speed, int flags);
mcp3008_p MCP3008_close(mcp3008_p s);

int MCP3008_read_single_ended(mcp3008_p s, int channel);
int MCP3008_read_differential_plus(mcp3008_p s, int channel);
int MCP3008_read_differential_minus(mcp3008_p s, int channel);

#endif

