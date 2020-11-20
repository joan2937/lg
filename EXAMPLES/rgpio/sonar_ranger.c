/*
sonar_ranger.c
2020-11-20
Public Domain

http://abyz.me.uk/lg/rgpio.html

gcc -Wall -o sonar_ranger sonar_ranger.c -lrgpio

./sonar_ranger [chip] trigger echo

E.g.

./sonar_ranger 20 21 # ping gpiochip 0, trigger 20, echo 21

./sonar_ranger 2 7 5 # gpiochip 2, trigger 7, echo 5
*/

#include <stdio.h>
#include <stdlib.h>

#include <lgpio.h>
#include <rgpio.h>

int pinged = 0;
uint64_t ping_time;

void cbf(
   int sbc, int chip, int gpio, int level,
   uint64_t timestamp, void *userdata)
{
   static uint64_t _high = 0;

   if (level == 1) _high = timestamp;
   else
   {
      if (_high != 0)
      {
         ping_time = timestamp - _high;
         _high = 0;
         pinged = 1;
      }
   }
}

float read_ranger(int sbc, int h, int trigger)
{
   double start;

   /*
      Return the distance in cms if okay, otherwise 0.
   */

   pinged = 0;

   /* send a 15 microsecond high pulse as trigger */
   tx_pulse(sbc, h, trigger, 15, 0, 0, 1);

   start = lgu_time();

   while (!pinged)
   {
      if ((lgu_time() - start) > 0.3) return 0.0;
      lgu_sleep(0.01);
   }

   return 17015.0 * ping_time / 1e9;
}

int main(int argc, char *argv[])
{
   int sbc;
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

   sbc = rgpiod_start(NULL, NULL);

   if (sbc < 0)
   {
      printf("connection failed\n");
      exit(-1);
   }

   h = gpiochip_open(sbc, chip);

   if (h < 0)
   {
      fprintf(stderr, "can't open /dev/gpiochip%d (%s)\n",
         chip, lgu_error_text(h));
      return -1;
   }

   err = gpio_claim_output(sbc, h, 0, trigger, 0);

   if (err < 0)
   {
      fprintf(stderr, "can't claim GPIO %d (%s)\n",
         trigger, lgu_error_text(err));
      return -1;
   }

   err = gpio_claim_alert(sbc, h, 0, LG_BOTH_EDGES, echo, -1);

   if (err < 0)
   {
      fprintf(stderr, "can't claim GPIO %d (%s)\n",
         echo, lgu_error_text(err));
      return -1;
   }

   cb_echo = callback(sbc, h, echo, LG_BOTH_EDGES, cbf, NULL);

   if (cb_echo < 0)
   {
      fprintf(stderr, "can't create callback for GPIO %d (%s)\n",
         echo, lgu_error_text(cb_echo));
      return -1;
   }

   while (1)
   {
      printf("cms=%.1f\n", read_ranger(sbc, h, trigger));
      lgu_sleep(0.2);
   }
}

