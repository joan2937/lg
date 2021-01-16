/*
lgr_ads1x15.c
2021-01-16
Public Domain
*/

#include <stdio.h>
#include <stdlib.h>

#include <rgpio.h>

#include "lg_ads1x15.h"

/*
   ada1015 4 ch 12-bit ADC 3300 sps
   ads1115 4 ch 16-bit ADC 860 sps

   F E D C   B A 9 8   7 6 5 4   3 2 1 0
   Z C C C   V V V S   R R R W   P L Q Q

   Z    1=start conversion
   CCC  0=A0/A1(*) 1=A0/A3 2=A1/A3 3=A2/A3 4=A0 5=A1 6=A2 7=A3
   VVV  0=6.144 1=4.096 2=2.048(*) 3=1.024 4=0.512 5=0.256 6=0.256 7=0.256
   S    0=continuous 1=single shot(*)
   RRR  0=8   1=16  2=32  3=64  4=128  5=250  6=475  7=860 sps ADS1115
   RRR  0=128 1=250 2=490 3=920 4=1600(*) 5=2400 6=3300 7=3300 sps ADS1015
   W    0=traditional(*) 1=window
   P    ALERT/RDY pin 0=active low(*)  1=active high
   L    comparator 0=non-latching(*) 1=latching
   QQ   queue 0=after 1 1=after 2, 2=after 4, 3=disable(*)
*/

typedef struct ads1x15_s
{
   int sbc;       // sbc connection
   int bus;       // I2C bus
   int device;    // I2C device
   int flags;     // I2C flags
   int i2ch;      // I2C handle
   int alert_rdy; // mode of ALERT_RDY pin
   int configH;   // config high byte
   int configL;   // config low byte
   int channel;   // channel setting
   int gain;      // gain setting
   int *SPS;      // array of legal samples per seconds
   float voltage_range; // voltage range (set by gain setting)
   float vhigh;   // alert high voltage
   float vlow;    // alert low voltage
   int single_shot; // single shot setting
   int sps;       // samples per second setting
   int comparator_mode;
   int comparator_polarity;
   int comparator_latch;
   int comparator_queue;
   int compare_high; // set from vhigh
   int compare_low;  // set from vlow
   int set_queue;    // set from comparator queue
} ads1x15_t, *ads1x15_p;


float _GAIN[]=
   {6.144, 4.096, 2.048, 1.024, 0.512, 0.256, 0.256, 0.256};

const char *_CHAN[]=
   {"A0-A1", "A0-A3", "A1-A3", "A2-A3", "A0", "A1", "A2", "A3"};

int _SPS_1015[]={128, 250, 490, 920, 1600, 2400, 3300, 3300};
int _SPS_1115[]={  8,  16,  32,  64,  128,  250,  475,  860};


#define CONVERSION_REG 0
#define CONFIG_REG 1
#define COMPARE_LOW_REG 2
#define COMPARE_HIGH_REG 3

int _read_config(ads1x15_p s)
{
   unsigned char buf[8];

   buf[0] = CONFIG_REG;

   i2c_write_device(s->sbc, s->i2ch, buf, 1);  // set config register

   i2c_read_device(s->sbc, s->i2ch, buf, 2);

   s->configH = buf[0];
   s->configL = buf[1];

   buf[0] = COMPARE_LOW_REG;

   i2c_write_device(s->sbc, s->i2ch, buf, 1); // set low compare register

   i2c_read_device(s->sbc, s->i2ch, buf, 2);

   s->compare_low = (buf[0] << 8) | buf[1];

   buf[0] = COMPARE_HIGH_REG;

   i2c_write_device(s->sbc, s->i2ch, buf, 1); // set high compare register

   i2c_read_device(s->sbc, s->i2ch, buf, 2);

   s->compare_high = (buf[0] << 8) | buf[1];

   buf[0] = CONVERSION_REG;

   i2c_write_device(s->sbc, s->i2ch, buf, 1); // set conversion register

   s->channel = (s->configH >> 4) & 7;
   s->gain = (s->configH >> 1) & 7;
   s->voltage_range = _GAIN[s->gain];
   s->single_shot = s->configH & 1;
   s->sps = (s->configL >> 5) & 7;
   s->comparator_mode = (s->configL >> 4) & 1;
   s->comparator_polarity = (s->configL >> 3) & 1;
   s->comparator_latch = (s->configL >> 2) & 1;
   s->comparator_queue = s->configL & 3;

   if (s->comparator_queue != 3)
      s->set_queue = s->comparator_queue;
   else
      s->set_queue = 0;

   return 0;
}

int _write_config(ads1x15_p s)
{
   unsigned char buf[8];

   buf[0] = CONFIG_REG;
   buf[1] = s->configH;
   buf[2] = s->configL;

   i2c_write_device(s->sbc, s->i2ch, buf, 3);

   buf[0] = CONVERSION_REG;

   i2c_write_device(s->sbc, s->i2ch, buf, 1);

   return 0;
}

