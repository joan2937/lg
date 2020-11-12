#include <stdio.h>
#include <stdlib.h>

#include <lgpio.h>
#include <rgpio.h>

#define OUT 21
#define LOOPS 120

#define LFLAGS 0

int main(int argc, char *argv[])
{
   int sbc;
   int h;
   int i;
   double start, end;

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
         tx_pulse(sbc, h, OUT, 20000, 30000, 0, 0);

         lgu_sleep(2);

         tx_pulse(sbc, h, OUT, 20000, 5000, 0, LOOPS);

         start = lgu_time();

         while (tx_busy(sbc, h, OUT, LG_TX_PWM)) lgu_sleep(0.01);

         end = lgu_time();

         printf("%d cycles at 40 Hz took %.1f seconds\n", LOOPS, end-start);
      }

      gpiochip_close(sbc, h);
   }

   rgpiod_stop(sbc);
}

