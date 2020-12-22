/*
tx_servo.c
2020-12-21
Public Domain

http://abyz.me.uk/lg/lgpio.html

gcc -Wall -o tx_servo tx_servo.c -llgpio

./tx_servo
*/

#include <stdio.h>
#include <stdlib.h>

#include <lgpio.h>

#define SERVO 21

#define LFLAGS 0

int main(int argc, char *argv[])
{
   int h;

   h = lgGpiochipOpen(0);

   if (h >= 0)
   {
      if (lgGpioClaimOutput(h, LFLAGS, SERVO, 0) == LG_OKAY)
      {
         lgTxServo(h, SERVO, 1500, 50, 0, 0); /* 1500 microseconds, 50 Hz */
         lguSleep(60);
      }

      lgGpiochipClose(h);
   }
}

