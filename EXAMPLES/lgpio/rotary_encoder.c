/*
rotary_encoder.c
2020-11-20
Public Domain

http://abyz.me.uk/lg/lgpio.html

gcc -Wall -o renc rotary_encoder.c -llgpio

./renc [chip] gpioA gpioB

E.g.

./renc 20 21 # gpiochip 0, gpioA 20, gpioB 21

./renc 2 7 5 # gpiochip 2, gpioA 7, gpioB 5
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
      renc.chip = 0;
      renc.gpioA = atoi(argv[1]);
      renc.gpioB = atoi(argv[2]);
   }

   else
   {
      fprintf(stderr, "Usage: ./renc [chip] gpioA gpioB\n");
      return -1;
   }

   h = lgGpiochipOpen(renc.chip);

   if (h < 0)
   {
      fprintf(stderr, "can't open /dev/gpiochip%d (%s)\n",
         renc.chip, lguErrorText(h));
      return -1;
   }

   lgGpioSetUser(h, "lg_rotary_encoder");

   err = lgGpioClaimAlert(h, 0, LG_BOTH_EDGES, renc.gpioA, -1);

   if (err < 0)
   {
      fprintf(stderr, "can't claim GPIO %d (%s)\n",
         renc.gpioA, lguErrorText(err));
      return -1;
   }

   err = lgGpioClaimAlert(h, 0, LG_BOTH_EDGES, renc.gpioB, -1);

   if (err < 0)
   {
      fprintf(stderr, "can't claim GPIO %d (%s)\n",
         renc.gpioB, lguErrorText(err));
      return -1;
   }

   lgGpioSetSamplesFunc(cbf, &renc);

   while (1) lguSleep(1);
}

