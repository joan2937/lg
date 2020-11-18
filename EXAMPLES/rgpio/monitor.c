/*
monitor.c
2020-11-18
Public Domain

http://abyz.me.uk/lg/rgpio.html

gcc -Wall -o monitor monitor.c -lrgpio

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
#include <rgpio.h>

/* callback function */
void cbf(
   int sbc, int chip, int gpio, int level,
   uint64_t timestamp, void * userdata)
{
   int secs, nanos;

   secs = timestamp / 1000000000L;
   nanos = timestamp % 1000000000L;
     
   printf("sbc=%d chip=%d gpio=%d level=%d time=%d.%09d\n",
      sbc, chip, gpio, level, secs, nanos);
}

int main(int argc, char *argv[])
{
   int sbc, i, h=-1, err, cb_id;
   int chip = 0;
   int gpio = -1;
   int c, g;
   char d;

   sbc = rgpiod_start(NULL, NULL);

   if (sbc < 0)
   {
      printf("connection failed\n");
      exit(-1);
   }

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
            h = gpiochip_open(sbc, chip);
         }

         if (h >= 0)
         {
            /* got a handle, now open the GPIO for alerts */
            err = gpio_claim_alert(sbc, h, 0, LG_BOTH_EDGES, g, -1);
            if (err < 0)
            {
               fprintf(stderr, "GPIO in use %d:%d (%s)\n",
                  chip, gpio, lgu_error_text(err));
               return -1;
            }
            cb_id = callback(sbc, h, gpio, LG_BOTH_EDGES, cbf, NULL);
            if (cb_id < 0)
            {
               fprintf(stderr, "can't create callback %d:%d (%s)\n",
                  chip, gpio, lgu_error_text(cb_id));
               return -1;
            }

         }
         else
         {
            fprintf(stderr, "can't open gpiochip %d (%s)\n",
               chip, lgu_error_text(h));
            return -1;
         }
      }
   }

   while (1) lgu_sleep(1); /* sleep until interrupted */
}

