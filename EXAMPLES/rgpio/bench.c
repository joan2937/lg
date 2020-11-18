/*
bench.c
2020-11-18
Public Domain

http://abyz.me.uk/lg/rgpio.html

gcc Wall -o bench bench.c -lrgpio

./bench
*/

#include <stdio.h>
#include <stdlib.h>

#include <lgpio.h>
#include <rgpio.h>

#define LFLAGS 0

#define OUT 21
#define LOOPS 5000

int main(int argc, char *argv[])
{
   int sbc;
   int h;
   int i;
   double t0, t1;

   sbc = rgpiod_start(NULL, NULL);

   if (sbc < 0)
   {
      printf("connection failed\n");
      exit(-1);
   }

   h = gpiochip_open(sbc, 0);

   if (h >= 0)
   {
      if (gpio_claim_output(sbc, h, LFLAGS, OUT, 0) == LG_OKAY)
      {

         t0 = lgu_time();

         for (i=0; i<LOOPS; i++)
         {
            gpio_write(sbc, h, OUT, 0);
            gpio_write(sbc, h, OUT, 1);
         }

         t1 = lgu_time();

         printf("%.0f toggles per second\n", (1.0 * LOOPS)/(t1-t0));
      }

      gpiochip_close(sbc, h);
   }

   rgpiod_stop(sbc);
}