int _write_comparator_thresholds(ads1x15_p s, int high, int low)
{
   unsigned char buf[8];

   if (high > 32767) high = 32767;
   else if (high < -32768) high = -32768;

   if (low > 32767) low = 32767;
   else if (low < -32768) low = -32768;

   s->compare_high = high;
   s->compare_low = low;

   buf[0] = COMPARE_LOW_REG;
   buf[1] = (low >> 8) & 0xff;
   buf[2] = low & 0xff;

   i2c_write_device(s->sbc, s->i2ch, buf, 3);

   buf[0] = COMPARE_HIGH_REG;
   buf[1] = (high >> 8) & 0xff;
   buf[2] = high & 0xff;

   i2c_write_device(s->sbc, s->i2ch, buf, 3);

   buf[0] = CONVERSION_REG;

   i2c_write_device(s->sbc, s->i2ch, buf, 1);

   return 0;
}

int _update_comparators(ads1x15_p s)
{
   int h, l;

   if (s->alert_rdy >= ADS1X15_ALERT_TRADITIONAL)
   {
      h = s->vhigh * 32768.0 / s->voltage_range;
      l = s->vlow * 32768.0 / s->voltage_range;

      return _write_comparator_thresholds(s, h, l);
   }

   return 0;
}

int _update_config(ads1x15_p s)
{
   int H, L;

   H = s->configH;
   L = s->configL;

   s->configH = ((1 << 7) | (s->channel << 4) |
      (s->gain << 1) | s->single_shot);

   s->configL = ((s->sps << 5) | (s->comparator_mode << 4) |
      (s->comparator_polarity << 3) | (s->comparator_latch << 2) |
      s->comparator_queue);

   if ((H != s->configH) || (L != s->configL)) _write_config(s);

   return 0;
}

int ADS1X15_set_comparator_polarity(ads1x15_p s, int level)
{
   if (level) s->comparator_polarity = 1;
   else s->comparator_polarity = 0;

   return _update_config(s);
}

int ADS1X15_get_comparator_polarity(ads1x15_p s)
   { return s->comparator_polarity; }

int ADS1X15_set_comparator_latch(ads1x15_p s, int value)
{
      if (value) s->comparator_latch = 1;
      else       s->comparator_latch = 0;

      return _update_config(s);
}

int ADS1X15_get_comparator_latch(ads1x15_p s) { return s->comparator_latch; }


int ADS1X15_set_comparator_queue(ads1x15_p s, int queue)
{
   if ((queue >= 0) && (queue <= 2))
   {
      s->set_queue = queue;
      return _update_config(s);
   }

   return -1;
}

int ADS1X15_get_comparator_queue(ads1x15_p s) { return s->set_queue; }


int ADS1X15_set_continuous_mode(ads1x15_p s)
{
      s->single_shot = 0;
      return _update_config(s);
}

int ADS1X15_set_single_shot_mode(ads1x15_p s)
{
   s->single_shot = 1;
   return _update_config(s);
}

int ADS1X15_get_conversion_mode(ads1x15_p s) { return s->single_shot; }

int ADS1X15_set_sample_rate(ads1x15_p s, int rate)
{
   int val, i;

   val = 7;

   for (i=0; i<8; i++)
   {
      if (rate <= s->SPS[i])
      {
         val = i;
         break;
      }
   }

   s->sps = val;
   _update_config(s);

   return s->SPS[val];
}

int ADS1X15_get_sample_rate(ads1x15_p s) { return s->SPS[s->sps]; }

float ADS1X15_set_voltage_range(ads1x15_p s, float vrange)
{
   int val, i;

   val = 7;

   for (i=0; i<8; i++)
   {
      if (vrange > _GAIN[i])
      {
         val = i;
         break;
      }
   }

   if (val > 0) val = val - 1;

   s->gain = val;

   s->voltage_range = _GAIN[val];

   _update_comparators(s);

   _update_config(s);

   return s->voltage_range;
}

float ADS1X15_get_voltage_range(ads1x15_p s) { return _GAIN[s->gain]; }

int ADS1X15_set_channel(ads1x15_p s, int channel)
{
   if (channel < 0) channel = 0;
   else if (channel > 7) channel = 7;

   s->channel = channel;

   _update_config(s);

   return channel;
}

int   ADS1X15_get_channel(ads1x15_p s) { return s->channel; }

const char*ADS1X15_get_channel_name(ads1x15_p s) { return _CHAN[s->channel];}

int ADS1X15_alert_when_high_clear_when_low(ads1x15_p s, float vhigh, float vlow)
{
   s->vhigh = vhigh;
   s->vlow = vlow;

   s->comparator_mode = 0; // traditional
   s->comparator_queue = s->set_queue;
   s->alert_rdy = ADS1X15_ALERT_TRADITIONAL;
   _update_comparators(s);
   s->single_shot = 0; // must be in continuous mode
   return _update_config(s);
}

int ADS1X15_alert_when_high_or_low(ads1x15_p s, float vhigh, float vlow)
{
   s->vhigh = vhigh;
   s->vlow = vlow;

   s->comparator_mode = 1; // window
   s->comparator_queue = s->set_queue;
   s->alert_rdy = ADS1X15_ALERT_WINDOW;
   _update_comparators(s);
   s->single_shot = 0; // must be in continuous mode
   return _update_config(s);
}

