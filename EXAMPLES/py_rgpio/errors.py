#!/usr/bin/env python

import time
import rgpio

def check(func, exp, got):
   if exp != got:
      print("FAIL: {} (expected {}, got {})".format(func, exp, got))
   else:
      print("PASS: {}".format(func))

def check_no_error(func, got):
   if got < 0:
      print("FAIL: {} (expected no error, got {})".format(func, got))
   else:
      print("PASS: {} ({})".format(func, got))

def check_not_null(func, got):
   if got == "":
      print("FAIL: {} (expected name, got {})".format(func, got))
   else:
      print("PASS: {} ({})".format(func, got))

pulses=[]
pulses.append(rgpio.pulse(0xff, 0xff, 1000))
pulses.append(rgpio.pulse(0x00, 0x0f, 2000))
pulses.append(rgpio.pulse(0xff, 0xf0, 3000))
pulses.append(rgpio.pulse(0x00, 0xff, 4000))
pulses.append(rgpio.pulse(0xff, 0x55, 5000))
pulses.append(rgpio.pulse(0x00, 0xAA, 6000))

sbc = rgpio.sbc()

if not sbc.connected:
   exit()

rgpio.exceptions = False

status = sbc.set_user("admin", ".lg_secret")

status = sbc.set_internal(0, 2)

status, value = sbc.get_internal(0)
check("get_internal", 3, value)

status = sbc.set_internal(0, 3)
check("set_internal", rgpio.OKAY, status)

status = sbc.set_user("test1", ".lg_secret")

status = sbc.file_close(9999)
check("file_close", rgpio.BAD_HANDLE, status)

status, dummy = sbc.file_list("TEST/pattern/*")
check("file_list 1", rgpio.NO_FILE_MATCH, status)

status, dummy = sbc.file_list("..")
check("file_list 2", rgpio.NO_FILE_ACCESS, status)

status = sbc.file_open("TEST/file", 9999)
check("file_open 1", rgpio.BAD_FILE_MODE, status)

status = sbc.file_open("TEST/file", 1)
check("file_open 2", rgpio.FILE_OPEN_FAILED, status)

status = sbc.file_open("missing_file", 1)
check("file_open 3", rgpio.FILE_OPEN_FAILED, status)

status, dummy = sbc.file_read(9999, 0)
check("file_read 1", rgpio.BAD_FILE_PARAM, status)

status, dummy = sbc.file_read(9999, 8888)
check("file_read 2", rgpio.BAD_HANDLE, status)

status = sbc.file_seek(9999, 8888, 7777)
check("file_seek 1", rgpio.BAD_FILE_SEEK, status)

status = sbc.file_seek(9999, 8888, 1)
check("file_seek 2", rgpio.BAD_HANDLE, status)

status = sbc.file_write(9999, [])
check("file_write 1", rgpio.BAD_FILE_PARAM, status)

status = sbc.file_write(9999, "Hello")
check("file_write 2", rgpio.BAD_HANDLE, status)

status = sbc.i2c_close(9999)
check("i2c_close", rgpio.BAD_HANDLE, status)

status = sbc.i2c_open(1, 8888, 7777)
check("i2c_open 1", rgpio.BAD_I2C_ADDR, status)

status = sbc.i2c_open(1, 0x40, 7777)
check("i2c_open 2", rgpio.BAD_I2C_FLAGS, status)

status = sbc.i2c_open(999, 0x40, 0)
check("i2c_open 3", rgpio.BAD_I2C_BUS, status)

