#!/usr/bin/env python
"""
files.py
2020-11-18
Public Domain

http://abyz.me.uk/lg/py_rgpio.html

./files.py
"""

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

def check_error(func, got):
   if got < 0:
      print("PASS: {} ({})".format(func, got))
   else:
      print("FAIL: {} (expected error, got {})".format(func, got))

def check_not_null(func, got):
   if got == "":
      print("FAIL: {} (expected name, got {})".format(func, got))
   else:
      print("PASS: {} ({})".format(func, got))

sbc = rgpio.sbc()
if not sbc.connected:
   exit()

sbc.set_user("test1")

# open file for write, create if it doesn't exist

h = sbc.file_open(
   "test.file", rgpio.FILE_WRITE+rgpio.FILE_CREATE+rgpio.FILE_TRUNC)
check_no_error("file_open", h)

# write some text

s = sbc.file_write(h, "Now is the winter of our discontent\n")
check_no_error("file_write", s)

s = sbc.file_write(h, "Made glorious summer by this son of York\n")
check_no_error("file_write", s)

s = sbc.file_close(h)
check_no_error("file_close", s)

# open for read

h = sbc.file_open("test.file", rgpio.FILE_READ)
check_no_error("file_open", h)

(s, data) = sbc.file_read(h, 100) # read up to 100 characters from file
check("file_read", 77, s)

s = sbc.file_seek(h, 25, rgpio.FROM_START)
check_no_error("file_seek", s)

(s, data) = sbc.file_read(h, 100) # read up to 100 characters from file
check("file_read", 52, s)

s = sbc.file_seek(h, -25, rgpio.FROM_END)
check_no_error("file_seek", s)

(s, data) = sbc.file_read(h, 100) # read up to 100 charactrs from file
check("file_read", 25, s)

s = sbc.file_seek(h, -50, rgpio.FROM_END)
check_no_error("file_seek", s)

(s, data) = sbc.file_read(h, 5) # read up to 5 charactrs from file
check("file_read", 5, s)

sbc.file_seek(h, -20, rgpio.FROM_CURRENT)
check_no_error("file_seek", s)

(s, data) = sbc.file_read(h, 100) # read up to 100 charactrs from file
check("file_read", 65, s)

s = sbc.file_close(h)
check_no_error("file_close", s)

(s, data) = sbc.file_list("file*")
check("file_list", 32, s)

rgpio.exceptions = False

for pat in "/", "/tmp", "*", "TEST":
   (s, data) = sbc.file_list(pat)
   check("file_list (" + pat + ")", rgpio.NO_FILE_ACCESS, s)

for pat in "/tmp/unlikely_file_name", "file34":
   (s, data) = sbc.file_list(pat)
   check("file_list (" + pat + ")", rgpio.NO_FILE_MATCH, s)

for pat in "/tmp/*", "file.*":
   (s, data) = sbc.file_list(pat)
   check_no_error("file_list (" + pat + ")", s)

# create a file

h = sbc.file_open(
   "/tmp/unlikely_file", rgpio.FILE_WRITE+rgpio.FILE_CREATE+rgpio.FILE_TRUNC)
check_no_error("file_open", h)

s = sbc.file_close(h)
check_no_error("file_close", s)

expected = [
   rgpio.NO_FILE_ACCESS, 1,                 1, 1,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS, 1, 1,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS, 1, 1,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS, 1, 1,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS, 1, 1,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS, 1, 1,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS, 1, 1,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS, 1, 1]


fails = 0

for mode in range(0, 32):
   h = sbc.file_open("/tmp/unlikely_file", mode)
   if h < 0:
      if h != expected[mode]:
         fails += 1
         print("A: for {} expected {}, got {}".format(mode, expected[mode], h))
   else:
      if expected[mode] < 0:
         fails += 1
         print("A: for {} expected ok, got {}".format(mode, h))
      sbc.file_close(h)
check("A: file_open", 0, fails)

expected = [
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS,
   rgpio.NO_FILE_ACCESS, rgpio.NO_FILE_ACCESS]

fails = 0

for mode in range(0, 32):
   h = sbc.file_open("unlikely_file", mode)
   if h < 0:
      if h != expected[mode]:
         fails += 1
         print("B: for {} expected {}, got {}".format(mode, expected[mode], h))
   else:
      if expected[mode] < 0:
         fails += 1
         print("B: for {} expected ok, got {}".format(mode, h))
      sbc.file_close(h)
check("B: file_open", 0, fails)

fails = 0

for pat in "./zzz", "././yyy", "\.\./xxx", "../yyy", "./yyy":
   h = sbc.file_open(pat, rgpio.FILE_WRITE+rgpio.FILE_CREATE+rgpio.FILE_TRUNC)
   if h != rgpio.NO_FILE_ACCESS:
      fails += 1
      print("FAIL: for {} expected no access".format(root+pat))
      sbc.file_close(h)
check("file_open", 0, fails)

rgpio.exceptions = True

sbc.stop()

