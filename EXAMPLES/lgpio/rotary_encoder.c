/*
rotary_encoder.c
2020-11-17
Public Domain

gcc -o renc rotary_encoder.c -llgpio

./renc
*/

#include <stdio.h>
#include <stdlib.h>

#include <lgpio.h>

/*

             +---------+         +---------+      0
             |         |         |         |
   A         |         |         |         |
             |         |         |         |
   +---------+         +---------+         +----- 1

       +---------+         +---------+            0
       |         |         |         |
   B   |         |         |         |
       |         |         |         |
   ----+         +---------+         +---------+  1

*/

typedef struct Renc_s
{
   int chip;
   int gpioA;
   int gpioB;
   void (*callback)(int);
   int levA;
   int levB;
   int lastGpio;
} Renc_t, *Renc_p;

void cbf(int e, lgGpioAlert_p evt, void *data)
{
   Renc_p renc;
   int i;
   int secs, nanos;

   renc = data;

   for (i=0; i<e; i++)
   {
      /*
      secs = evt[i].report.timestamp / 1000000000L;
      nanos = evt[i].report.timestamp % 1000000000L;
     
      printf("chip=%d gpio=%d level=%d time=%d.%09d\n",
         evt[i].report.chip, evt[i].report.gpio, evt[i].report.level,
         secs, nanos);
      */

      if (evt[i].report.chip == renc->chip)
      {
         if (evt[i].report.gpio == renc->gpioA)
         {
            renc->levA = evt[i].report.level;
            if ((renc->levA) && (renc->levB)) (renc->callback)(1);
         }
         else if (evt[i].report.gpio == renc->gpioB)
         {
            renc->levB = evt[i].report.level;
            if ((renc->levB) && (renc->levA)) (renc->callback)(-1);
         }
      }
   }
}

void way(int dir)
{
   static int pos=0;
   pos += dir;
   printf("%d\n", pos);
}

int main(int argc, char *argv[])
{
   int h;
   int err;
   Renc_t renc;

   renc.chip = 0;
   renc.gpioA = 20;
   renc.gpioB = 21;
   renc.levA = 0;
   renc.levB = 0;
   renc.callback = way;

   if (argc == 4) /* chip gpioA gpioB */
   {
      renc.chip = atoi(argv[1]);
      renc.gpioA = atoi(argv[2]);
      renc.gpioB = atoi(argv[3]);
   }

   else if (argc == 3) /* gpioA gpioB (chip 0) */
   {
      renc.gpioA = atoi(argv[1]);
      renc.gpioB = atoi(argv[2]);
   }

   h = lgGpiochipOpen(renc.chip);

   if (h < 0)
   {
      fprintf(stderr, "can't open /dev/gpiochip%d (%s)\n",
         renc.chip, lgErrStr(h));
      return -1;
   }

   lgGpioSetUser(h, "lg_rotary_encoder");

   err = lgGpioClaimAlert(h, 0, LG_BOTH_EDGES, renc.gpioA, -1);

   if (err < 0)
   {
      fprintf(stderr, "can't claim GPIO %d (%s)\n",
         renc.gpioA, lgErrStr(err));
      return -1;
   }

   err = lgGpioClaimAlert(h, 0, LG_BOTH_EDGES, renc.gpioB, -1);

   if (err < 0)
   {
      fprintf(stderr, "can't claim GPIO %d (%s)\n",
         renc.gpioB, lgErrStr(err));
      return -1;
   }

   lgGpioSetSamplesFunc(cbf, &renc);

   while (1) lguSleep(1);
}

