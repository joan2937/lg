#ifndef LG_ADS1X15_H
#define LG_ADS1X15_H

/*
lg_ads1x15.h
2021-01-16
Public Domain

http://abyz.me.uk/lg/lgpio.html
http://abyz.me.uk/lg/rgpio.html

ADS1X15

*/

#define   ADS1X15_A0_1 0
#define   ADS1X15_A0_3 1
#define   ADS1X15_A1_3 2
#define   ADS1X15_A2_3 3
#define   ADS1X15_A0   4
#define   ADS1X15_A1   5
#define   ADS1X15_A2   6
#define   ADS1X15_A3   7

#define   ADS1X15_ALERT_NEVER       0
#define   ADS1X15_ALERT_READY       1
#define   ADS1X15_ALERT_TRADITIONAL 2
#define   ADS1X15_ALERT_WINDOW      3

typedef struct ads1x15_s ads1x15_t, *ads1x15_p;

ads1x15_p ADS1015_open(int sbc, int bus, int device, int flags);
/* get a handle to an ADS1015 */

ads1x15_p ADS1115_open(int sbc, int bus, int device, int flags);
/* get a handle to an ADS1115 */

ads1x15_p ADS1X15_close(ads1x15_p s);
/* release an ADS1X15 handle */

int ADS1X15_set_channel(ads1x15_p s, int channel);
/*
Set the channel to be used for conversions.

May be one of the following constants:

ADS1X15_A0 - single-ended A0
ADS1X15_A1 - single-ended A1
ADS1X15_A2 - single-ended A2
ADS1X15_A3 - single-ended A3

ADS1X15_A0_1 - differential A0 - A1
ADS1X15_A0_3 - differential A0 - A3
ADS1X15_A1_3 - differential A1 - A3
ADS1X15_A2_3 - differential A2 - A3

Returns the channel set.
*/

int ADS1X15_get_channel(ads1x15_p s);
const char * ADS1X15_get_channel_name(ads1x15_p s);

float ADS1X15_set_voltage_range(ads1x15_p s, float vrange);
/*
Set the voltage range.

Any value less than the minimum will set the minimum rate.  Any
value greater than the maximum will set the maximum rate.

The ADS1015/ADS1115 support voltage ranges 256 mV, 512 mV, 1.024 V,
2.048 V, 4.096 V, and 6.144 V.

The first range greater than or equal to the specified value will
be set,

The set voltage range will be returned.
*/

float ADS1X15_get_voltage_range(ads1x15_p s);

int ADS1X15_set_sample_rate(ads1x15_p s, int rate);
/*
Set the sample rate.

Any value less than the minimum will set the minimum rate.  Any
value greater than the maximum will set the maximum rate.

The ADS1015 supports 128, 250, 490, 920, 1600, 2400, and 3300
samples per second.

The ADS1115 supports 8, 16, 32, 64, 128, 250, 475, and 860 samples
per second.

The first sample rate greater than or equal to the specified
value will be set,

The set samples per second will be returned.
*/

int ADS1X15_get_sample_rate(ads1x15_p s);

int ADS1X15_set_continuous_mode(ads1x15_p s);
/* Set continuous conversion mode. */

int ADS1X15_set_single_shot_mode(ads1x15_p s);
/* Set single-shot conversion mode. */

int ADS1X15_get_conversion_mode(ads1x15_p s);

int ADS1X15_read(ads1x15_p s);
/*
Returns the last conversion value.  For the ADS1115 this is a
16-bit quantity,  For the ADS1015 this is a 12-bit quantity.
The returned ADS1015 value is multiplied by 16 so it has the
same range as the ADS1115.
*/

float ADS1X15_read_voltage(ads1x15_p s);
/* Returns the last conversion value as a voltage. */

int ADS1X15_alert_never(ads1x15_p s);
/* Set the ALERT/RDY pin to unused. */

int ADS1X15_alert_when_high_clear_when_low(ads1x15_p s, float vhigh, float vlow);
/*
Set the ALERT/RDY pin to be used as an alert signal.

The ALERT/RDY pin will be asserted when the voltage goes
above high.  It will continue to be asserted until the
voltage drops beneath low.

This sets continuous conversion mode.

To be useful your script will have to monitor the
ALERT/RDY pin and react when it changes level (both
edges is probably best).
*/

int ADS1X15_alert_when_high_or_low(ads1x15_p s, float vhigh, float vlow);
/*
Set the ALERT/RDY pin to be used as an alert signal.

The ALERT/RDY pin will be asserted when the voltage goes
above high or drops beneath low.  It will continue to be
asserted until the voltage is between low to high.

This sets continuous conversion mode.

To be useful your script will have to monitor the
ALERT/RDY pin and react when it changes level (both
edges is probably best).
*/

int ADS1X15_alert_when_ready(ads1x15_p s);
/*
Set the ALERT/RDY pin to be used as a conversion
complete signal.

This sets continuous conversion mode.

To be useful your script will have to monitor the
ALERT/RDY pin and react when it is asserted (use
falling edge if comparator polarity is the default 0,
rising edge if comparator polarity is 1).
*/

int ADS1X15_get_alert_status(ads1x15_p s, int *high, int *low);
/*
Gets the type of alert (one of the ADS1X15_ALERT constants)
and the value set in the high and low compare resisters.
*/

int ADS1X15_set_comparator_latch(ads1x15_p s, int value);
/*
Sets whether the ALERT/RDY pin stays active when asserted
or whether it is cleared automatically if the alert condition
is no longer present.

True or non-zero sets latch on, False or 0 sets latch off.
*/

int ADS1X15_get_comparator_latch(ads1x15_p s);

int ADS1X15_set_comparator_polarity(ads1x15_p s, int level);
/*
Set the level of the ALERT/RDY pin when active.

1 for active high, 0 for active low.
*/

int ADS1X15_get_comparator_polarity(ads1x15_p s);

int ADS1X15_set_comparator_queue(ads1x15_p s, int queue);
/*
Sets the number of consecutive alert readings required
before asserting the ALERT/RDY pin.

0 for 1 reading
1 for 2 readings
2 for 4 readings
*/

int ADS1X15_get_comparator_queue(ads1x15_p s);

#endif

