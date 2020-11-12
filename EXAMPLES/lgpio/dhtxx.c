/*
dhtxx.c
2020-10-17
Public Domain
*/

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <inttypes.h>

#include <lgpio.h>

#define DHTAUTO 0
#define DHT11   1
#define DHTXX   2

#define DHT_GOOD         0
#define DHT_BAD_CHECKSUM 1
#define DHT_BAD_DATA     2
#define DHT_TIMEOUT      3

/*
gcc -o dhtxx dhtxx.c -llg
*/

#define MAX_GPIO 32

static int decode_dhtxx(uint64_t reading, int model, float *rh, float *temp)
{
/*
      +-------+-------+
      | DHT11 | DHTXX |
      +-------+-------+
Temp C| 0-50  |-40-125|
      +-------+-------+
RH%   | 20-80 | 0-100 |
      +-------+-------+

         0      1      2      3      4
      +------+------+------+------+------+
DHT11 |check-| 0    | temp |  0   | RH%  |
      |sum   |      |      |      |      |
      +------+------+------+------+------+
DHT21 |check-| temp | temp | RH%  | RH%  |
DHT22 |sum   | LSB  | MSB  | LSB  | MSB  |
DHT33 |      |      |      |      |      |
DHT44 |      |      |      |      |      |
      +------+------+------+------+------+

*/
   uint8_t byte[5];
   uint8_t chksum;
   float div;
   float t, h;
   int valid;
   int status;

   byte[0] = (reading    ) & 255;
   byte[1] = (reading>> 8) & 255;
   byte[2] = (reading>>16) & 255;
   byte[3] = (reading>>24) & 255;
   byte[4] = (reading>>32) & 255;

   chksum = (byte[1] + byte[2] + byte[3] + byte[4]) & 0xFF;

   valid = 0;

   if (chksum == byte[0])
   {
      if (model == DHT11)
      {
         if ((byte[1] == 0) && (byte[3] == 0))
         {
            valid = 1;

            t = byte[2];

            if (t > 60.0) valid = 0;

            h = byte[4];

            if ((h < 10.0) || (h > 90.0)) valid = 0;
         }
      }
      else if (model == DHTXX)
      {
         valid = 1;

         h = ((float)((byte[4]<<8) + byte[3]))/10.0;

         if (h > 110.0) valid = 0;

         if (byte[2] & 128) div = -10.0; else div = 10.0;

         t = ((float)(((byte[2]&127)<<8) + byte[1])) / div;

         if ((t < -50.0) || (t > 135.0)) valid = 0;
      }
      else /* AUTO */
      {
         valid = 1;

         /* Try DHTXX first. */

         h = ((float)((byte[4]<<8) + byte[3]))/10.0;

         if (h > 110.0) valid = 0;

         if (byte[2] & 128) div = -10.0; else div = 10.0;

         t = ((float)(((byte[2]&127)<<8) + byte[1])) / div;

         if ((t < -50.0) || (t > 135.0)) valid = 0;

         if (!valid)
         {
            /* If not DHTXX try DHT11. */

            if ((byte[1] == 0) && (byte[3] == 0))
            {
               valid = 1;

               t = byte[2];

               if (t > 60.0) valid = 0;

               h = byte[4];

               if ((h < 10.0) || (h > 90.0)) valid = 0;
            }
         }
      }

      if (valid)
      {
         status = DHT_GOOD;

         *rh = h;
         *temp = t;
      }
      else status = DHT_BAD_DATA;
   }
   else status = DHT_BAD_CHECKSUM;

   return status;
}

static int status;
static float h=0, t=0;

void afunc(int e, lgGpioAlert_p evt, void *data)
{
   int i;
   uint64_t edge_len, now_tick;
   static int bits = 0;
   static uint64_t reading = 0;
   static uint64_t last_tick = 0;

   for (i=0; i<e; i++)
   {
      if (evt[i].report.level != LG_TIMEOUT)
      {
         now_tick = evt[i].report.timestamp;
         edge_len = now_tick - last_tick;
         last_tick = now_tick;
         if (edge_len > 1e6) // a millisecond
         {
            reading = 0;
            bits = 0;
         }
         else
         {
            reading <<= 1;
            if (edge_len > 1e5) reading |= 1; // longer than 100 micros
            ++bits;
         }
      }
      else
      {
         status = decode_dhtxx(reading, DHTAUTO, &t, &h);
         reading = 0;
         bits = 0;
      }
   }
}

int main(int argc, char *argv[])
{
   int i, g;
   int v;
   int loop;
   int fd;
   int chip;
   int num_gpio;
   int gpio[MAX_GPIO];
   int err;
   int count;

   chip = lgGpiochipOpen(0);

   if (argc > 1)
   {
      num_gpio=argc-1;
      if (num_gpio > MAX_GPIO) num_gpio = MAX_GPIO;
      for (g=0; g<num_gpio; g++) gpio[g] = atoi(argv[g+1]);
   }
   else
   {
      num_gpio = 1;
      gpio[0] = 4;
   }

   if (chip >= 0)
   {
      lgGpioSetUser(chip, "niagra");
      lgGpioSetSamplesFunc(afunc, (void*)123456);

      for (g=0; g<num_gpio; g++)
      {
         lgGpioSetWatchdog(chip, gpio[g], 1000); /* millisecond watchdog */
      }

      for (loop=0; loop<200000; loop++)
      {
         for (g=0; g<num_gpio; g++)
         {
            err = lgGpioClaimOutput(chip, 0, gpio[g], 0);
            if (err) fprintf(stderr, "set out err %d\n", err);

            usleep(15000);

            err = lgGpioClaimAlert(
               chip, 0, LG_RISING_EDGE, gpio[g], -1);
            if (err) fprintf(stderr, "set event err %d\n", err);

            count = 0;
            status = DHT_TIMEOUT;

            while ((status == DHT_TIMEOUT) && (++count<11)) usleep(1000);

            printf("%d %.1f %.1f (g=%d)\n", status, t, h, gpio[g]);

            fflush(NULL);
         }
         sleep(3);
      }

      lgGpiochipClose(chip);
   }
   else
   {
      fprintf(stderr, "open /dev/gpiochip0 failed (%d)\n", chip);
   }
}

