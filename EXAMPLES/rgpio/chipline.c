/*
chipline.c
2020-11-18
Public Domain

http://abyz.me.uk/lg/rgpio.html

gcc -Wall -o chipline chipline.c -lrgpio

./chipline
*/

#include <stdio.h>
#include <stdlib.h>

#include <lgpio.h>
#include <rgpio.h>

int main(int argc, char *argv[])
{
   int sbc;
   int h;
   int i;
   lgChipInfo_t cinf;
   lgLineInfo_t linf;

   sbc = rgpiod_start(NULL, NULL);

   if (sbc < 0)
   {
      printf("connection failed\n");
      exit(-1);
   }

   h = gpiochip_open(sbc, 0);

   if (h >= 0)
   {
      if (gpio_get_chip_info(sbc, h, &cinf) == LG_OKAY)
      {
         printf("%d \"%s\" \"%s\"\n", cinf.lines, cinf.name, cinf.label);

         for (i=0; i<cinf.lines; i++)
         {
            if (gpio_get_line_info(sbc, h, i, &linf) == LG_OKAY)
            {
               printf("%d %d \"%s\" \"%s\"\n",
                  linf.offset, linf.lFlags, linf.name, linf.user);
            }
         }
      }

      gpiochip_close(sbc, h);
   }

   rgpiod_stop(sbc);
}

