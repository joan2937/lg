/*
tx_wave.c
2020-11-18
Public Domain

http://abyz.me.uk/lg/rgpio.html

gcc -Wall -o tx_wave tx_wave.c -lrgpio

./tx_wave
*/

#include <stdio.h>
#include <stdlib.h>

#include <lgpio.h>
#include <rgpio.h>

int OUT[6]={20, 21, 22, 23, 24, 25};
int lvl[6]={ 0,  0,  0,  0,  0,  0};

#define PULSES 500

#define LFLAGS 0

lgPulse_t pulses[PULSES];

int main(int argc, char *argv[])
{
   int sbc;
   int h;
   int i;
   double start, end;
   int delay = 1000;
   int total = 0;

   sbc = rgpiod_start(NULL, NULL);

   if (sbc < 0)
   {
      printf("connection failed\n");
      exit(-1);
   }

   for (i=0; i<PULSES; i++)
   {
      pulses[i].bits = i;
      pulses[i].mask = -1;
      pulses[i].delay = delay;

      total += delay;
      delay += 100;
   }

   h = gpiochip_open(sbc, 0);

   if (h >= 0)
   {
      if (group_claim_output(sbc, h, LFLAGS, 6, OUT, lvl) == LG_OKAY)
      {
         tx_wave(sbc, h, OUT[0], PULSES, pulses);

         start = lgu_time();

         while (tx_busy(sbc, h, OUT[0], LG_TX_WAVE)) lgu_sleep(0.01);

         end = lgu_time();

         printf("%d pulses took %.1f seconds (exp=%.1f)\n",
            PULSES, end-start, total/1e6);
      }

      gpiochip_close(sbc, h);
   }

   rgpiod_stop(sbc);
}

