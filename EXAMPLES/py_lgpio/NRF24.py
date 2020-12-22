#!/usr/bin/env python
"""
NRF24.py
2020-12-21
Public Domain

http://abyz.me.uk/lg/py_lgpio.html

./NRF24.py   # RX
./NRF24.py x # TX
"""

class NRF24:
   """
   Note that RX and TX addresses must match

   Note that communication channels must match:

   Note that payload size must match:

   The following table describes how to configure the operational
   modes.

   +----------+--------+---------+--------+-----------------------------+
   |Mode      | PWR_UP | PRIM_RX | CE pin | FIFO state                  |
   +----------+--------+---------+--------+-----------------------------+
   |RX mode   |  1     |  1      |  1     | ---                         |
   +----------+--------+---------+--------+-----------------------------+
   |TX mode   |  1     |  0      |  1     | Data in TX FIFOs. Will empty|
   |          |        |         |        | all levels in TX FIFOs      |
   +----------+--------+---------+--------+-----------------------------+
   |TX mode   |  1     |  0      |  >10us | Data in TX FIFOs. Will empty|
   |          |        |         |  pulse | one level in TX FIFOs       |
   +----------+--------+---------+--------+-----------------------------+
   |Standby-II|  1     |  0      |  1     | TX FIFO empty               |
   +----------+--------+---------+--------+-----------------------------+
   |Standby-I |  1     |  ---    |  0     | No ongoing transmission     |
   +----------+--------+---------+--------+-----------------------------+
   |Power Down|  0     |  ---    |  ---   | ---                         |
   +----------+--------+---------+--------+-----------------------------+
   """

   SPI_MAIN_CE0 = 0
   SPI_MAIN_CE1 = 1
   SPI_AUX_CE0  = 2
   SPI_AUX_CE1  = 3
   SPI_AUX_CE2  = 4

   TX = 0
   RX = 1

   ACK_PAYLOAD = -1
   DYNAMIC_PAYLOAD = 0
   MIN_PAYLOAD = 1
   MAX_PAYLOAD = 32

   def _tobuf(self, x):
      if isinstance(x, (str)):
         return list(map(ord, x))
      elif isinstance(x, (list, tuple)):
         return bytearray(x)
      else:
         return x

   def _NRFXfer(self, data):

      b, d = self.sbc.spi_xfer(self.spih, data)

      return d

   def _NRFCommand(self, arg):

      if type(arg) is not list:
         arg = [arg]

      return self._NRFXfer(arg)

   def _NRFReadReg(self, reg, count):

      return self._NRFXfer([reg] + [0]*count)[1:]

   def _NRFWriteReg(self, reg, arg):
      """
      Write arg (which may be one or more bytes) to reg.

      This function is only permitted in a powerdown or
      standby mode.
      """
      if type(arg) is not list:
         arg = [arg]

      self._NRFXfer([self.W_REGISTER | reg] + arg)

   def _configurePayload(self):
      if self.payload >= self.MIN_PAYLOAD: # fixed payload
         self._NRFWriteReg(self.RX_PW_P0, self.payload)
         self._NRFWriteReg(self.RX_PW_P1, self.payload)
         self._NRFWriteReg(self.DYNPD, 0)
         self._NRFWriteReg(self.FEATURE, 0)
      else: # dynamic payload
         self._NRFWriteReg(self.DYNPD, self.DPL_P0 | self.DPL_P1)
         if self.payload  == self.ACK_PAYLOAD:
            self._NRFWriteReg(self.FEATURE, self.EN_DPL | self.EN_ACK_PAY)
         else:
            self._NRFWriteReg(self.FEATURE, self.EN_DPL)

   def __init__(self,
      sbc,                      # sbc connection
      CE,                       # GPIO for chip enable
      spi_channel=0,            # SPI channel
      spi_device=0,             # SPI device
      spi_speed=50e3,           # SPI bps
      mode=RX,                  # primary mode (RX or TX)
      channel=1,                # radio channel
      payload=8,                # message size in bytes
      pad=32,                   # value used to pad short messages
      address_bytes=5,          # RX/TX address length in bytes
      crc_bytes=1               # number of CRC bytes
         ):
      """
      Instantiate with the sbc to which the card reader is connected.

      Optionally the SPI channel/device may be specified.  The default is
      spidev0.0.
      """

      self.sbc = sbc

      assert 0 <= CE <= 31

      self._chip = sbc.gpiochip_open(0)

      self.CE = CE

      sbc.gpio_claim_output(self._chip, CE, 0)

      self.unsetCE()

      assert NRF24.SPI_MAIN_CE0 <= spi_channel <= NRF24.SPI_AUX_CE2

      assert 32000 <= spi_speed <= 10e6

      self.spih = sbc.spi_open(spi_channel, spi_device, int(spi_speed))

      self.setChannel(channel)

      self.setPayload(payload)

      self.setPadValue(pad)

      self.setAddressBytes(address_bytes)

      self.setCRCBytes(crc_bytes)

      self.PTX = 0

      self.powerDown()

      self._NRFWriteReg(self.SETUP_RETR, 0b11111)

      self.flushRX()
      self.flushTX()

      self.powerUpRX()

   def setChannel(self, channel):
      assert 0 <= channel <= 125
      self.channel = channel # frequency (2400 + channel) MHz
      self._NRFWriteReg(self.RF_CH, self.channel)

   def setPayload(self, payload):
      assert self.ACK_PAYLOAD <= payload <= self.MAX_PAYLOAD
      self.payload = payload # 0 is dynamic payload
      self._configurePayload()

   def setPadValue(self, pad):
      try:
         self.pad = ord(pad)
      except:
         self.pad = pad
      assert 0 <= self.pad <= 255

   def setAddressBytes(self, address_bytes):
      assert 3 <= address_bytes <= 5
      self.width = address_bytes
      self._NRFWriteReg(self.SETUP_AW, self.width - 2)

   def setCRCBytes(self, crc_bytes):
      assert 1 <= crc_bytes <= 2
      if crc_bytes == 1:
         self.CRC = 0
      else:
         self.CRC = self.CRCO

   def showRegisters(self):
      print(self.format_CONFIG())
      print(self.format_EN_AA())
      print(self.format_EN_RXADDR())
      print(self.format_SETUP_AW())
      print(self.format_SETUP_RETR())
      print(self.format_RF_CH())
      print(self.format_RF_SETUP())
      print(self.format_STATUS())
      print(self.format_OBSERVE_TX())
      print(self.format_RPD())
      print(self.format_RX_ADDR_PX())
      print(self.format_TX_ADDR())
      print(self.format_RX_PW_PX())
      print(self.format_FIFO_STATUS())
      print(self.format_DYNPD())
      print(self.format_FEATURE())

   def _setFixedWidth(self, msg, width, pad):
      msg = self._tobuf(msg)
      if len(msg) >= width:
         return msg[:width]
      msg.extend([pad]*(width-len(msg)))
      return msg

   def send(self, data):

      status = self.getStatus()

      if status & (self.TX_FULL | self.MAX_RT):
         self.flushTX()

      if self.payload >= self.MIN_PAYLOAD: # fixed payload
         data = self._setFixedWidth(data, self.payload, self.pad)
      else:
         data = self._tobuf(data)


      self._NRFCommand([self.W_TX_PAYLOAD] + data)

      self.powerUpTX()

   def ack_payload(self, data):
      self._NRFCommand([self.W_ACK_PAYLOAD] + self._tobuf(data))

   def setLocalAddress(self, laddr):

      addr = self._setFixedWidth(laddr, self.width, self.pad)

      self.unsetCE()

      self._NRFWriteReg(self.RX_ADDR_P1, addr)

      self.setCE()

   def setRemoteAddress(self, raddr): 

      addr = self._setFixedWidth(raddr, self.width, self.pad)

      self.unsetCE();

      self._NRFWriteReg(self.TX_ADDR, addr)
      self._NRFWriteReg(self.RX_ADDR_P0, addr) # Needed for auto acks

      self.setCE()

   def dataReady(self):

      status = self.getStatus()

      if status & self.RX_DR:
         return True

      status = self._NRFReadReg(self.FIFO_STATUS, 1)[0]

      if status & self.FRX_EMPTY:
         return False
      else:
         return True

   def isSending(self):

      if self.PTX > 0:
         status = self.getStatus()

         if  status & (self.TX_DS | self.MAX_RT):
            self.powerUpRX()
            return False
         
         return True

      return False

   def getPayload(self):

      if self.payload < self.MIN_PAYLOAD: # dynamic payload
         bytes = self._NRFCommand([self.R_RX_PL_WID, 0])[1]
      else: # fixed payload
         bytes = self.payload

      d = self._NRFReadReg(self.R_RX_PAYLOAD, bytes)

      self.unsetCE() # added

      self._NRFWriteReg(self.STATUS, self.RX_DR)

      self.setCE() # added

      return d

   def getStatus(self):

      return self._NRFCommand(self.NOP)[0]

   def powerUpTX(self):

      self.unsetCE()

      self.PTX = 1

      config = self.EN_CRC | self.CRC | self.PWR_UP

      self._NRFWriteReg(self.CONFIG, config)

      self._NRFWriteReg(self.STATUS, self.RX_DR | self.TX_DS | self.MAX_RT)

      self.setCE()

   def powerUpRX(self):

      self.unsetCE()

      self.PTX = 0

      config = self.EN_CRC | self.CRC | self.PWR_UP | self.PRIM_RX

      self._NRFWriteReg(self.CONFIG, config)

      self._NRFWriteReg(self.STATUS, self.RX_DR | self.TX_DS | self.MAX_RT)

      self.setCE()

   def powerDown(self):

      self.unsetCE()

      self._NRFWriteReg(self.CONFIG, self.EN_CRC | self.CRC)

   def setCE(self):

      self.sbc.gpio_write(self._chip, self.CE, 1)

   def unsetCE(self):

      self.sbc.gpio_write(self._chip, self.CE, 0)

   def flushRX(self):

      self._NRFCommand(self.FLUSH_RX)

   def flushTX(self):

      self._NRFCommand(self.FLUSH_TX)

   _AUX_SPI=(1<<8)

   R_REGISTER          = 0x00 # reg in bits 0-4, read 1-5 bytes
   W_REGISTER          = 0x20 # reg in bits 0-4, write 1-5 bytes
   R_RX_PL_WID         = 0x60
   R_RX_PAYLOAD        = 0x61 # read 1-32 bytes
   W_TX_PAYLOAD        = 0xA0 # write 1-32 bytes
   W_ACK_PAYLOAD       = 0xA8 # pipe in bits 0-2, write 1-32 bytes
   W_TX_PAYLOAD_NO_ACK = 0xB0 # no ACK, write 1-32 bytes
   FLUSH_TX            = 0xE1
   FLUSH_RX            = 0xE2
   REUSE_TX_PL         = 0xE3
   NOP                 = 0xFF # no operation

   CONFIG      = 0x00
   EN_AA       = 0x01
   EN_RXADDR   = 0x02
   SETUP_AW    = 0x03
   SETUP_RETR  = 0x04
   RF_CH       = 0x05
   RF_SETUP    = 0x06
   STATUS      = 0x07
   OBSERVE_TX  = 0x08
   RPD         = 0x09
   RX_ADDR_P0  = 0x0A
   RX_ADDR_P1  = 0x0B
   RX_ADDR_P2  = 0x0C
   RX_ADDR_P3  = 0x0D
   RX_ADDR_P4  = 0x0E
   RX_ADDR_P5  = 0x0F
   TX_ADDR     = 0x10
   RX_PW_P0    = 0x11
   RX_PW_P1    = 0x12
   RX_PW_P2    = 0x13
   RX_PW_P3    = 0x14
   RX_PW_P4    = 0x15
   RX_PW_P5    = 0x16
   FIFO_STATUS = 0x17
   DYNPD       = 0x1C
   FEATURE     = 0x1D

   # CONFIG

   MASK_RX_DR =  1 << 6
   MASK_TX_DS =  1 << 5
   MASK_MAX_RT = 1 << 4
   EN_CRC =      1 << 3 # default
   CRCO =        1 << 2
   PWR_UP =      1 << 1
   PRIM_RX =     1 << 0

   def format_CONFIG(self):

      v = self._NRFReadReg(self.CONFIG, 1)[0]

      s = "CONFIG: "

      if v & self.MASK_RX_DR:
         s += "no RX_DR IRQ, "
      else:
         s += "RX_DR IRQ, "

      if v & self.MASK_TX_DS:
         s += "no TX_DS IRQ, "
      else:
         s += "TX_DS IRQ, "

      if v & self.MASK_MAX_RT:
         s += "no MAX_RT IRQ, "
      else:
         s += "MAX_RT IRQ, "

      if v & self.EN_CRC:
         s += "CRC on, "
      else:
         s += "CRC off, "

      if v & self.CRCO:
         s += "CRC 2 byte, "
      else:
         s += "CRC 1 byte, "

      if v & self.PWR_UP:
         s += "Power up, "
      else:
         s += "Power down, "

      if v & self.PRIM_RX:
         s += "RX"
      else:
         s += "TX"

      return s

   # EN_AA

   ENAA_P5 = 1 << 5 # default
   ENAA_P4 = 1 << 4 # default
   ENAA_P3 = 1 << 3 # default
   ENAA_P2 = 1 << 2 # default
   ENAA_P1 = 1 << 1 # default
   ENAA_P0 = 1 << 0 # default

   def format_EN_AA(self):

      v = self._NRFReadReg(self.EN_AA, 1)[0]

      s = "EN_AA: "

      for i in range(6):
         if v & (1<<i):
            s += "P{}:ACK ".format(i)
         else:
            s += "P{}:no ACK ".format(i)

      return s

   # EN_RXADDR

   ERX_P5 = 1 << 5
   ERX_P4 = 1 << 4
   ERX_P3 = 1 << 3
   ERX_P2 = 1 << 2
   ERX_P1 = 1 << 1 # default
   ERX_P0 = 1 << 0 # default

   def format_EN_RXADDR(self):

      v = self._NRFReadReg(self.EN_RXADDR, 1)[0]

      s = "EN_RXADDR: "

      for i in range(6):
         if v & (1<<i):
            s += "P{}:on ".format(i)
         else:
            s += "P{}:off ".format(i)

      return s

   # SETUP_AW

   AW_3 = 1
   AW_4 = 2
   AW_5 = 3 # default

   def format_SETUP_AW(self):

      v = self._NRFReadReg(self.SETUP_AW, 1)[0]

      s = "SETUP_AW: address width bytes "

      if v == self.AW_3:
         s += "3"
      elif v == self.AW_4:
         s += "4"
      elif v == self.AW_5:
         s += "5"
      else:
         s += "invalid"

      return s

   # SETUP_RETR

   # ARD 7-4
   # ARC 3-0

   def format_SETUP_RETR(self):

      v = self._NRFReadReg(self.SETUP_RETR, 1)[0]

      ard = (((v>>4)&15)*250)+250
      arc = v & 15
      s = "SETUP_RETR: retry delay {} us, retries {}".format(ard, arc)

      return s

   # RF_CH

   # RF_CH 6-0

   def format_RF_CH(self):

      v = self._NRFReadReg(self.RF_CH, 1)[0]

      s = "RF_CH: channel {}".format(v&127)

      return s

   # RF_SETUP

   CONT_WAVE  =  1 << 7
   RF_DR_LOW  =  1 << 5
   PLL_LOCK   =  1 << 4
   RF_DR_HIGH =  1 << 3
   # RF_PWR  2-1

   def format_RF_SETUP(self):

      v = self._NRFReadReg(self.RF_SETUP, 1)[0]

      s = "RF_SETUP: "

      if v & self.CONT_WAVE:
         s += "continuos carrier on, "
      else:
         s += "no continuous carrier, "

      if v & self.PLL_LOCK:
         s += "force PLL lock on, "
      else:
         s += "no force PLL lock, "

      dr = 0

      if v & self.RF_DR_LOW:
         dr += 2

      if v & self.RF_DR_HIGH:
         dr += 1

      if dr == 0:
         s += "1 Mbps, "
      elif dr == 1:
         s += "2 Mbps, "
      elif dr == 2:
         s += "250 kbps, "
      else:
         s += "illegal speed, "

      pwr = (v>>1) & 3

      if pwr == 0:
         s += "-18 dBm"
      elif pwr == 1:
         s += "-12 dBm"
      elif pwr == 2:
         s += "-6 dBm"
      else:
         s += "0 dBm"

      return s

   # STATUS

   RX_DR      =  1 << 6
   TX_DS      =  1 << 5
   MAX_RT     =  1 << 4
   # RX_P_NO 3-1
   TX_FULL    =  1 << 0

   def format_STATUS(self):

      v = self._NRFReadReg(self.STATUS, 1)[0]

      s = "STATUS: "

      if v & self.RX_DR:
         s += "RX data, "
      else:
         s += "no RX data, "

      if v & self.TX_DS:
         s += "TX ok, "
      else:
         s += "no TX, "

      if v & self.MAX_RT:
         s += "TX retries bad, "
      else:
         s += "TX retries ok, "

      p = (v>>1)&7

      if p < 6:
         s += "pipe {} data, ".format(p)
      elif p == 6:
         s += "PIPE 6 ERROR, "
      else:
         s += "no pipe data, "

      if v & self.TX_FULL:
         s += "TX FIFO full"
      else:
         s += "TX FIFO not full"

      return s

   # OBSERVE_TX

   # PLOS_CNT 7-4
   # ARC_CNT 3-0

   def format_OBSERVE_TX(self):

      v = self._NRFReadReg(self.OBSERVE_TX, 1)[0]

      plos = (v>>4)&15
      arc = v & 15
      s = "OBSERVE_TX: lost packets {}, retries {}".format(plos, arc)

      return s

   # RPD

   # RPD 1 << 0

   def format_RPD(self):

      v = self._NRFReadReg(self.RPD, 1)[0]

      s = "RPD: received power detector {}".format(v&1)

      return s

   # RX_ADDR_P0 - RX_ADDR_P5

   def _byte2hex(self, s):

      return ":".join("{:02x}".format(c) for c in s)

   def format_RX_ADDR_PX(self):

      p0 = self._NRFReadReg(self.RX_ADDR_P0, 5)
      p1 = self._NRFReadReg(self.RX_ADDR_P1, 5)
      p2 = self._NRFReadReg(self.RX_ADDR_P2, 1)[0]
      p3 = self._NRFReadReg(self.RX_ADDR_P3, 1)[0]
      p4 = self._NRFReadReg(self.RX_ADDR_P4, 1)[0]
      p5 = self._NRFReadReg(self.RX_ADDR_P5, 1)[0]

      s  = "RX ADDR_PX: "
      s += "P0=" + self._byte2hex(p0) + " "
      s += "P1=" + self._byte2hex(p1) + " "
      s += "P2={:02x} ".format(p2)
      s += "P3={:02x} ".format(p3)
      s += "P4={:02x} ".format(p4)
      s += "P5={:02x}".format(p5)

      return s

   # TX_ADDR

   def format_TX_ADDR(self):

      p0 = self._NRFReadReg(self.TX_ADDR, 5)

      s  = "TX_ADDR: " + self._byte2hex(p0)

      return s

   # RX_PW_P0 - RX_PW_P5

   def format_RX_PW_PX(self):

      p0 = self._NRFReadReg(self.RX_PW_P0, 1)[0]
      p1 = self._NRFReadReg(self.RX_PW_P1, 1)[0]
      p2 = self._NRFReadReg(self.RX_PW_P2, 1)[0]
      p3 = self._NRFReadReg(self.RX_PW_P3, 1)[0]
      p4 = self._NRFReadReg(self.RX_PW_P4, 1)[0]
      p5 = self._NRFReadReg(self.RX_PW_P5, 1)[0]

      s = "RX_PW_PX: "
      s += "P0={} ".format(p0)
      s += "P1={} ".format(p1)
      s += "P2={} ".format(p2)
      s += "P3={} ".format(p3)
      s += "P4={} ".format(p4)
      s += "P5={} ".format(p5)

      return s

   # FIFO_STATUS

   FTX_REUSE = 1 << 6
   FTX_FULL =  1 << 5
   FTX_EMPTY = 1 << 4
   FRX_FULL =  1 << 1
   FRX_EMPTY = 1 << 0

   def format_FIFO_STATUS(self):

      v = self._NRFReadReg(self.FIFO_STATUS, 1)[0]

      s = "FIFO_STATUS: "

      if v & self.FTX_REUSE:
         s += "TX reuse set, "
      else:
         s += "TX reuse not set, "

      if v & self.FTX_FULL:
         s += "TX FIFO full, "
      elif v & self.FTX_EMPTY:
         s += "TX FIFO empty, "
      else:
         s += "TX FIFO has data, "

      if v & self.FRX_FULL:
         s += "RX FIFO full, "
      elif v & self.FRX_EMPTY:
         s += "RX FIFO empty"
      else:
         s += "RX FIFO has data"

      return s

   # DYNPD

   DPL_P5 = 1 << 5
   DPL_P4 = 1 << 4
   DPL_P3 = 1 << 3
   DPL_P2 = 1 << 2
   DPL_P1 = 1 << 1
   DPL_P0 = 1 << 0

   def format_DYNPD(self):

      v = self._NRFReadReg(self.DYNPD, 1)[0]

      s = "DYNPD: "

      for i in range(6):
         if v & (1<<i):
            s += "P{}:on ".format(i)
         else:
            s += "P{}:off ".format(i)

      return s

   # FEATURE

   EN_DPL =     1 << 2
   EN_ACK_PAY = 1 << 1
   EN_DYN_ACK = 1 << 0

   def format_FEATURE(self):

      v = self._NRFReadReg(self.FEATURE, 1)[0]

      s = "FEATURE: "

      if v & self.EN_DPL:
         s += "Dynamic payload on, "
      else:
         s += "Dynamic payload off, "

      if v & self.EN_ACK_PAY:
         s += "ACK payload on, "
      else:
         s += "ACK payload off, "

      if v & self.EN_DYN_ACK:
         s += "W_TX_PAYLOAD_NOACK on"
      else:
         s += "W_TX_PAYLOAD_NOACK off"

      return s

