/*
rotary_encoder.c
2020-11-18
Public Domain

http://abyz.me.uk/lg/rgpio.html

gcc -Wall -o renc rotary_encoder.c -lrgpio

./renc [chip] gpioA gpioB

E.g.

./renc 20 21 # gpiochip 0, gpioA 20, gpioB 21

./renc 2 7 5 # gpiochip 2, gpioA 7, gpioB 5
*/

#include <stdio.h>
#include <stdlib.h>

#include <lgpio.h>
#include <rgpio.h>

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

void cbf(
   int sbc, int chip, int gpio, int level,
   uint64_t timestamp, void *userdata)
{
   Renc_p renc;
   int i;

   renc = userdata;

   if (chip == renc->chip)
   {
      if (gpio == renc->gpioA)
      {
         renc->levA = level;
         if ((renc->levA) && (renc->levB)) (renc->callback)(1);
      }
      else if (gpio == renc->gpioB)
      {
         renc->levB = level;
         if ((renc->levB) && (renc->levA)) (renc->callback)(-1);
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
   int sbc;
   int h;
   int err;
   int cb_id_a, cb_id_b;
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

   sbc = rgpiod_start(NULL, NULL);

   if (sbc < 0)
   {
      printf("connection failed\n");
      exit(-1);
   }

   h = gpiochip_open(sbc, renc.chip);

   if (h < 0)
   {
      fprintf(stderr, "can't open /dev/gpiochip%d (%s)\n",
         renc.chip, lgu_error_text(h));
      return -1;
   }

   err = gpio_claim_alert(sbc, h, 0, LG_BOTH_EDGES, renc.gpioA, -1);

   if (err < 0)
   {
      fprintf(stderr, "can't claim GPIO %d (%s)\n",
         renc.gpioA, lgu_error_text(err));
      return -1;
   }

   err = gpio_claim_alert(sbc, h, 0, LG_BOTH_EDGES, renc.gpioB, -1);

   if (err < 0)
   {
      fprintf(stderr, "can't claim GPIO %d (%s)\n",
         renc.gpioB, lgu_error_text(err));
      return -1;
   }

   cb_id_a = callback(sbc, h, renc.gpioA, LG_BOTH_EDGES, cbf, &renc);

   if (cb_id_a < 0)
   {
      fprintf(stderr, "can't create callback for GPIO %d (%s)\n",
         renc.gpioA, lgu_error_text(cb_id_a));
      return -1;
   }

   cb_id_b = callback(sbc, h, renc.gpioB, LG_BOTH_EDGES, cbf, &renc);

   if (cb_id_b < 0)
   {
      fprintf(stderr, "can't create callback for GPIO %d (%s)\n",
         renc.gpioB, lgu_error_text(cb_id_b));
      return -1;
   }

   while (1) lgu_sleep(1);
}

