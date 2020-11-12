#include <stdio.h>
#include <stdlib.h>

#include <lgpio.h>
#include <rgpio.h>

/*
gcc -Wall -o files files.c -lrgpio

./files
*/

int sbc;
int h;
int s;
int i;
int mode;
int fails;
char data[2048];

void check(char *func, int exp, int got)
{
   if (exp != got)
      printf("FAIL: %s (expected %d, got %d)\n", func, exp, got);
   else
      printf("PASS: %s\n", func);
}

void check_no_error(char *func, int got)
{
   if (got < 0)
      printf("FAIL: %s (expected no error, got %d)\n", func, got);
   else
      printf("PASS: %s (%d)\n", func, got);
}

void check_error(char *func, int got)
{
   if (got < 0)
      printf("PASS: %s (%d)\n", func, got);
   else
      printf("FAIL: %s (expected error, got %d)\n", func, got);
}

void check_not_null(char *func, int got)
{
   if (got == 0)
      printf("FAIL: %s (expected name, got %d)\n", func, got);
   else
      printf("PASS: %s (%d)\n", func, got);
}

int main(int argc, char *argv[])
{
   sbc = rgpiod_start(NULL, NULL);

   if (sbc < 0)
   {
      printf("connection failed\n");
      exit(-1);
   }

   // open file for write, create if it doesn't exist

   h = file_open(sbc,
      "test.file", LG_FILE_WRITE+LG_FILE_CREATE+LG_FILE_TRUNC);
   check_no_error("file_open", h);

   // write some text

   s = file_write(sbc, h, "Now is the winter of our discontent\n", 36);
   check_no_error("file_write", s);

   s = file_write(sbc, h, "Made glorious summer by this son of York\n", 41);
   check_no_error("file_write", s);

   s = file_close(sbc, h);
   check_no_error("file_close", s);

   // open for read

   h = file_open(sbc, "test.file", LG_FILE_READ);
   check_no_error("file_open", h);

   s = file_read(sbc, h, data, 100); // read up to 100 characters from file
   check("file_read", 77, s);

   s = file_seek(sbc, h, 25, LG_FROM_START);
   check_no_error("file_seek", s);

   s = file_read(sbc, h, data, 100); // read up to 100 characters from file
   check("file_read", 52, s);

   s = file_seek(sbc, h, -25, LG_FROM_END);
   check_no_error("file_seek", s);

   s = file_read(sbc, h, data, 100); // read up to 100 charactrs from file
   check("file_read", 25, s);

   s = file_seek(sbc, h, -50, LG_FROM_END);
   check_no_error("file_seek", s);

   s = file_read(sbc, h, data, 5); // read up to 5 charactrs from file
   check("file_read", 5, s);

   file_seek(sbc, h, -20, LG_FROM_CURRENT);
   check_no_error("file_seek", s);

   s = file_read(sbc, h, data, 100); // read up to 100 charactrs from file
   check("file_read", 65, s);

   s = file_close(sbc, h);
   check_no_error("file_close", s);

   s = file_list(sbc, "test*", data, 1000);
   check_no_error("file_list", s);

   char *pat2[]={"/tmp/unlikely-file-name", "file34"};

   for (i=0; i<sizeof(pat2)/sizeof(char*); i++)
   {
      s = file_list(sbc, pat2[i], data, 1000);
      check("file_list", LG_NO_FILE_MATCH, s);
   }

   char *pat3[]={"/tmp/*", "test.*"};

   for (i=0; i<sizeof(pat3)/sizeof(char*); i++)
   {
      s = file_list(sbc, pat3[i], data, 1000);
      check_no_error("file_list", s);
   }

   // create a file

   h = file_open(sbc,
      "/tmp/unlikely-file", LG_FILE_WRITE+LG_FILE_CREATE+LG_FILE_TRUNC);
   check_no_error("file_open", h);

   s = file_close(sbc, h);
   check_no_error("file_close", s);

   rgpiod_stop(sbc);
}

