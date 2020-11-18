/*
errors.c
2020-11-18
Public Domain

http://abyz.me.uk/lg/rgpio.html

gcc -Wall -o errors errors.c -lrgpio

./errors
*/

#include <stdio.h>

#include "lgpio.h"
#include "rgpio.h"

static int gFailOnly = 0;

void check(char *func, int exp, int got)
{
   if (exp != got)
      printf("FAIL: %s (expected %d, got %d)\n", func, exp, got);
   else
      if (!gFailOnly) printf("PASS: %s\n", func);
}

void check_no_error(char *func, int got)
{
   if (got < 0)
      printf("FAIL: %s (expected no error, got %d)\n", func, got);
   else
      if (!gFailOnly) printf("PASS: %s (%d)\n", func, got);
}

void check_not_null(char *func, int got, char *name)
{
   if (got < 0)
      printf("FAIL: %s (expected name, got %d)\n", func, got);
   else
      if (!gFailOnly) printf("PASS: %s (%s)\n", func, name);
}

int main(int argc, char *argv[])
{
   int sbc;
   int status;
   int h;
   uint64_t temp64=0x123456789abcdef0;
   uint64_t t64;
   int xGpio[]={99, 88, 77, 66, 55, 44, 33, 22, 11};
   int xVals[]={11, 22, 33, 44, 55, 66, 77, 88, 99};
   uint32_t param[20];
   char buf[1024];
   lgPulse_t pulses[20];
   lgChipInfo_t chipInfo;
   lgLineInfo_t lineInfo;

   if (argc > 1) gFailOnly =1;

   sbc = rgpiod_start(0, 0);

   if (sbc < 0)
   {
      fprintf(stderr, "initialisation failed (sbc, %d).\n", sbc);
      return 1;
   }

   printf("Connected to rgpiod (%d).\n", sbc);

   status = lgu_set_user(sbc, "admin", ".lg_secret");

   status = lgu_set_internal(sbc, 0, 2);

   t64=0;
   status = lgu_get_internal(sbc, 0, &t64);
   check("lgu_get_internal", 3, t64);

   status = lgu_set_internal(sbc, 0, 3);
   check("lgu_set_internal", LG_OKAY, status);

   status = lgu_set_user(sbc, "test1", ".lg_secret");

   status = gpiochip_close(sbc, 9999);
   check("gpiochip_close 1", LG_BAD_HANDLE, status);

   status = gpio_claim_input(sbc, 9999, 8888, 7777);
   check("gpio_claim_input 1", LG_BAD_HANDLE, status);

   status = group_claim_input(sbc, 9999, 0, 5, xGpio);
   check("group_claim_input 1", LG_BAD_HANDLE, status);

   status = gpio_claim_output(sbc, 9999, 8888, 7777, 6666);
   check("gpio_claim_output 1", LG_BAD_HANDLE, status);

   status = group_claim_output(sbc, 9999, 8888, 7, xGpio, xVals);
   check("group_claim_output 1", LG_BAD_HANDLE, status);

   status = gpio_write(sbc, 9999, 8888, 7777);
   check("gpio_write 1", LG_BAD_HANDLE, status);

   status = group_read(sbc, 9999, 4, &temp64);
   check("group_read 1", LG_BAD_HANDLE, status);

   status = group_write(sbc, 9999, 4, temp64, -1);
   check("group_write 1", LG_BAD_HANDLE, status);

   status = gpiochip_open(sbc, 9999);
   check("gpiochip_open 1", LG_CANNOT_OPEN_CHIP, status);

   status = gpio_read(sbc, 9999, 8888);
   check("gpio_read 1", LG_BAD_HANDLE, status);

   status = gpio_free(sbc, 9999, 8888);
   check("gpio_free 1", LG_BAD_HANDLE, status);

   status = group_free(sbc, 9999, 8888);
   check("group_free 1", LG_BAD_HANDLE, status);

   status = tx_pulse(sbc, 9999, 8888, 7777, 6666, 5555, 4444);
   check("tx_pulse 1", LG_BAD_HANDLE, status);

   status = tx_pwm(sbc, 9999, 8888, 7777, 6666, 5555, 4444);
   check("tx_pwm 1", LG_BAD_PWM_DUTY, status);

   status = tx_pwm(sbc, 9999, 8888, 77777, 66, 5555, 4444);
   check("tx_pwm 2", LG_BAD_PWM_FREQ, status);

   status = tx_pwm(sbc, 9999, 8888, 7777, 66, 5555, 4444);
   check("tx_pwm 3", LG_BAD_HANDLE, status);

   status = tx_servo(sbc, 9999, 8888, 7777, 6666, 5555, 4444);
   check("tx_servo 1", LG_BAD_SERVO_FREQ, status);

   status = tx_servo(sbc, 9999, 8888, 7777, 50, 5555, 4444);
   check("tx_servo 2", LG_BAD_SERVO_WIDTH, status);

   status = tx_servo(sbc, 9999, 8888, 1500, 50, 5555, 4444);
   check("tx_servo 3", LG_BAD_HANDLE, status);

   status = tx_room(sbc, 9999, 8888, 7777);
   check("tx_room 1", LG_BAD_TX_TYPE, status);

   status = tx_room(sbc, 9999, 8888, 0);
   check("tx_room 2", LG_BAD_HANDLE, status);

   status = tx_busy(sbc, 9999, 8888, 7777);
   check("tx_busy 1", LG_BAD_TX_TYPE, status);

   status = tx_busy(sbc, 9999, 8888, 0);
   check("tx_busy 2", LG_BAD_HANDLE, status);

   status = gpio_set_debounce_time(sbc, 9999, 8888, 10000000);
   check("gpio_set_debounce_time 1", LG_BAD_DEBOUNCE_MICS, status);

   status = gpio_set_debounce_time(sbc, 9999, 8888, 1000000);
   check("gpio_set_debounce_time 2", LG_BAD_HANDLE, status);

   status = gpio_set_watchdog_time(sbc, 9999, 8888, 1000000000);
   check("gpio_set_watchdog_time 1", LG_BAD_WATCHDOG_MICS, status);

   status = gpio_set_watchdog_time(sbc, 9999, 8888, 1000000);
   check("gpio_set_watchdog_time 2", LG_BAD_HANDLE, status);

   status = gpio_get_mode(sbc, 9999, 8888);
   check("gpio_get_mode 1", LG_BAD_HANDLE, status);

   status = gpio_get_chip_info(sbc, 9999, &chipInfo);
   check("gpio_get_chip_info 1", LG_BAD_HANDLE, status);

   status = gpio_get_line_info(sbc, 9999, 8888, &lineInfo);
   check("gpio_get_line_info 1", LG_BAD_HANDLE, status);

   status = gpio_claim_alert(sbc, 9999, 8888, 7777, 6666, 5555);
   check("gpio_claim_alert 1", LG_BAD_HANDLE, status);

   status = tx_wave(sbc, 9999, 8888, 0, pulses);
   check("tx_wave 1", LG_BAD_HANDLE, status);

   status = file_close(sbc, 9999);
   check("file_close", LG_BAD_HANDLE, status);

   status = file_list(sbc, "TEST/pattern/*", buf, sizeof(buf));
   check("file_list 1", LG_NO_FILE_MATCH, status);

   status = file_list(sbc, "./", buf, sizeof(buf));
   check("file_list 2", LG_NO_FILE_ACCESS, status);

   status = file_open(sbc, "TEST/file", 9999);
   check("file_open 1", LG_BAD_FILE_MODE, status);

   status = file_open(sbc, "TEST/unlikelyFileName", 1);
   check("file_open 2", LG_FILE_OPEN_FAILED, status);

   status = file_open(sbc, "unlikelyFileName", 1);
   check("file_open 3", LG_FILE_OPEN_FAILED, status);

   status = file_read(sbc, 9999, buf, 0);
   check("file_read 1", LG_BAD_FILE_PARAM, status);

   status = file_read(sbc, 9999, buf, sizeof(buf));
   check("file_read 2", LG_BAD_HANDLE, status);

   status = file_seek(sbc, 9999, 8888, 7777);
   check("file_seek 1", LG_BAD_FILE_SEEK, status);

   status = file_seek(sbc, 9999, 8888, 1);
   check("file_seek 2", LG_BAD_HANDLE, status);

   status = file_write(sbc, 9999, buf, 0);
   check("file_write 1", LG_BAD_FILE_PARAM, status);

   status = file_write(sbc, 9999, buf, 5);
   check("file_write 2", LG_BAD_HANDLE, status);

   status = i2c_close(sbc, 9999);
   check("i2c_close", LG_BAD_HANDLE, status);

   status = i2c_open(sbc, 1, 8888, 7777);
   check("i2c_open 1", LG_BAD_I2C_ADDR, status);

   status = i2c_open(sbc, 1, 0x40, 7777);
   check("i2c_open 2", LG_BAD_I2C_FLAGS, status);

   status = i2c_open(sbc, 999, 0x40, 0);
   check("i2c_open 3", LG_BAD_I2C_BUS, status);

   status = i2c_process_call(sbc, 9999, 8888, 7777);
   check("i2c_process_call 1", LG_BAD_I2C_PARAM, status);

   status = i2c_process_call(sbc, 9999, 5, 77777);
   check("i2c_process_call 2", LG_BAD_I2C_PARAM, status);

   status = i2c_process_call(sbc, 9999, 0xff, 0xffff);
   check("i2c_process_call 3", LG_BAD_HANDLE, status);

   status = i2c_block_process_call(sbc, 9999, 256, buf, 10);
   check("i2c_block_process_call 1", LG_BAD_I2C_PARAM, status);

   status = i2c_block_process_call(sbc, 9999, 23, buf, 0);
   check("i2c_block_process_call 2", LG_BAD_I2C_PARAM, status);

   status = i2c_block_process_call(sbc, 9999, 23, buf, 10);
   check("i2c_block_process_call 3", LG_BAD_HANDLE, status);

   status = i2c_read_byte_data(sbc, 9999, 8888);
   check("i2c_read_byte_data 1", LG_BAD_I2C_PARAM, status);

   status = i2c_read_byte_data(sbc, 9999, 250);
   check("i2c_read_byte_data 2", LG_BAD_HANDLE, status);

   status = i2c_read_device(sbc, 9999, buf, 0);
   check("i2c_read_device 1", LG_BAD_I2C_PARAM, status);

   status = i2c_read_device(sbc, 9999, buf, 250);
   check("i2c_read_device 2", LG_BAD_HANDLE, status);

   status = i2c_read_i2c_block_data(sbc, 9999, 8888, buf, 20);
   check("i2c_read_i2c_block_data 1", LG_BAD_I2C_PARAM, status);

   status = i2c_read_i2c_block_data(sbc, 9999, 250, buf, 33);
   check("i2c_read_i2c_block_data 2", LG_BAD_I2C_PARAM, status);

   status = i2c_read_i2c_block_data(sbc, 9999, 250, buf, 30);
   check("i2c_read_i2c_block_data 3", LG_BAD_HANDLE, status);

   status = i2c_read_block_data(sbc, 9999, 8888, buf);
   check("i2c_read_block_data 1", LG_BAD_I2C_PARAM, status);

   status = i2c_read_block_data(sbc, 9999, 25, buf);
   check("i2c_read_block_data 2", LG_BAD_HANDLE, status);

   status = i2c_read_byte(sbc, 9999);
   check("i2c_read_byte 1", LG_BAD_HANDLE, status);

   status = i2c_read_word_data(sbc, 9999, 8888);
   check("i2c_read_word_data 1", LG_BAD_I2C_PARAM, status);

   status = i2c_read_word_data(sbc, 9999, 88);
   check("i2c_read_word_data 2", LG_BAD_HANDLE, status);

   status = i2c_write_byte_data(sbc, 9999, 8888, 7777);
   check("i2c_write_byte_data 1", LG_BAD_I2C_PARAM, status);

   status = i2c_write_byte_data(sbc, 9999, 8, 777);
   check("i2c_write_byte_data 2", LG_BAD_I2C_PARAM, status);

   status = i2c_write_byte_data(sbc, 9999, 8, 77);
   check("i2c_write_byte_data 3", LG_BAD_HANDLE, status);

   status = i2c_write_device(sbc, 9999, buf, 0);
   check("i2c_write_device 1", LG_BAD_I2C_PARAM, status);

   status = i2c_write_device(sbc, 9999, buf, 20);
   check("i2c_write_device 2", LG_BAD_HANDLE, status);

   status = i2c_write_i2c_block_data(sbc, 9999, 8888, buf, 20);
   check("i2c_write_i2c_block_data 1", LG_BAD_I2C_PARAM, status);

   status = i2c_write_i2c_block_data(sbc, 9999, 88, buf, 0);
   check("i2c_write_i2c_block_data 2", LG_BAD_I2C_PARAM, status);

   status = i2c_write_i2c_block_data(sbc, 9999, 88, buf, 10);
   check("i2c_write_i2c_block_data 3", LG_BAD_HANDLE, status);

   status = i2c_write_block_data(sbc, 9999, 256, buf, 10);
   check("i2c_write_block_data 1", LG_BAD_I2C_PARAM, status);

   status = i2c_write_block_data(sbc, 9999, 55, buf, 0);
   check("i2c_write_block_data 2", LG_BAD_I2C_PARAM, status);

   status = i2c_write_block_data(sbc, 9999, 55, buf, 10);
   check("i2c_write_block_data 3", LG_BAD_HANDLE, status);

   status = i2c_write_quick(sbc, 9999, 2);
   check("i2c_write_quick 1", LG_BAD_I2C_PARAM, status);

   status = i2c_write_quick(sbc, 9999, 1);
   check("i2c_write_quick 2", LG_BAD_HANDLE, status);

   status = i2c_write_byte(sbc, 9999, 8888);
   check("i2c_write_byte 1", LG_BAD_I2C_PARAM, status);

   status = i2c_write_byte(sbc, 9999, 255);
   check("i2c_write_byte 2", LG_BAD_HANDLE, status);

   status = i2c_write_word_data(sbc, 9999, 8888, 7777);
   check("i2c_write_word_data 1", LG_BAD_I2C_PARAM, status);

   status = i2c_write_word_data(sbc, 9999, 88, 77777);
   check("i2c_write_word_data 2", LG_BAD_I2C_PARAM, status);

   status = i2c_write_word_data(sbc, 9999, 88, 7777);
   check("i2c_write_word_data 3", LG_BAD_HANDLE, status);

   status = i2c_zip(sbc, 9999, buf, 0, buf, 10);
   check("i2c_zip 1", LG_BAD_POINTER, status);

   status = i2c_zip(sbc, 9999, buf, 10, buf, 10);
   check("i2c_zip 2", LG_BAD_HANDLE, status);

   status = lgu_get_sbc_name(sbc, buf, sizeof(buf));
   check_not_null("lgu_get_sbc_name", status, buf);

   status = lgu_rgpio_version();
   check_no_error("lgu_rgpio_version", status);

   lgu_set_user(sbc, "test2", ".lg_secret");

   h = notify_open(sbc);
   check_no_error("notify_open 1", h);

   status = notify_resume(sbc, h);
   check("notify_resume 1", LG_OKAY, status);

   status = notify_resume(sbc, 9999);
   check("notify_resume 2", LG_BAD_HANDLE, status);

   status = notify_pause(sbc, h);
   check("notify_pause 1", LG_OKAY, status);

   status = notify_pause(sbc, 9999);
   check("notify_pause 2", LG_BAD_HANDLE, status);

   status = notify_close(sbc, h);
   check("notify_close 1", LG_OKAY, status);

   status = notify_close(sbc, 9999);
   check("notify_close 2", LG_BAD_HANDLE, status);

   lgu_set_user(sbc, "test3", ".lg_secret");

   h = script_store(sbc, "tag 0 dcr p1 mils 100 jmp 0");
   check_no_error("script_store 1", h);

   while (script_status(sbc, h, param) == LG_SCRIPT_INITING) ;

   status = script_status(sbc, h, param);
   check("script_status 1", LG_SCRIPT_READY, status);

   status = script_status(sbc, 9999, param);
   check("script_status 2", LG_BAD_HANDLE, status);

   status = script_update(sbc, h, 4, param);
   check("script_update 1", LG_OKAY, status);

   status = script_update(sbc, 9999, 4, param);
   check("script_update 2", LG_BAD_HANDLE, status);

   status = script_run(sbc, h, 6, param);
   check("script_run 1", LG_OKAY, status);

   status = script_run(sbc, 8888, 6, param);
   check("script_run 2", LG_BAD_HANDLE, status);

   status = script_stop(sbc, h);
   check("script_stop 1", LG_OKAY, status);

   status = script_stop(sbc, 9999);
   check("script_stop 2", LG_BAD_HANDLE, status);

   status = script_delete(sbc, h);
   check("script_delete 1", LG_OKAY, status);

   status = script_delete(sbc, 9999);
   check("script_delete 2", LG_BAD_HANDLE, status);

   status = lgu_set_user(sbc, "test3", ".lg_secret");

   status = serial_open(sbc, "raw", 9600, 0);
   check("serial_open 1", LG_SERIAL_OPEN_FAILED, status);

   status = lgu_set_user(sbc, "test1", ".lg_secret");

   status = serial_open(sbc, "ttyS0", 8888, 7777);
   check("serial_open 2", LG_BAD_SERIAL_SPEED, status);

   status = serial_open(sbc, "ttyS0", 9600, 7777);
   check("serial_open 3", LG_BAD_SERIAL_FLAGS, status);

   status = serial_open(sbc, "ttyUnlikelyFileName", 9600, 0);
   check("serial_open 4", LG_SERIAL_OPEN_FAILED, status);

   status = serial_close(sbc, 9999);
   check("serial_close 1", LG_BAD_HANDLE, status);

   status = serial_data_available(sbc, 9999);
   check("serial_data_available 1", LG_BAD_HANDLE, status);

   status = serial_read(sbc, 9999, buf, 0);
   check("serial_read 1", LG_BAD_SERIAL_PARAM, status);

   status = serial_read(sbc, 9999, buf, 8888);
   check("serial_read 2", LG_BAD_HANDLE, status);

   status = serial_read_byte(sbc, 9999);
   check("serial_read_byte 1", LG_BAD_HANDLE, status);

   status = serial_write(sbc, 9999, buf, 0);
   check("serial_write 1", LG_BAD_SERIAL_PARAM, status);

   status = serial_write(sbc, 9999, buf, 8);
   check("serial_write 2", LG_BAD_HANDLE, status);

   status = serial_write_byte(sbc, 9999, 256);
   check("serial_write_byte 2", LG_BAD_SERIAL_PARAM, status);

   status = serial_write_byte(sbc, 9999, 88);
   check("serial_write_byte 2", LG_BAD_HANDLE, status);

   status = lgu_set_user(sbc, "test3", ".lg_secret");

   status = shell(sbc, "echo", "me");
   check("shell 1", 32512, status);

   status = lgu_set_user(sbc, "test1", ".lg_secret");

   status = spi_close(sbc, 9999);
   check("spi_close 1", LG_BAD_HANDLE, status);

   status = spi_open(sbc, 2, 1, 7777, 6666);
   check("spi_open 1", LG_SPI_OPEN_FAILED, status);

   status = spi_read(sbc, 9999, buf, 0);
   check("spi_read 1", LG_BAD_SPI_COUNT, status);

   status = spi_read(sbc, 9999, buf, 8888);
   check("spi_read 2", LG_BAD_HANDLE, status);

   status = spi_write(sbc, 9999, buf, 0);
   check("spi_write 1", LG_BAD_SPI_COUNT, status);

   status = spi_write(sbc, 9999, buf, 8);
   check("spi_write 2", LG_BAD_HANDLE, status);

   status = spi_xfer(sbc, 9999, buf, buf, 0);
   check("spi_xfer 1", LG_BAD_SPI_COUNT, status);

   status = spi_xfer(sbc, 9999, buf, buf, 10);
   check("spi_xfer 2", LG_BAD_HANDLE, status);
 
   status = lgu_set_share_id(sbc, 9999, 8888);
   check("lgu_set_share_id 1", LG_BAD_HANDLE, status);

   status = lgu_use_share_id(sbc, 0);
   check("lgu_use_share_id 1", LG_OKAY, status);

   rgpiod_stop(sbc);

   return 0;
}

