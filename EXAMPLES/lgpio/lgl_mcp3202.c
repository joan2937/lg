/*
lgl_mcp3202.c
2021-01-17
Public Domain
*/

#include <stdlib.h>

#include <lgpio.h>

#include "lg_mcp3202.h"

typedef struct mcp3202_s
{
   int sbc;     // sbc connection
   int device;  // SPI device
   int channel; // SPI channel
   int speed;   // SPI bps
   int flags;   // SPI flags
   int spih;    // SPI handle
   callbk_t enable;
} mcp3202_t, *mcp3202_p;

mcp3202_p MCP3202_open(int sbc, int device, int channel, int speed, int flags)
{
   mcp3202_p s;

   s = calloc(1, sizeof(mcp3202_t));

   if (s == NULL) return NULL;

   s->sbc = sbc;         // sbc connection
   s->device = device;   // SPI device
   s->channel = channel; // SPI channel
   s->speed = speed;     // SPI speed
   s->flags = flags;     // SPI flags

   s->spih = lgSpiOpen(device, channel, speed, flags);

   if (s->spih < 0)
   {
      free(s);
      s = NULL;
   }

   return s;
}

mcp3202_p MCP3202_close(mcp3202_p s)
{
   if (s != NULL)
   {
      lgSpiClose(s->spih);
      free(s);
      s = NULL;
   }
   return s;
}

int MCP3202_read_single_ended(mcp3202_p s, int channel)
{
   int value;
   unsigned char buf[16];

   if (s == NULL) return -1;

   if ((channel < 0) || (channel > 1)) return -2;

   if (s->enable != NULL) s->enable(1);

   buf[0] = 1;
   buf[1] = 0xA0 + (channel<<6);
   buf[2] = 0;

   lgSpiXfer(s->spih, buf, buf, 3);

   if (s->enable != NULL) s->enable(0);

   value = ((buf[1]&0x0f)<<8) + buf[2];

   return value;
}

int MCP3202_read_differential_plus(mcp3202_p s)
{
   int value;
   unsigned char buf[16];

   if (s == NULL) return -1;

   if (s->enable != NULL) s->enable(1);

   buf[0] = 1;
   buf[1] = 0x20;
   buf[2] = 0;

   lgSpiXfer(s->spih, buf, buf, 3);

   if (s->enable != NULL) s->enable(0);

   value = ((buf[1]&0x0f)<<8) + buf[2];
   return value;
}

int MCP3202_read_differential_minus(mcp3202_p s)
{
   int value;
   unsigned char buf[16];

   if (s == NULL) return -1;

   if (s->enable != NULL) s->enable(1);

   buf[0] = 1;
   buf[1] = 0x60;
   buf[2] = 0;

   lgSpiXfer(s->spih, buf, buf, 3);

   if (s->enable != NULL) s->enable(0);

   value = ((buf[1]&0x0f)<<8) + buf[2];

   return value;
}

int MCP3202_set_enable(mcp3202_p s, callbk_t enable)
{
   s->enable = enable;

   return 0;
}


#ifdef EXAMPLE

/*
gcc -D EXAMPLE -o mcp3202 lgl_mcp3202.c -llgpio
./mcp3202
*/

#include <stdio.h>

#include <lgpio.h>

#include "lg_mcp3202.h"

int main(int argc, char *argv[])
{
   int sbc=-1;
   mcp3202_p adc=NULL;
   int v0, v1, v2, v3;

   adc = MCP3202_open(sbc, 0, 1, 50000, 0);

   if (adc == NULL) return -1;

   while (1)
   {
      lguSleep(0.2);

      v0 = MCP3202_read_single_ended(adc, 0);
      v1 = MCP3202_read_single_ended(adc, 1);
      v2 = MCP3202_read_differential_plus(adc);
      v3 = MCP3202_read_differential_minus(adc);

      printf("0=%4d 1=%4d 2=%4d 3=%4d\n", v0, v1, v2, v3);
   }

   return 0;
}

#endif

