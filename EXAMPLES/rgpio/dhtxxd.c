/*
dhtxxd.c
2020-08-14
Public Domain
*/

/*

REQUIRES

One or more DHT11/DHT21/DHT22/DHT33/DHT44.

TO BUILD

gcc -Wall -o dhtxxd dhtxxd.c -lrgpio

TO RUN

./dhtxxd -g17 # one reading from DHT connected to GPIO 17

./dhtxxd -g14 -i3 # read DHT connected to GPIO 14 every 3 seconds

*/

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <unistd.h>

#include <rgpio.h>

struct DHTXXD_s;

typedef struct DHTXXD_s DHTXXD_t;

#define DHTAUTO 0
#define DHT11   1
#define DHTXX   2

#define DHT_GOOD         0
#define DHT_BAD_CHECKSUM 1
#define DHT_BAD_DATA     2
#define DHT_TIMEOUT      3

typedef struct
{
   int sbc;
   int chip;
   int gpio;
   int status;
   float temperature;
   float humidity;
   double timestamp;
} DHTXXD_data_t;

typedef void (*DHTXXD_CB_t)(DHTXXD_data_t);

/*
DHTXXD starts a DHTXX sensor on sbc with GPIO gpio.

The model may be auto detected (DHTAUTO), or specified as a
DHT11 (DHT11), or DHT21/22/33/44 (DHTXX).

If cb_func is not null it will be called at each new reading
whether the received data is valid or not.  The callback
receives a DHTXXD_data_t object.

If cb_func is null then the DHTXXD_ready function should be
called to check for new data which may then be retrieved by
a call to DHTXXD_data.

A single reading may be triggered with DHTXXD_manual_read.

A reading may be triggered at regular intervals using
DHTXXD_auto_read.  If the auto trigger interval is 30
seconds or greater two readings will be taken and only
the second will be returned.  I would not read the
DHT22 more than once every 3 seconds.  The DHT11 can
safely be read once a second.  I don't know about the
other models.

At program end the DHTXX sensor should be cancelled using
DHTXXD_cancel.  This releases system resources.
*/

DHTXXD_t     *DHTXXD             (int sbc,
                                  int chip,
                                  int gpio,
                                  int model,
                                  DHTXXD_CB_t cb_func);

void          DHTXXD_cancel      (DHTXXD_t *self);

int           DHTXXD_ready       (DHTXXD_t *self);

DHTXXD_data_t DHTXXD_data        (DHTXXD_t *self);

void          DHTXXD_manual_read (DHTXXD_t *self);

void          DHTXXD_auto_read   (DHTXXD_t *self, float seconds);

/*

Code to read the DHTXX temperature/humidity sensors.

*/

/* PRIVATE ---------------------------------------------------------------- */

struct DHTXXD_s
{
   int sbc;
   int chip;
   int gpio;
   int model;
   int seconds;
   DHTXXD_CB_t cb;
   int _cb_id;
   pthread_t *_pth;
   union
   {
      uint8_t _byte[8];
      uint64_t _code;
   };
   int _bits;
   int _ready;
   int _new_reading;
   DHTXXD_data_t _data;
   uint64_t _last_edge_tick;
   int _ignore_reading;
};

static void _decode_dhtxx(DHTXXD_t *self)
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
   uint8_t chksum;
   float div;
   float t, h;
   int valid;

   self->_data.timestamp = lgu_time();

   chksum = (self->_byte[1] + self->_byte[2] +
             self->_byte[3] + self->_byte[4]) & 0xFF;

   valid = 0;

   if (chksum == self->_byte[0])
   {
      if (self->model == DHT11)
      {
         if ((self->_byte[1] == 0) && (self->_byte[3] == 0))
         {
            valid = 1;

            t = self->_byte[2];

            if (t > 60.0) valid = 0;

            h = self->_byte[4];

            if ((h < 10.0) || (h > 90.0)) valid = 0;
         }
      }
      else if (self->model == DHTXX)
      {
         valid = 1;

         h = ((float)((self->_byte[4]<<8) + self->_byte[3]))/10.0;

         if (h > 110.0) valid = 0;

         if (self->_byte[2] & 128) div = -10.0; else div = 10.0;

         t = ((float)(((self->_byte[2]&127)<<8) + self->_byte[1])) / div;

         if ((t < -50.0) || (t > 135.0)) valid = 0;
      }
      else /* AUTO */
      {
         valid = 1;

         /* Try DHTXX first. */

         h = ((float)((self->_byte[4]<<8) + self->_byte[3]))/10.0;

         if (h > 110.0) valid = 0;

         if (self->_byte[2] & 128) div = -10.0; else div = 10.0;

         t = ((float)(((self->_byte[2]&127)<<8) + self->_byte[1])) / div;

         if ((t < -50.0) || (t > 135.0)) valid = 0;

         if (!valid)
         {
            /* If not DHTXX try DHT11. */

            if ((self->_byte[1] == 0) && (self->_byte[3] == 0))
            {
               valid = 1;

               t = self->_byte[2];

               if (t > 60.0) valid = 0;

               h = self->_byte[4];

               if ((h < 10.0) || (h > 90.0)) valid = 0;
            }
         }
      }

      if (valid)
      {
         self->_data.temperature = t;
         self->_data.humidity = h;
         self->_data.status = DHT_GOOD;
         self->_new_reading = 1;
         self->_ready = 1;
         self->_bits = 0;
         if (self->cb) (self->cb)(self->_data);
      }
      else
      {
         self->_data.status = DHT_BAD_DATA;
      }
   }
   else
   {
      self->_data.status = DHT_BAD_CHECKSUM;
   }
}

