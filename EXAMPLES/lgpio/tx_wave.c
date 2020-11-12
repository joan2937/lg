#include <stdio.h>
#include <stdlib.h>

#include <lgpio.h>

int OUT[6]={20, 21, 22, 23, 24, 25};
int lvl[6]={ 0,  0,  0,  0,  0,  0};

#define PULSES 500

#define LFLAGS 0

lgPulse_t pulses[PULSES];

int main(int argc, char *argv[])
{
   int h;
   int i;
   double start, end;
   int delay = 1000;
   int total = 0;

   for (i=0; i<PULSES; i++)
   {
      pulses[i].bits = i;
      pulses[i].mask = -1;
      pulses[i].delay = delay;

      total += delay;
      delay += 100;
   }

   h = lgGpiochipOpen(0);

   if (h >= 0)
   {
      if (lgGroupClaimOutput(h, LFLAGS, 6, OUT, lvl) == LG_OKAY)
      {
         lgTxWave(h, OUT[0], PULSES, pulses);

         start = lguTime();

         while (lgTxBusy(h, OUT[0], LG_TX_WAVE)) lguSleep(0.01);

         end = lguTime();

         printf("%d pulses took %.1f seconds (exp=%.1f)\n",
            PULSES, end-start, total/1e6);
      }

      lgGpiochipClose(h);
   }
}

