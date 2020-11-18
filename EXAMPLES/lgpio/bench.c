/*
bench.c
2020-11-18
Public Domain

http://abyz.me.uk/lg/lgpio.html

gcc -Wall -o bench bench.c -llgpio

./bench
*/

#include <stdio.h>
#include <stdlib.h>

#include <lgpio.h>

#define LFLAGS 0

#define OUT 21
#define LOOPS 20000

int main(int argc, char *argv[])
{
   int h;
   int i;
   double t0, t1;

   h = lgGpiochipOpen(0);

   if (h >= 0)
   {
      if (lgGpioClaimOutput(h, LFLAGS, OUT, 0) == LG_OKAY)
      {

         t0 = lguTime();

         for (i=0; i<LOOPS; i++)
         {
            lgGpioWrite(h, OUT, 0);
            lgGpioWrite(h, OUT, 1);
         }

         t1 = lguTime();

         printf("%.0f toggles per second\n", (1.0 * LOOPS)/(t1-t0));
      }

      lgGpiochipClose(h);
   }
}

