/*
sonar_ranger.c
2020-11-20
Public Domain

http://abyz.me.uk/lg/lgpio.html

gcc -Wall -o sonar_ranger sonar_ranger.c -llgpio

./sonar_ranger [chip] trigger echo

E.g.

./sonar_ranger 20 21 # ping gpiochip 0, trigger 20, echo 21

./sonar_ranger 2 7 5 # gpiochip 2, trigger 7, echo 5
*/

#include <stdio.h>
#include <stdlib.h>

#include <lgpio.h>

int pinged = 0;
uint64_t ping_time;

void cbf(int e, lgGpioAlert_p evt, void *userdata)
{
   int i;
   static uint64_t _high = 0;

   for (i=0; i<e; i++)
   {
      if (evt[i].report.level == 1) _high = evt[i].report.timestamp;
      else
      {
         if (_high != 0)
         {
            ping_time = evt[i].report.timestamp - _high;
            _high = 0;
            pinged = 1;
         }
      }
   }
}

float readRanger(int h, int trigger)
{
   double start;

   /*
      Return the distance in cms if okay, otherwise 0.
   */

   pinged = 0;

   /* send a 15 microsecond high pulse as trigger */
   lgTxPulse(h, trigger, 15, 0, 0, 1);

   start = lguTime();

   while (!pinged)
   {
      if ((lguTime() - start) > 0.3) return 0.0;
      lguSleep(0.01);
   }

   return 17015.0 * ping_time / 1e9;
}

int main(int argc, char *argv[])
{
   int h;
   int chip, trigger, echo;
   int cb_echo;
   int err;

   if (argc == 4) /* chip trigger echo */
   {
      chip = atoi(argv[1]);
      trigger = atoi(argv[2]);
      echo = atoi(argv[3]);
   }

   else if (argc == 3) /* trigger echo (chip 0) */
   {
      chip = 0;
      trigger = atoi(argv[1]);
      echo = atoi(argv[2]);
   }

   else
   {
      fprintf(stderr, "Usage: ./sonar_ranger [chip] trigger echo\n");
      return -1;
   }

   h = lgGpiochipOpen(chip);

   if (h < 0)
   {
      fprintf(stderr, "can't open /dev/gpiochip%d (%s)\n",
         chip, lguErrorText(h));
      return -1;
   }

   err = lgGpioClaimOutput(h, 0, trigger, 0);

   if (err < 0)
   {
      fprintf(stderr, "can't claim GPIO %d (%s)\n",
         trigger, lguErrorText(err));
      return -1;
   }

   err = lgGpioClaimAlert(h, 0, LG_BOTH_EDGES, echo, -1);

   if (err < 0)
   {
      fprintf(stderr, "can't claim GPIO %d (%s)\n",
         echo, lguErrorText(err));
      return -1;
   }

   err = lgGpioSetAlertsFunc(h, echo, cbf, NULL);

   if (err < 0)
   {
      fprintf(stderr, "can't create callback for GPIO %d (%s)\n",
         echo, lguErrorText(cb_echo));
      return -1;
   }

   while (1)
   {
      printf("cms=%.1f\n", readRanger(h, trigger));
      lguSleep(0.2);
   }
}