status = sbc.i2c_process_call(9999, 8888, 7777)
check("i2c_process_call 1", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_process_call(9999, 5, 77777)
check("i2c_process_call 2", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_process_call(9999, 0xff, 0xffff)
check("i2c_process_call 3", rgpio.BAD_HANDLE, status)

status, dummy = sbc.i2c_block_process_call(9999, 256, [77, 66, 55, 44, 33, 22, 11])
check("i2c_block_process_call 1", rgpio.BAD_I2C_PARAM, status)

status, dummy = sbc.i2c_block_process_call(9999, 23, [])
check("i2c_block_process_call 2", rgpio.BAD_I2C_PARAM, status)

status, dummy = sbc.i2c_block_process_call(9999, 23, [77, 66, 55, 44, 33, 22, 11])
check("i2c_block_process_call 3", rgpio.BAD_HANDLE, status)

status = sbc.i2c_read_byte_data(9999, 8888)
check("i2c_read_byte_data 1", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_read_byte_data(9999, 250)
check("i2c_read_byte_data 2", rgpio.BAD_HANDLE, status)

status, dummy = sbc.i2c_read_device(9999, 0)
check("i2c_read_device 1", rgpio.BAD_I2C_PARAM, status)

status, dummy = sbc.i2c_read_device(9999, 250)
check("i2c_read_device 2", rgpio.BAD_HANDLE, status)

status, dummy = sbc.i2c_read_i2c_block_data(9999, 8888, 20)
check("i2c_read_i2c_block_data 1", rgpio.BAD_I2C_PARAM, status)

status, dummy = sbc.i2c_read_i2c_block_data(9999, 250, 33)
check("i2c_read_i2c_block_data 2", rgpio.BAD_I2C_PARAM, status)

status, dummy = sbc.i2c_read_i2c_block_data(9999, 250, 30)
check("i2c_read_i2c_block_data 3", rgpio.BAD_HANDLE, status)

status, dummy = sbc.i2c_read_block_data(9999, 8888)
check("i2c_read_block_data 1", rgpio.BAD_I2C_PARAM, status)

status, dummy = sbc.i2c_read_block_data(9999, 25)
check("i2c_read_block_data 2", rgpio.BAD_HANDLE, status)

status = sbc.i2c_read_byte(9999)
check("i2c_read_byte 1", rgpio.BAD_HANDLE, status)

status = sbc.i2c_read_word_data(9999, 8888)
check("i2c_read_word_data 1", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_read_word_data(9999, 88)
check("i2c_read_word_data 2", rgpio.BAD_HANDLE, status)

status = sbc.i2c_write_byte_data(9999, 8888, 7777)
check("i2c_write_byte_data 1", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_write_byte_data(9999, 8, 777)
check("i2c_write_byte_data 2", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_write_byte_data(9999, 8, 77)
check("i2c_write_byte_data 3", rgpio.BAD_HANDLE, status)

status = sbc.i2c_write_device(9999, [])
check("i2c_write_device 1", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_write_device(9999, [88, 77, 66, 55, 44, 33, 22, 11])
check("i2c_write_device 2", rgpio.BAD_HANDLE, status)

status = sbc.i2c_write_i2c_block_data(9999, 8888, [77, 66, 55, 44, 33, 22, 11])
check("i2c_write_i2c_block_data 1", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_write_i2c_block_data(9999, 88, [])
check("i2c_write_i2c_block_data 2", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_write_i2c_block_data(9999, 88, [77, 66, 55, 44, 33, 22, 11])
check("i2c_write_i2c_block_data 3", rgpio.BAD_HANDLE, status)

status = sbc.i2c_write_block_data(9999, 256, [77, 66, 55, 44, 33, 22, 11])
check("i2c_write_block_data 1", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_write_block_data(9999, 55, [])
check("i2c_write_block_data 2", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_write_block_data(9999, 55, [77, 66, 55, 44, 33, 22, 11])
check("i2c_write_block_data 3", rgpio.BAD_HANDLE, status)

status = sbc.i2c_write_quick(9999, 2)
check("i2c_write_quick 1", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_write_quick(9999, 1)
check("i2c_write_quick 2", rgpio.BAD_HANDLE, status)

status = sbc.i2c_write_byte(9999, 8888)
check("i2c_write_byte 1", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_write_byte(9999, 255)
check("i2c_write_byte 2", rgpio.BAD_HANDLE, status)

status = sbc.i2c_write_word_data(9999, 8888, 7777)
check("i2c_write_word_data 1", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_write_word_data(9999, 88, 77777)
check("i2c_write_word_data 2", rgpio.BAD_I2C_PARAM, status)

status = sbc.i2c_write_word_data(9999, 88, 7777)
check("i2c_write_word_data 3", rgpio.BAD_HANDLE, status)

status, dummy = sbc.i2c_zip(9999, [])
check("i2c_zip 1", rgpio.BAD_POINTER, status)

status, dummy = sbc.i2c_zip(9999, [88, 77, 66, 55, 44, 33, 22, 11])
check("i2c_zip 2", rgpio.BAD_HANDLE, status)

server = sbc.get_sbc_name()
check_not_null("get_sbc_name", server)

status = rgpio.get_module_version()
check_not_null("get_module_version", status)

sbc.set_user("test2", ".lg_secret")

h = sbc.notify_open()
check_no_error("notify_open 1", h)

status = sbc.notify_resume(h)
check("notify_resume 1", rgpio.OKAY, status)

status = sbc.notify_resume(9999)
check("notify_resume 2", rgpio.BAD_HANDLE, status)

status = sbc.notify_pause(h)
check("notify_pause 1", rgpio.OKAY, status)

status = sbc.notify_pause(9999)
check("notify_pause 2", rgpio.BAD_HANDLE, status)

status = sbc.notify_close(h)
check("notify_close 1", rgpio.OKAY, status)

status = sbc.notify_close(9999)
check("notify_close 2", rgpio.BAD_HANDLE, status)

sbc.set_user("test3", ".lg_secret")

h = sbc.script_store("tag 0 dcr p1 mils 100 jmp 0")
check_no_error("script store 1", h)

time.sleep(0.2)

status, dummy = sbc.script_status(h)
check("script_status 1", rgpio.SCRIPT_READY, status)

status, dummy = sbc.script_status(9999)
check("script_status 2", rgpio.BAD_HANDLE, status)

status = sbc.script_update(h, [5555, 4444, 3333, 2222, 1111])
check("script_update 1", rgpio.OKAY, status)

status = sbc.script_update(9999, [5555, 4444, 3333, 2222, 1111])
check("script_update 2", rgpio.BAD_HANDLE, status)

status = sbc.script_run(h, [8888, 7777, 6666, 5555])
check("script_run 1", rgpio.OKAY, status)

status = sbc.script_run(8888, [8888, 7777, 6666, 5555])
check("script_run 2", rgpio.BAD_HANDLE, status)

status = sbc.script_stop(h)
check("script_stop 1", rgpio.OKAY, status)

status = sbc.script_stop(9999)
check("script_stop 2", rgpio.BAD_HANDLE, status)

status = sbc.script_delete(h)
check("script_delete 1", rgpio.OKAY, status)

status = sbc.script_delete(9999)
check("script_delete 2", rgpio.BAD_HANDLE, status)

status = sbc.set_user("test3", ".lg_secret")

status = sbc.serial_open("raw", 9600, 0)
check("serial_open 1", rgpio.SERIAL_OPEN_FAILED, status)

status = sbc.set_user("test1", ".lg_secret")

status = sbc.serial_open("ttyS0", 8888, 7777)
check("serial_open 2", rgpio.BAD_SERIAL_SPEED, status)

status = sbc.serial_open("ttyS0", 9600, 7777)
check("serial_open 3", rgpio.BAD_SERIAL_FLAGS, status)

status = sbc.serial_open("ttyUnlikelyFileName", 9600, 0)
check("serial_open 4", rgpio.SERIAL_OPEN_FAILED, status)

status = sbc.serial_close(9999)
check("serial_close 1", rgpio.BAD_HANDLE, status)

status = sbc.serial_data_available(9999)
check("serial_data_available 1", rgpio.BAD_HANDLE, status)

status, dummy = sbc.serial_read(9999, 0)
check("serial_read 1", rgpio.BAD_SERIAL_PARAM, status)

status, dummy = sbc.serial_read(9999, 8888)
check("serial_read 2", rgpio.BAD_HANDLE, status)

status = sbc.serial_read_byte(9999)
check("serial_read_byte 1", rgpio.BAD_HANDLE, status)

status = sbc.serial_write(9999, [])
check("serial_write 1", rgpio.BAD_SERIAL_PARAM, status)

status = sbc.serial_write(9999, [88, 77, 66, 55, 44, 33, 22, 11])
check("serial_write 2", rgpio.BAD_HANDLE, status)

status = sbc.serial_write_byte(9999, 256)
check("serial_write_byte 2", rgpio.BAD_SERIAL_PARAM, status)

status = sbc.serial_write_byte(9999, 88)
check("serial_write_byte 2", rgpio.BAD_HANDLE, status)

status = sbc.set_user("test3", ".lg_secret")

status = sbc.shell("echo", "me")
check("shell 1", 32512, status)

status = sbc.set_user("test1", ".lg_secret")

status = sbc.spi_close(9999)
check("spi_close 1", rgpio.BAD_HANDLE, status)

status = sbc.spi_open(2, 1, 7777, 6666)
check("spi_open 1", rgpio.SPI_OPEN_FAILED, status)

status, dummy = sbc.spi_read(9999, 0)
check("spi_read 1", rgpio.BAD_SPI_COUNT, status)

status, dummy = sbc.spi_read(9999, 8888)
check("spi_read 2", rgpio.BAD_HANDLE, status)

status = sbc.spi_write(9999, [])
check("spi_write 1", rgpio.BAD_SPI_COUNT, status)

status = sbc.spi_write(9999, [88, 77, 66, 55, 44, 33, 22, 11])
check("spi_write 2", rgpio.BAD_HANDLE, status)

status, dummy = sbc.spi_xfer(9999, [])
check("spi_xfer 1", rgpio.BAD_SPI_COUNT, status)

status, dummy = sbc.spi_xfer(9999, [88, 77, 66, 55, 44, 33, 22, 11])
check("spi_xfer 2", rgpio.BAD_HANDLE, status)
 
status = sbc.gpiochip_close(9999)
check("gpiochip_close 1", rgpio.BAD_HANDLE, status)

status, dummy = sbc.group_read(9999, 8888)
check("group_read 1", rgpio.BAD_HANDLE, status)

status = sbc.group_write(9999, 8888, 7777)
check("group_write 1", rgpio.BAD_HANDLE, status)

status = sbc.gpiochip_open(9999)
check("gpiochip_open 1", rgpio.CANNOT_OPEN_CHIP, status)

status, lines, name, label = sbc.gpio_get_chip_info(9999)
check("gpio_get_chip_info 1", rgpio.BAD_HANDLE, status)

status, offset, flags, name, user = sbc.gpio_get_line_info(9999, 8888)
check("gpio_get_line_info 1", rgpio.BAD_HANDLE, status)

status = sbc.gpio_get_mode(9999, 8888)
check("gpio_get_mode 1", rgpio.BAD_HANDLE, status)

status = sbc.gpio_read(9999, 8888)
check("gpio_read 1", rgpio.BAD_HANDLE, status)

status = sbc.gpio_free(9999, 8888)
check("gpio_free 1", rgpio.BAD_HANDLE, status)

status = sbc.group_free(9999, 8888)
check("group_free 1", rgpio.BAD_HANDLE, status)

status = sbc.tx_pulse(9999, 8888,7777, 6666, 5555, 4444)
check("tx_pulse 1", rgpio.BAD_HANDLE, status)

status = sbc.tx_pwm(9999, 8888, 7777, 6666, 5555, 4444)
check("tx_pwm 1", rgpio.BAD_PWM_DUTY, status)

status = sbc.tx_pwm(9999, 8888, 77777, 50, 5555, 4444)
check("tx_pwm 2", rgpio.BAD_PWM_FREQ, status)

status = sbc.tx_pwm(9999, 8888, 5000, 50, 5555, 4444)
check("tx_pwm 3", rgpio.BAD_HANDLE, status)

status = sbc.tx_servo(9999, 8888, 7777, 6666, 5555, 4444)
check("tx_servo 1", rgpio.BAD_SERVO_FREQ, status)

status = sbc.tx_servo(9999, 8888, 7777, 50, 5555, 4444)
check("tx_servo 2", rgpio.BAD_SERVO_WIDTH, status)

status = sbc.tx_servo(9999, 8888, 1500, 50, 5555, 4444)
check("tx_servo 2", rgpio.BAD_HANDLE, status)

status = sbc.tx_wave(9999, 8888, pulses)
check("tx_wave 1", rgpio.BAD_HANDLE, status)

status = sbc.tx_busy(9999, 8888, 7777)
check("tx_busy 1", rgpio.BAD_TX_TYPE, status)

status = sbc.tx_busy(9999, 8888, 0)
check("tx_busy 2", rgpio.BAD_HANDLE, status)

status = sbc.tx_room(9999, 8888, 7777)
check("tx_room 1", rgpio.BAD_TX_TYPE, status)

status = sbc.tx_room(9999, 8888, 0)
check("tx_room 2", rgpio.BAD_HANDLE, status)

status = sbc.gpio_set_debounce_micros(9999, 8888, 6000000)
check("gpio_set_debounce_micros 1", rgpio.BAD_DEBOUNCE_MICS, status)

status = sbc.gpio_set_debounce_micros(9999, 8888, 600)
check("gpio_set_debounce_micros 2", rgpio.BAD_HANDLE, status)

status = sbc.gpio_set_watchdog_micros(9999, 8888, 400000000)
check("gpio_set_watchdog_micros 1", rgpio.BAD_WATCHDOG_MICS, status)

status = sbc.gpio_set_watchdog_micros(9999, 8888, 4000)
check("gpio_set_watchdog_micros 2", rgpio.BAD_HANDLE, status)

status = sbc.gpio_claim_alert(9999, 8888, 7777, 6666, 5555)
check("gpio_claim_alert 1", rgpio.BAD_HANDLE, status)

status = sbc.gpio_claim_input(9999, 8888)
check("gpio_claim_input 1", rgpio.BAD_HANDLE, status)

status = sbc.group_claim_input(9999, [8888, 7777, 6666])
check("group_claim_input 1", rgpio.BAD_HANDLE, status)

status = sbc.gpio_claim_output(9999, 8888, 7777)
check("gpio_claim_output 1", rgpio.BAD_HANDLE, status)

status = sbc.group_claim_output(9999, [8888, 7777, 6666])
check("group_claim_output 1", rgpio.BAD_HANDLE, status)

status = sbc.gpio_write(9999, 8888, 7777)
check("gpio_write 1", rgpio.BAD_HANDLE, status)

status = sbc.set_share_id(9999, 8888)
check("set_share_id 1", rgpio.BAD_HANDLE, status)

status = sbc.use_share_id(9999)
check("use_share_id 1", rgpio.OKAY, status)

err = rgpio.error_text(0)
check("error_text 1", "No error", err)

err = rgpio.error_text(-1)
check("error_text 2", "initialisation failed", err)

err = rgpio.error_text(1)
check("error_text 3", "unknown error", err)

sbc.stop()

