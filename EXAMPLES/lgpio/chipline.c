/*
bench.c
2020-11-18
Public Domain

http://abyz.me.uk/lg/lgpio.html

gcc -Wall -o bench bench.c -llgpio

./bench
*/
#include <stdio.h>

#include <lgpio.h>

int main(int argc, char *argv[])
{
   int h;
   int i;
   lgChipInfo_t cinf;
   lgLineInfo_t linf;

   h = lgGpiochipOpen(0);
   if (h >= 0)
   {
      if (lgGpioGetChipInfo(h, &cinf) == LG_OKAY)
      {
         printf("%d \"%s\" \"%s\"\n", cinf.lines, cinf.name, cinf.label);

         for (i=0; i<cinf.lines; i++)
         {
            if (lgGpioGetLineInfo(h, i, &linf) == LG_OKAY)
            {
               printf("%d %d \"%s\" \"%s\"\n",
                  linf.offset, linf.lFlags, linf.name, linf.user);
            }
         }
      }

      lgGpiochipClose(h);
   }
}

