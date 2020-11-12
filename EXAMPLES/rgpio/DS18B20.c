#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <lgpio.h>
#include <rgpio.h>

/*
# DS18B20.py
# 2020-09-09
# Public Domain

gcc -Wall -o DS18B20 DS18B20.c -lrgpio

./DS18B20

This uses the file interface to access the remote file system.

In this case it is used to access the sysfs 1-wire bus interface
to read any connected DS18B20 temperature sensors.

The remote permits file is used to grant access to
the remote file system.

For this example the file must contain the following line which
grants read access to DS18B20 device files for the test1 user.

[files]
test1=/sys/bus/w1/devices/28*\/w1_slave r

*/

int main(int argc, char *argv[])
{
   int sbc;
   int bytes;
   int h;
   char sensor[1024];
   char data[256];
   char *nameSP;
   char *nameEP;
   char *dataP;
   float t;

   sbc = rgpiod_start(0, 0);

   if (sbc < 0)
   {
      fprintf(stderr, "lg initialisation failed (sbc, %d).\n", sbc);
      return 1;
   }

   printf("Connected to lg daemon (%d).\n", sbc);

   lgu_set_user(sbc, "test1", ".lg_secret");

   while (1)
   {
      /* Get list of connected sensors. */
      bytes = file_list(
         sbc, "/sys/bus/w1/devices/28-00*/w1_slave", sensor, sizeof(sensor));

      if (bytes >= 0)
      {
         nameSP = sensor;
         while ((nameEP=strchr(nameSP, '\n')) != NULL)
         {
            t = 999.99;

            *nameEP = 0;

            /*

            Typical file name

            /sys/bus/w1/devices/28-000005d34cd2/w1_slave

            */

            h = file_open(sbc, nameSP, LG_FILE_READ);

            if (h >= 0)
            {
               file_read(sbc, h, data, sizeof(data));
               file_close(sbc, h);

               /*
               Typical file contents

               73 01 4b 46 7f ff 0d 10 41 : crc=41 YES
               73 01 4b 46 7f ff 0d 10 41 t=23187
               */

               if (strstr(data, "YES") != NULL)
               {
                  dataP = strstr(data, "t=");
                  if (dataP != NULL)
                  {
                     t = atoi(dataP+2) / 1000.0;
                  }
               }
            }

            nameSP += 20;     /* point to device id */
            *(nameSP+15) = 0; /* null terminate device id */
            printf("%s %.1f\n", nameSP, t);
            nameSP = nameEP+1; /* move to next line */
         }
      }
      else printf("no sensors found\n");

      lgu_sleep(3.0);
   }
}