static void _rising_edge(
   int sbc, int chip, int gpio, int level, uint64_t tick, void *user)
{
   DHTXXD_t *self=user;
   uint64_t edge_len;

   if (level != LG_TIMEOUT)
   {
      edge_len = tick - self->_last_edge_tick;
      self->_last_edge_tick = tick;

      if (edge_len > 2e8) // 0.2 seconds
      {
         self->_bits = 0;
         self->_code = 0;
      }
      else
      {
         self->_code <<= 1;

         if (edge_len > 1e5) // 100 microseconds, so a high bit
         {
            /* 1 bit */
            self->_code |= 1;
         }

         self->_bits ++;
      }
   }
   else
   {
      if (self->_bits >= 30)
      {
         if (!self->_ignore_reading) _decode_dhtxx(self);

         self->_bits = 0;
         self->_code = 0;
      }
   }
}

static void _trigger(DHTXXD_t *self)
{
   gpio_claim_output(self->sbc, self->chip, 0, self->gpio, 0);

   if (self->model != DHTXX) lgu_sleep(0.018); else lgu_sleep(0.001);

   gpio_claim_alert(self->sbc, self->chip, 0, RISING_EDGE, self->gpio, -1);
}

static void *pthTriggerThread(void *x)
{
   DHTXXD_t *self=x;
   float seconds;

   seconds = self->seconds;

   while (1)
   {
      if (seconds > 0.0)
      {
         if (seconds >= 30.0)
         {
            lgu_sleep(seconds - 4.0);
            self->_ignore_reading = 1;
            _trigger(self);
            lgu_sleep(4.0);
            self->_ignore_reading = 0;
         }
         else lgu_sleep(seconds);

         DHTXXD_manual_read(self);
      }
      else lgu_sleep(1);
   }
   pthread_exit(NULL);
}

/* PUBLIC ----------------------------------------------------------------- */

DHTXXD_t *DHTXXD(int sbc, int chip, int gpio, int model, DHTXXD_CB_t cb_func)
{
   DHTXXD_t *self;

   self = malloc(sizeof(DHTXXD_t));

   if (!self) return NULL;

   self->sbc = sbc;
   self->chip = chip;
   self->gpio = gpio;
   self->model = model;
   self->seconds = 0;
   self->cb = cb_func;

   self->_data.sbc = sbc;
   self->_data.gpio = gpio;
   self->_data.status = 0;
   self->_data.temperature = 0.0;
   self->_data.humidity = 0.0;

   self->_ignore_reading = 0;

   self->_pth = NULL;

   self->_bits = 0;

   self->_ready = 0;
   self->_new_reading = 0;

   self->_last_edge_tick = 0;

   gpio_set_watchdog_time(sbc, chip, gpio, 1000); // 1 ms watchdog

   self->_cb_id = callback(sbc, chip, gpio, RISING_EDGE, _rising_edge, self);

   return self;
}

void DHTXXD_cancel(DHTXXD_t *self)
{
   if (self)
   {
      if (self->_pth)
      {
         thread_stop(self->_pth);
         self->_pth = NULL;
      }

      if (self->_cb_id >= 0)
      {
         callback_cancel(self->_cb_id);
         self->_cb_id = -1;
      }
      free(self);
   }
}
int DHTXXD_ready(DHTXXD_t *self)
{
   /*
   Returns True if a new unread code is ready.
   */
   return self->_ready;
}

DHTXXD_data_t DHTXXD_data(DHTXXD_t *self)
{
   /*
   Returns the last reading.
   */
   self->_ready = 0;
   return self->_data;
}