if __name__ == "__main__":

   import sys
   import time
   import lgpio as sbc
   import NRF24

   test_words = [
"Now", "is", "the", "winter", "of", "our", "discontent",
"Made", "glorious", "summer", "by", "this", "sun", "of", "York",
"And", "all", "the", "clouds", "that", "lour'd", "upon", "our", "house",
"In", "the", "deep", "bosom", "of", "the", "ocean", "buried",
"Now", "are", "our", "brows", "bound", "with", "victorious", "wreaths",
"Our", "bruised", "arms", "hung", "up", "for", "monuments",
"Our", "stern", "alarums", "changed", "to", "merry", "meetings",
"Our", "dreadful", "marches", "to", "delightful", "measures",
"Grim-visaged", "war", "hath", "smooth'd", "his", "wrinkled", "front",
"And", "now", "instead", "of", "mounting", "barded", "steeds",
"To", "fright", "the", "souls", "of", "fearful", "adversaries",
"He", "capers", "nimbly", "in", "a", "lady's", "chamber",
"To", "the", "lascivious", "pleasing", "of", "a", "lute",
"But", "I", "that", "am", "not", "shaped", "for", "sportive", "tricks",
"Nor", "made", "to", "court", "an", "amorous", "looking-glass",
"I", "that", "am", "rudely", "stamp'd", "and", "want", "love's", "majesty",
"To", "strut", "before", "a", "wanton", "ambling", "nymph",
"I", "that", "am", "curtail'd", "of", "this", "fair", "proportion",
"Cheated", "of", "feature", "by", "dissembling", "nature",
"Deformed", "unfinish'd", "sent", "before", "my", "time",
"Into", "this", "breathing", "world", "scarce", "half", "made", "up",
"And", "that", "so", "lamely", "and", "unfashionable",
"That", "dogs", "bark", "at", "me", "as", "I", "halt", "by", "them",
"Why", "I", "in", "this", "weak", "piping", "time", "of", "peace",
"Have", "no", "delight", "to", "pass", "away", "the", "time",
"Unless", "to", "spy", "my", "shadow", "in", "the", "sun",
"And", "descant", "on", "mine", "own", "deformity",
"And", "therefore", "since", "I", "cannot", "prove", "a", "lover",
"To", "entertain", "these", "fair", "well-spoken", "days",
"I", "am", "determined", "to", "prove", "a", "villain",
"And", "hate", "the", "idle", "pleasures", "of", "these", "days",
"Plots", "have", "I", "laid", "inductions", "dangerous",
"By", "drunken", "prophecies", "libels", "and", "dreams",
"To", "set", "my", "brother", "Clarence", "and", "the", "king",
"In", "deadly", "hate", "the", "one", "against", "the", "other",
"And", "if", "King", "Edward", "be", "as", "true", "and", "just",
"As", "I", "am", "subtle", "false", "and", "treacherous",
"This", "day", "should", "Clarence", "closely", "be", "mew'd", "up",
"About", "a", "prophecy", "which", "says", "that", "'G'",
"Of", "Edward's", "heirs", "the", "murderer", "shall", "be",
"Dive", "thoughts", "down", "to", "my", "soul", "here",
"Clarence", "comes"]

   number_of_test_words = len(test_words)

   if len(sys.argv) > 1:
      SENDING = True
   else:
      SENDING = False

   ver = "L" + str(sys.version_info[0]) + '.' + str(sys.version_info[1])

   end_time = time.time() + 3600

   nrf = NRF24.NRF24(
      sbc, CE=27, payload=NRF24.NRF24.ACK_PAYLOAD,
      pad='*', address_bytes=3, crc_bytes=2)

   nrf.showRegisters();

   if SENDING:

      count = 0

      nrf.setLocalAddress("h1")
      nrf.setRemoteAddress("h2")

      while time.time() < end_time:
         #print(nrf.format_FIFO_STATUS())
         #print(nrf.format_OBSERVE_TX())
         if not nrf.isSending():
            print("{}> {}".format(ver, test_words[count]))
            nrf.send(test_words[count])
            count += 1
            if count >= number_of_test_words:
               count = 0
         time.sleep(0.5)

   else:

      nrf.setLocalAddress("h2")
      nrf.setRemoteAddress("h1")

      while time.time() < end_time:
         #print(nrf.format_FIFO_STATUS())
         #print(nrf.format_OBSERVE_TX())
         while nrf.dataReady():
            print("{}< {}".format(ver, nrf.getPayload()))
         time.sleep(0.5)

   sbc.spi_close(nrf.spih)