int ADS1X15_alert_when_ready(ads1x15_p s)
{
   _write_comparator_thresholds(s, -1, 1); // conversion alerts
   s->comparator_queue = s->set_queue;
   s->alert_rdy = ADS1X15_ALERT_READY;
   s->single_shot = 0; // must be in continuous mode
   return _update_config(s);
}

int ADS1X15_alert_never(ads1x15_p s)
{
   s->comparator_queue = 3;
   s->compare_high = 0;
   s->compare_low = 0;
   s->alert_rdy = ADS1X15_ALERT_NEVER;
   return _update_config(s);
}

int ADS1X15_get_alert_data(ads1x15_p s, int *high, int *low)
{
   *high = s->compare_high;
   *low = s->compare_low;
   return s->alert_rdy;
}

int ADS1X15_read_config_data(ads1x15_p s, int *high, int *low)
{
   _read_config(s);

   *high = s->compare_high;
   *low = s->compare_low;
   return (s->configH << 8) | s->configL;
}

int ADS1X15_read(ads1x15_p s)
{
   unsigned char buf[8];

   if (s->single_shot) _write_config(s);
  
   i2c_read_device(s->sbc, s->i2ch, buf, 2);

   return (buf[0]<<8) + buf[1];
}

float ADS1X15_read_voltage(ads1x15_p s)
{
   return ADS1X15_read(s) * s->voltage_range / 32768.0;
}


ads1x15_p ADS1X15_open(int sbc, int bus, int device, int flags)
{
   ads1x15_p s;

   s = calloc(1, sizeof(ads1x15_t));

   if (s == NULL) return NULL;

   s->sbc = sbc;         // sbc connection
   s->bus = bus;         // I2C bus
   s->device = device;   // I2C device
   s->flags = flags;     // I2C flags

   s->SPS = _SPS_1015;   // default

   s->i2ch = i2c_open(sbc, bus, device, flags);

   if (s->i2ch < 0)
   {
      free(s);
      return NULL;
   }

   _read_config(s);

   ADS1X15_alert_never(s); // switch off ALERT/RDY pin.

   return s;
}

ads1x15_p ADS1015_open(int sbc, int bus, int device, int flags)
{
   ads1x15_p s;

   s = ADS1X15_open(sbc, bus, device, flags);

   if (s) s->SPS = _SPS_1015;

   return s;
}

ads1x15_p ADS1115_open(int sbc, int bus, int device, int flags)
{
   ads1x15_p s;

   s = ADS1X15_open(sbc, bus, device, flags);

   if (s) s->SPS = _SPS_1115;

   return s;
}

ads1x15_p ADS1X15_close(ads1x15_p s)
{
   if (s != NULL)
   {
      i2c_close(s->sbc, s->i2ch);
      free(s);
      s = NULL;
   }
   return s;
}


#ifdef EXAMPLE

/*
gcc -D EXAMPLE -o ads1x15 lgr_ads1x15.c -lrgpio
./ads1x15
*/

#include <stdio.h>

#include <lgpio.h>
#include <rgpio.h>

#include "lg_ads1x15.h"

#define ALERT 21 /* set to the ALERT GPIO, -1 if not connected */

/* callback function */
void cbf(
   int sbc, int chip, int gpio, int level,
   uint64_t timestamp, void * userdata)
{
   ads1x15_p adc = userdata;

   printf("ALERT: %.2f\n", ADS1X15_read_voltage(adc));
}

int main(int argc, char *argv[])
{
   int sbc=-1;
   int h;
   int err;
   int cb_id;
   ads1x15_p adc=NULL;
   double end_time;

   sbc = rgpiod_start(NULL, NULL);

   if (sbc < 0) return -1;

   adc = ADS1015_open(sbc, 1, 0x48, 0);

   if (adc == NULL) return -2;

   ADS1X15_set_channel(adc, ADS1X15_A0);
   ADS1X15_set_voltage_range(adc, 3.3);
   ADS1X15_set_sample_rate(adc, 0); // set minimum sampling rate
   ADS1X15_alert_when_high_or_low(adc, 3, 1); // alert outside these voltages

   if (ALERT >= 0) /* ALERT pin connected */
   {
      h = gpiochip_open(sbc, 0);

      if (h <0) return -3;

      /* got a handle, now open the GPIO for alerts */
      err = gpio_claim_alert(sbc, h, 0, LG_BOTH_EDGES, ALERT, -1);
      if (err < 0) return -4;
      cb_id = callback(sbc, h, ALERT, LG_BOTH_EDGES, cbf, adc);
   }

   end_time = lgu_time() + 120;

   while (lgu_time() < end_time)
   {
      lgu_sleep(0.2);

      printf("%.2f\n", ADS1X15_read_voltage(adc));
   }

   ADS1X15_close(adc);

   if (ALERT >= 0) /* ALERT pin connected */
   {
      callback_cancel(cb_id);
      gpio_free(sbc, h, ALERT);
      gpiochip_close(sbc, h);
   }

   rgpiod_stop(sbc);

   return 0;
}

#endif