void DHTXXD_manual_read(DHTXXD_t *self)
{
   int i;
   double timestamp;

   self->_new_reading = 0;
   self->_data.status = DHT_TIMEOUT;

   timestamp = lgu_time();

   _trigger(self);

   /* timeout if no new reading */

   for (i=0; i<4; i++) /* timeout after 0.2 seconds */
   {
      lgu_sleep(0.05);
      if (self->_new_reading) break;
   }

   if (!self->_new_reading)
   {
      self->_data.timestamp = timestamp;
      self->_ready = 1;

      if (self->cb) (self->cb)(self->_data);
   }
}

void DHTXXD_auto_read(DHTXXD_t *self, float seconds)
{
   if (seconds != self->seconds)
   {
      /* Delete any existing timer thread. */
      if (self->_pth != NULL)
      {
         thread_stop(self->_pth);
         self->_pth = NULL;
      }
      self->seconds = seconds;
   }

   if (seconds > 0.0) self->_pth = thread_start(pthTriggerThread, self);
}

void fatal(char *fmt, ...)
{
   char buf[128];
   va_list ap;

   va_start(ap, fmt);
   vsnprintf(buf, sizeof(buf), fmt, ap);
   va_end(ap);

   fprintf(stderr, "%s\n", buf);

   fflush(stderr);

   exit(EXIT_FAILURE);
}

void usage()
{
   fprintf(stderr, "\n" \
      "Usage: DHTXXD [OPTION] ...\n" \
      "   -g value, gpio, 0-31,                       default 4\n" \
      "   -i value, reading interval in seconds\n" \
      "             0=single reading,                 default 0\n" \
      "   -m value, model 0=auto, 1=DHT11, 2=other,   default auto\n" \
      "   -h string, host name,                       default NULL\n" \
      "   -p value, socket port, 1024-32000,          default 8888\n" \
      "EXAMPLE\n" \
      "DHTXXD -g11 -i5\n" \
      "   Read a DHT connected to GPIO 11 every 5 seconds.\n\n");
}

int optGPIO     = 4;
char *optHost   = NULL;
char *optPort   = NULL;
int optModel    = DHTAUTO;
int optInterval = 0;

static uint64_t getNum(char *str, int *err)
{
   uint64_t val;
   char *endptr;

   *err = 0;
   val = strtoll(str, &endptr, 0);
   if (*endptr) {*err = 1; val = -1;}
   return val;
}

static void initOpts(int argc, char *argv[])
{
   int opt, err, i;

   while ((opt = getopt(argc, argv, "g:h:i:m:p:")) != -1)
   {
      switch (opt)
      {
         case 'g':
            i = getNum(optarg, &err);
            if ((i >= 0) && (i <= 31)) optGPIO = i;
            else fatal("invalid -g option (%d)", i);
            break;

         case 'h':
            optHost = malloc(sizeof(optarg)+1);
            if (optHost) strcpy(optHost, optarg);
            break;

         case 'i':
            i = getNum(optarg, &err);
            if ((i>=0) && (i<=86400)) optInterval = i;
            else fatal("invalid -i option (%d)", i);
            break;

         case 'm':
            i = getNum(optarg, &err);
            if ((i >= DHTAUTO) && (i <= DHTXX)) optModel = i;
            else fatal("invalid -m option (%d)", i);
            break;

         case 'p':
            optPort = malloc(sizeof(optarg)+1);
            if (optPort) strcpy(optPort, optarg);
            break;

        default: /* '?' */
           usage();
           exit(-1);
        }
    }
}

void cbf(DHTXXD_data_t r)
{
   printf("%d %.1f %.1f\n", r.status, r.temperature, r.humidity);
}

int main(int argc, char *argv[])
{
   int sbc;
   int chip;
   DHTXXD_t *dht;

   initOpts(argc, argv);

   sbc = rgpiod_start(optHost, optPort); /* Connect to local sbc. */

   if (sbc >= 0)
   {
      /* open gpiochip 0 */

      chip = gpiochip_open(sbc, 0);

      dht = DHTXXD(sbc, chip, optGPIO, optModel, cbf); /* Create DHTXX. */

      if (optInterval)
      {
         DHTXXD_auto_read(dht, optInterval);

         while (1) lgu_sleep(60);
      }
      else
      {
         DHTXXD_manual_read(dht);
      }

      DHTXXD_cancel(dht); /* Cancel DHTXX. */

      gpiochip_close(sbc, chip);

      rgpiod_stop(sbc); /* Disconnect from local sbc. */
   }
   else printf("can't connect to lgd\n");

   return 0;
}

