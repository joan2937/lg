/*
monitor.c
2020-11-15
Public Domain

gcc -o monitor monitor.c -llgpio

./monitor [chip:]gpio ...

chip specifies a gpiochip number.  gpio is a GPIO in the previous
gpiochip (gpiochip0 if there is no previous gpiochip).

e.g.

./monitor 23 24 25        # monitor gpiochip0: 23,24,25
./monitor 0:23 24 1:0 5 6 # monitor gpiochip0: 23,24 gpiochip1: 0,5,6
*/

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <inttypes.h>

#include <lgpio.h>

/* callback function */
void cbf(int e, lgGpioAlert_p evt, void *data)
{
   int i;
   int secs, nanos;

   for (i=0; i<e; i++)
   {
      secs = evt[i].report.timestamp / 1000000000L;
      nanos = evt[i].report.timestamp % 1000000000L;
     
      printf("chip=%d gpio=%d level=%d time=%d.%09d\n",
         evt[i].report.chip, evt[i].report.gpio, evt[i].report.level,
         secs, nanos);
   }
}

int main(int argc, char *argv[])
{
   int i, h=-1, err;
   int chip = 0;
   int gpio = -1;
   int c, g;
   char d;

   for (i=1; i<argc; i++)
   {
      c=-1; g=-1; d=-1;

      if (sscanf(argv[i], "%d:%d%c", &c, &g, &d) == 2)
      {
         /* chip:gpio option */
         printf("chip=%d gpio=%d\n", c, g);

         if (c != chip) h = -1; /* force open of new gpiochip */

         chip = c;
         gpio = g;
      }
      else if (sscanf(argv[i], "%d%c", &g, &d) == 1)
      {
         /* gpio option */
         printf("chip=%d gpio=%d\n", chip, g);

         /* chip the same as previous */
         gpio = g;
      }
      else
      {
         /* bad option */

         gpio = -1;
         printf("don't understand %s\n", argv[i]);
         return -1;
      }
      if (gpio >= 0)
      {
         if (h < 0)
         {
            /* get a handle to the gpiochip */
            h = lgGpiochipOpen(chip);
         }

         if (h >= 0)
         {
            /* got a handle, now open the GPIO for alerts */
            err = lgGpioClaimAlert(h, 0, LG_BOTH_EDGES, g, -1);
            if (err < 0)
            {
               fprintf(stderr, "GPIO in use %d:%d (%s)\n",
                  chip, gpio, lgErrStr(err));
               return -1;
            }
         }
         else
         {
            fprintf(stderr, "can't open gpiochip %d (%s)\n",
               chip, lgErrStr(h));
            return -1;
         }
      }
   }

   lgGpioSetSamplesFunc(cbf, NULL); /* call cbf for all alerts */

   while (1) lguSleep(1); /* sleep until interrupted */
}

