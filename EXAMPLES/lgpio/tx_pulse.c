#include <stdio.h>
#include <stdlib.h>

#include <lgpio.h>

#define OUT 21
#define LOOPS 120

#define LFLAGS 0

int main(int argc, char *argv[])
{
   int h;
   int i;
   double start, end;

   h = lgGpiochipOpen(0);

   if (h >= 0)
   {
      if (lgGpioClaimOutput(h, LFLAGS, OUT, 0) == LG_OKAY)
      {
         lgTxPulse(h, OUT, 20000, 30000, 0, 0);

         lguSleep(2);

         lgTxPulse(h, OUT, 20000, 5000, 0, LOOPS);

         start = lguTime();

         while (lgTxBusy(h, OUT, LG_TX_PWM)) lguSleep(0.01);

         end = lguTime();

         printf("%d cycles at 40 Hz took %.1f seconds\n", LOOPS, end-start);
      }

      lgGpiochipClose(h);
   }
}

