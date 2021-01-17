/*
lgl_mcp4131.c
2021-01-17
Public Domain
*/

#include <stdlib.h>

#include <lgpio.h>

#include "lg_mcp4131.h"

typedef struct mcp4131_s
{
   int sbc;     // sbc connection
   int device;  // SPI device
   int channel; // SPI channel
   int speed;   // SPI bps
   int flags;   // SPI flags
   int spih;    // SPI handle
   int value;   // wiper value
   callbk_t enable;
} mcp4131_t, *mcp4131_p;

mcp4131_p MCP4131_open(int sbc, int device, int channel, int speed, int flags)
{
   mcp4131_p s;

   s = calloc(1, sizeof(mcp4131_t));

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

mcp4131_p MCP4131_close(mcp4131_p s)
{
   if (s != NULL)
   {
      lgSpiClose(s->spih);
      free(s);
      s = NULL;
   }
   return s;
}

int MCP4131_set_wiper(mcp4131_p s, int value)
{
   char buf[16];

   if (s == NULL) return -1;

   if ((value < 0) || (value > 128)) return -2;

   s->value = value;

   if (s->enable != NULL) s->enable(1);

   buf[0] = 0;
   buf[1] = value;

   lgSpiWrite(s->spih, buf, 2);

   if (s->enable != NULL) s->enable(0);

   return 0;
}

int MCP4131_get_wiper(mcp4131_p s)
{
   if (s == NULL) return -1;

   return s->value;
}

int MCP4131_increment_wiper(mcp4131_p s)
{
   if (s == NULL) return -1;

   if (s->value < 128) MCP4131_set_wiper(s, s->value + 1);

   return 0;
}

int MCP4131_decrement_wiper(mcp4131_p s)
{
   if (s == NULL) return -1;

   if (s->value > 0) MCP4131_set_wiper(s, s->value - 1);

   return 0;
}

int MCP4131_set_enable(mcp4131_p s, callbk_t enable)
{
   s->enable = enable;

   return 0;
}

#ifdef EXAMPLE

/*
gcc -D EXAMPLE -o mcp4131 lgl_mcp4131.c -llgpio
./mcp4131
*/

#include <stdio.h>

#include <lgpio.h>

#include "lg_mcp4131.h"

int main(int argc, char *argv[])
{
   int sbc=-1;
   mcp4131_p dac=NULL;
   int potpos;

   dac = MCP4131_open(sbc, 0, 0, 50000, 0);

   if (dac == NULL) return -1;

   potpos = 0;

   while (1)
   {
      MCP4131_set_wiper(dac, potpos);

      lguSleep(0.2);

      potpos++;

      if (potpos > 128) potpos = 0;
   }

   return 0;
}

#endif

