/*
NRF24.c
2020-12-30
Public Domain

http://abyz.me.uk/lg/rgpio.html

gcc -Wall -o NRF24 NRF24.c -lrgpio

./NRF24   # rx
./NRF24 x # tx
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <lgpio.h>
#include <rgpio.h>

#define   NRF_TX  0
#define   NRF_RX  1

#define   NRF_ACK_PAYLOAD  -1
#define   NRF_DYNAMIC_PAYLOAD  0
#define   NRF_MIN_PAYLOAD  1
#define   NRF_MAX_PAYLOAD  32

#define   NRF_R_REGISTER           0x00 /* reg in bits 0-4, read 1-5 bytes */
#define   NRF_W_REGISTER           0x20 /* reg in bits 0-4, write 1-5 bytes */
#define   NRF_R_RX_PL_WID          0x60
#define   NRF_R_RX_PAYLOAD         0x61 /* read 1-32 bytes */
#define   NRF_W_TX_PAYLOAD         0xA0 /* write 1-32 bytes */
#define   NRF_W_ACK_PAYLOAD        0xA8 /* pipe in bits 0-2, write 1-32 bytes */
#define   NRF_W_TX_PAYLOAD_NO_ACK  0xB0 /* no ACK, write 1-32 bytes */
#define   NRF_FLUSH_TX             0xE1
#define   NRF_FLUSH_RX             0xE2
#define   NRF_REUSE_TX_PL          0xE3
#define   NRF_NOP                  0xFF /* no operation */

#define   NRF_CONFIG       0x00
#define   NRF_EN_AA        0x01
#define   NRF_EN_RXADDR    0x02
#define   NRF_SETUP_AW     0x03
#define   NRF_SETUP_RETR   0x04
#define   NRF_RF_CH        0x05
#define   NRF_RF_SETUP     0x06
#define   NRF_STATUS       0x07
#define   NRF_OBSERVE_TX   0x08
#define   NRF_RPD          0x09
#define   NRF_RX_ADDR_P0   0x0A
#define   NRF_RX_ADDR_P1   0x0B
#define   NRF_RX_ADDR_P2   0x0C
#define   NRF_RX_ADDR_P3   0x0D
#define   NRF_RX_ADDR_P4   0x0E
#define   NRF_RX_ADDR_P5   0x0F
#define   NRF_TX_ADDR      0x10
#define   NRF_RX_PW_P0     0x11
#define   NRF_RX_PW_P1     0x12
#define   NRF_RX_PW_P2     0x13
#define   NRF_RX_PW_P3     0x14
#define   NRF_RX_PW_P4     0x15
#define   NRF_RX_PW_P5     0x16
#define   NRF_FIFO_STATUS  0x17
#define   NRF_DYNPD        0x1C
#define   NRF_FEATURE      0x1D

/* NRF_CONFIG */
#define   NRF_MASK_RX_DR   1 << 6
#define   NRF_MASK_TX_DS   1 << 5
#define   NRF_MASK_MAX_RT  1 << 4
#define   NRF_EN_CRC       1 << 3 /* default */
#define   NRF_CRCO         1 << 2
#define   NRF_PWR_UP       1 << 1
#define   NRF_PRIM_RX      1 << 0

/* EN_AA */
#define   NRF_ENAA_P5  1 << 5 /* default */
#define   NRF_ENAA_P4  1 << 4 /* default */
#define   NRF_ENAA_P3  1 << 3 /* default */
#define   NRF_ENAA_P2  1 << 2 /* default */
#define   NRF_ENAA_P1  1 << 1 /* default */
#define   NRF_ENAA_P0  1 << 0 /* default */

/* EN_RXADDR */
#define   NRF_ERX_P5  1 << 5
#define   NRF_ERX_P4  1 << 4
#define   NRF_ERX_P3  1 << 3
#define   NRF_ERX_P2  1 << 2
#define   NRF_ERX_P1  1 << 1 /* default */
#define   NRF_ERX_P0  1 << 0 /* default */

/* NRF_SETUP_AW */
#define   NRF_AW_3  1
#define   NRF_AW_4  2
#define   NRF_AW_5  3 /* default */

/* NRF_RF_SETUP */
#define   NRF_CONT_WAVE    1 << 7
#define   NRF_RF_DR_LOW    1 << 5
#define   NRF_PLL_LOCK     1 << 4
#define   NRF_RF_DR_HIGH   1 << 3

/* NRF_STATUS */
#define   NRF_RX_DR        1 << 6
#define   NRF_TX_DS        1 << 5
#define   NRF_MAX_RT       1 << 4

/* RX_P_NO 3-1 */
#define   NRF_TX_FULL      1 << 0

/* NRF_OBSERVE_TX */
/* PLOS_CNT 7-4 */
/* ARC_CNT 3-0 */
/* NRF_RPD */
/* NRF_RPD 1 << 0 */
/* NRF_RX_ADDR_P0 - NRF_RX_ADDR_P5 */

/* NRF_FIFO_STATUS */
#define   NRF_FTX_REUSE  1 << 6
#define   NRF_FTX_FULL   1 << 5
#define   NRF_FTX_EMPTY  1 << 4
#define   NRF_FRX_FULL   1 << 1
#define   NRF_FRX_EMPTY  1 << 0

/* NRF_DYNPD */
#define   NRF_DPL_P5  1 << 5
#define   NRF_DPL_P4  1 << 4
#define   NRF_DPL_P3  1 << 3
#define   NRF_DPL_P2  1 << 2
#define   NRF_DPL_P1  1 << 1
#define   NRF_DPL_P0  1 << 0

/* NRF_FEATURE */
#define   NRF_EN_DPL      1 << 2
#define   NRF_EN_ACK_PAY  1 << 1
#define   NRF_EN_DYN_ACK  1 << 0

/*
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
*/

typedef struct
{
   int sbc;           // sbc connection
   int CE;            // GPIO for chip enable

   int spi_channel;   // SPI channel
   int spi_device;    // SPI device
   int spi_speed;     // SPI bps
   int mode;          // primary mode (RX or TX)
   int channel;       // radio channel
   int payload;       // message size in bytes
   int pad;           // value used to pad short messages
   int address_bytes; // RX/TX address length in bytes
   int crc_bytes;     // number of CRC bytes

   int spih;
   int chip;
   int PTX;
   int CRC;
} nrf_t, *nrf_p;


int NRF_xfer(nrf_p nrf, char *txBuf, char *rxBuf, int count)
{
   return spi_xfer(nrf->sbc, nrf->spih, txBuf, rxBuf, count);
}

int NRF_read_register(nrf_p nrf, int reg, char *rxBuf, int count)
{
   int i;
   char txBuf[64];
   char buf[64];

   txBuf[0] = reg;
   for (i=1; i<=count; i++) txBuf[i]=0;

   i = NRF_xfer(nrf, txBuf, buf, count+1);

   if (i >= 0)
   {
      for (i=0; i<count; i++) rxBuf[i] = buf[i+1];
      return count;
   }
   return i;
}

int NRF_write_register(nrf_p nrf, int reg, char *txBuf, int count)
{
   int i;
   char buf[64];
   char rxBuf[64];

   buf[0] = NRF_W_REGISTER | reg;
   for (i=0; i<count; i++) buf[i+1] = txBuf[i];
   i = NRF_xfer(nrf, buf, rxBuf, count+1);

   return i;
}


int NRF_get_status(nrf_p nrf)
{
   int res;
   char txBuf[8];
   char rxBuf[8];

   txBuf[0] = NRF_NOP;

   res = NRF_xfer(nrf, txBuf, rxBuf, 1);

   if (res >= 0) res = rxBuf[0];

   return res;
}

void NRF_set_CE(nrf_p nrf)
{
   gpio_write(nrf->sbc, nrf->chip, nrf->CE, 1);
}

void NRF_unset_CE(nrf_p nrf)
{
   gpio_write(nrf->sbc, nrf->chip, nrf->CE, 0);
}

void NRF_flush_tx(nrf_p nrf)
{
   char txBuf[64];
   char rxBuf[64];

   txBuf[0] = NRF_FLUSH_TX;
   NRF_xfer(nrf, txBuf, rxBuf, 1);
}

void NRF_power_up_tx(nrf_p nrf)
{
   char txBuf[128];

   NRF_unset_CE(nrf);

   nrf->PTX = 1;

   txBuf[0] = NRF_EN_CRC | nrf->CRC | NRF_PWR_UP;
   NRF_write_register(nrf, NRF_CONFIG, txBuf, 1);

   txBuf[0] = NRF_RX_DR | NRF_TX_DS | NRF_MAX_RT;
   NRF_write_register(nrf, NRF_STATUS, txBuf, 1);

   NRF_set_CE(nrf);
}

void NRF_power_up_rx(nrf_p nrf)
{
   char txBuf[64];

   NRF_unset_CE(nrf);

   nrf->PTX = 0;

   txBuf[0] = NRF_EN_CRC | nrf->CRC | NRF_PWR_UP | NRF_PRIM_RX;
   NRF_write_register(nrf, NRF_CONFIG, txBuf, 1);

   txBuf[0] = NRF_RX_DR | NRF_TX_DS | NRF_MAX_RT;
   NRF_write_register(nrf, NRF_STATUS, txBuf, 1);


   NRF_set_CE(nrf);
}


void NRF_configure_payload(nrf_p nrf)
{
   char txBuf[256];

   if (nrf->payload >= NRF_MIN_PAYLOAD) // fixed payload
   {
      txBuf[0] = nrf->payload;
      NRF_write_register(nrf, NRF_RX_PW_P0, txBuf, 1);
      NRF_write_register(nrf, NRF_RX_PW_P1, txBuf, 1);
      txBuf[0] = 0;
      NRF_write_register(nrf, NRF_DYNPD, txBuf, 1);
      NRF_write_register(nrf, NRF_FEATURE, txBuf, 1);
   }
   else // dynamic payload
   {
      txBuf[0] = NRF_DPL_P0 | NRF_DPL_P1;
      NRF_write_register(nrf, NRF_DYNPD, txBuf, 1);
      if (nrf->payload  == NRF_ACK_PAYLOAD)
         txBuf[0]= NRF_EN_DPL | NRF_EN_ACK_PAY;
      else txBuf[0] = NRF_EN_DPL;
      NRF_write_register(nrf, NRF_FEATURE, txBuf, 1);
   }
}


void NRF_set_channel(nrf_p nrf, int channel)
{
   char txBuf[8];
   nrf->channel = channel; // frequency (2400 + channel) MHz
   txBuf[0] = channel;
   NRF_write_register(nrf, NRF_RF_CH, txBuf, 1);
}

void NRF_set_payload(nrf_p nrf, int payload)
{
   //assert ACK_PAYLOAD <= payload <= MAX_PAYLOAD
   nrf->payload = payload;  // 0 is dynamic payload
   NRF_configure_payload(nrf);
}

void NRF_set_pad_value(nrf_p nrf, int pad)
{
   //assert 0 <= pad <= 255
   nrf->pad = pad;
}

void NRF_set_address_bytes(nrf_p nrf, int address_bytes)
{
   char txBuf[8];
   //assert 3 <= address_bytes <= 5
   nrf->address_bytes = address_bytes;
   txBuf[0] = nrf->address_bytes - 2;
   NRF_write_register(nrf, NRF_SETUP_AW, txBuf, 1);
}

void NRF_set_CRC_bytes(nrf_p nrf, int crc_bytes)
{
   //assert 1 <= crc_bytes <= 2
   if (crc_bytes == 1) nrf->CRC = 0;
   else                nrf->CRC = NRF_CRCO;
}

  
void NRF_set_fixed_width(char *data, int *count, int width, int pad)
{
   int i;

   for (i=*count; i<width; i++) data[i] = pad;
   *count = width;
}

void NRF_send(nrf_p nrf, char *data, int count)
{
   int status;
   int i;
   int n = count;
   char txBuf[256];
   char rxBuf[256];

   status = NRF_get_status(nrf);

   if (status & (NRF_TX_FULL | NRF_MAX_RT)) NRF_flush_tx(nrf);

   if (nrf->payload >= NRF_MIN_PAYLOAD) // fixed payload
      NRF_set_fixed_width(data, &n, nrf->payload, nrf->pad);

   txBuf[0] = NRF_W_TX_PAYLOAD;
   for (i=0; i<n; i++) txBuf[i+1] = data[i];

   NRF_xfer(nrf, txBuf, rxBuf, n+1);

   NRF_power_up_tx(nrf);
}

void NRF_ack_payload(nrf_p nrf, char *data, int count)
{
   int i;
   char txBuf[256];
   txBuf[0] = NRF_W_ACK_PAYLOAD;
   for (i=0; i<count; i++) txBuf[i+1] = data[i];
   NRF_xfer(nrf, txBuf, NULL, count+1);
}

void NRF_set_local_address(nrf_p nrf, char *addr)
{
   int i, n;
   char txBuf[64];
   n = strlen(addr);
   for (i=0; i<n; i++) txBuf[i] = addr[i];
   NRF_set_fixed_width(txBuf, &n, nrf->address_bytes, nrf->pad);

   NRF_unset_CE(nrf);

   NRF_write_register(nrf, NRF_RX_ADDR_P1, txBuf, n);

   NRF_set_CE(nrf);
}

void NRF_set_remote_address(nrf_p nrf, char *addr)
{
   int i, n;
   char txBuf[64];
   n = strlen(addr);
   for (i=0; i<n; i++) txBuf[i] = addr[i];
   NRF_set_fixed_width(txBuf, &n, nrf->address_bytes, nrf->pad);

   NRF_unset_CE(nrf);

   NRF_write_register(nrf, NRF_TX_ADDR, txBuf, n);
   NRF_write_register(nrf, NRF_RX_ADDR_P0, txBuf, n); // Needed for auto acks

   NRF_set_CE(nrf);
}

int NRF_data_ready(nrf_p nrf)
{
   int status;
   char rxBuf[8];
   status = NRF_get_status(nrf);

   if (status & NRF_RX_DR) return 1;

   NRF_read_register(nrf, NRF_FIFO_STATUS, rxBuf, 1);

   status = rxBuf[0];

   if (status & NRF_FRX_EMPTY) return 0; else return 1;
}

int NRF_is_sending(nrf_p nrf)
{
   int status;

   if (nrf->PTX > 0)
   {
      status = NRF_get_status(nrf);

      if  (status & (NRF_TX_DS | NRF_MAX_RT))
      {
         NRF_power_up_rx(nrf);
         return 0;
      }
      else return 1;
   }

   return 0;
}

char *NRF_get_payload(nrf_p nrf, char *rxBuf)
{
   char txBuf[64];
   int count;

   txBuf[0] = NRF_R_RX_PL_WID;
   txBuf[1] = 0;

   if (nrf->payload < NRF_MIN_PAYLOAD) // dynamic payload
   {
      NRF_xfer(nrf, txBuf, rxBuf, 2);
      count = rxBuf[1];
   }
   else // fixed payload
      count = nrf->payload;

   NRF_read_register(nrf, NRF_R_RX_PAYLOAD, rxBuf, count);

   rxBuf[count] = 0; /* terminate string */

   NRF_unset_CE(nrf); // added

   txBuf[0] = NRF_RX_DR;
   NRF_write_register(nrf, NRF_STATUS, txBuf, 1);

   NRF_set_CE(nrf); // added

   return rxBuf;
}



void NRF_power_down(nrf_p nrf)
{
   char txBuf[64];

   NRF_unset_CE(nrf);

   txBuf[0] = NRF_EN_CRC | nrf->CRC;

   NRF_write_register(nrf, NRF_CONFIG, txBuf, 1);
}

void NRF_flush_rx(nrf_p nrf)
{
   char txBuf[64];
   char rxBuf[64];

   txBuf[0] = NRF_FLUSH_RX;
   NRF_xfer(nrf, txBuf, rxBuf, 1);
}

char *NRF_format_CONFIG(nrf_p nrf, char *s)
{
   int v;
   char rxBuf[16];

   NRF_read_register(nrf, NRF_CONFIG, rxBuf, 1);

   v = rxBuf[0];

   strcpy(s, "NRF_CONFIG: ");

   if (v & NRF_MASK_RX_DR)
      strcat(s, "no NRF_RX_DR IRQ, ");
   else
      strcat(s, "NRF_RX_DR IRQ, ");

   if (v & NRF_MASK_TX_DS)
      strcat(s, "no NRF_TX_DS IRQ, ");
   else
      strcat(s, "NRF_TX_DS IRQ, ");

   if (v & NRF_MASK_MAX_RT)
      strcat(s, "no NRF_MAX_RT IRQ, ");
   else
      strcat(s, "NRF_MAX_RT IRQ, ");

   if (v & NRF_EN_CRC)
      strcat(s, "CRC on, ");
   else
      strcat(s, "CRC off, ");

   if (v & NRF_CRCO)
      strcat(s, "CRC 2 byte, ");
   else
      strcat(s, "CRC 1 byte, ");

   if (v & NRF_PWR_UP)
      strcat(s, "Power up, ");
   else
      strcat(s, "Power down, ");

   if (v & NRF_PRIM_RX)
      strcat(s, "RX");
   else
      strcat(s, "TX");

   return s;
}

char *NRF_format_EN_AA(nrf_p nrf, char *s)
{
   char t[16];
   int i, v;

   NRF_read_register(nrf, NRF_EN_AA, t, 1);
   v = t[0];

   strcpy(s, "EN_AA: ");

   for (i=0; i<6; i++)
   {
      if (v & (1<<i)) sprintf(t, "P%d:ACK ", i);
      else            sprintf(t, "P%d:no ACK ", i);
      strcat(s, t);
   }

   return s;
}

char *NRF_format_EN_RXADDR(nrf_p nrf, char *s)
{
   int i, v;
   char t[16];

   NRF_read_register(nrf, NRF_EN_RXADDR, t, 1);
   v = t[0];

   strcpy(s, "EN_RXADDR: ");

   for (i=0; i<6; i++)
   {
      if (v & (1<<i)) sprintf(t, "P%d:on ", i);
      else            sprintf(t, "P%d:off ", i);
      strcat(s, t);
   }

   return s;
}

char *NRF_format_SETUP_AW(nrf_p nrf, char *s)
{
   int v;
   char t[8];

   NRF_read_register(nrf, NRF_SETUP_AW, t, 1);
   v = t[0];

   strcpy(s, "NRF_SETUP_AW: address width bytes ");

   if (v == NRF_AW_3)      strcat(s, "3");
   else if (v == NRF_AW_4) strcat(s, "4");
   else if (v == NRF_AW_5) strcat(s, "5");
   else                strcat(s, "invalid");

   return s;
}

char *NRF_format_SETUP_RETR(nrf_p nrf, char *s)
{
   int v, ard, arc;
   char t[8];

   NRF_read_register(nrf, NRF_SETUP_RETR, t, 1);
   v = t[0];

   ard = (((v>>4)&15)*250)+250;
   arc = v & 15;

   sprintf(s, "NRF_SETUP_RETR: retry delay %d us, retries %d", ard, arc);

   return s;
}

// NRF_RF_CH

// NRF_RF_CH 6-0

char *NRF_format_RF_CH(nrf_p nrf, char *s)
{
   int v;
   char t[8];

   NRF_read_register(nrf, NRF_RF_CH, t, 1);
   v = t[0];

   sprintf(s, "NRF_RF_CH: channel %d", v&127);

   return s;
}


char *NRF_format_RF_SETUP(nrf_p nrf, char *s)
{
   int v, dr, pwr;
   char t[8];

   NRF_read_register(nrf, NRF_RF_SETUP, t, 1);
   v = t[0];

   strcpy(s, "NRF_RF_SETUP: ");

   if (v & NRF_CONT_WAVE) strcat(s, "continuos carrier on, ");
   else               strcat(s, "no continuous carrier, ");

   if (v & NRF_PLL_LOCK) strcat(s, "force PLL lock on, ");
   else              strcat(s, "no force PLL lock, ");

   dr = 0;

   if (v & NRF_RF_DR_LOW) dr += 2;

   if (v & NRF_RF_DR_HIGH) dr += 1;

   if (dr == 0)      strcat(s, "1 Mbps, ");
   else if (dr == 1) strcat(s, "2 Mbps, ");
   else if (dr == 2) strcat(s, "250 kbps, ");
   else              strcat(s, "illegal speed, ");

   pwr = (v>>1) & 3;

   if (pwr == 0)      strcat(s, "-18 dBm");
   else if (pwr == 1) strcat(s, "-12 dBm");
   else if (pwr == 2) strcat(s, "-6 dBm");
   else               strcat(s, "0 dBm");

   return s;
}


char *NRF_format_STATUS(nrf_p nrf, char *s)
{
   int v, p;
   char t[32];

   NRF_read_register(nrf, NRF_STATUS, t, 1);
   v = t[0];

   strcpy(s, "NRF_STATUS: ");

   if (v & NRF_RX_DR) strcat(s, "RX data, ");
   else           strcat(s, "no RX data, ");

   if (v & NRF_TX_DS) strcat(s, "TX ok, ");
   else           strcat(s, "no TX, ");

   if (v & NRF_MAX_RT) strcat(s, "TX retries bad, ");
   else            strcat(s, "TX retries ok, ");

   p = (v>>1)&7;

   if (p < 6)
   {
      sprintf(t, "pipe %d data, ", p);
      strcat(s, t);
   }
   else if (p == 6) strcat(s, "PIPE 6 ERROR, ");
   else             strcat(s, "no pipe data, ");

   if (v & NRF_TX_FULL) strcat(s, "TX FIFO full");
   else             strcat(s, "TX FIFO not full");

   return s;
}


char *NRF_format_OBSERVE_TX(nrf_p nrf, char *s)
{
   int v, plos, arc;
   char t[8];

   NRF_read_register(nrf, NRF_OBSERVE_TX, t, 1);
   v = t[0];

   plos = (v>>4)&15;
   arc = v & 15;
   sprintf(s, "NRF_OBSERVE_TX: lost packets %d, retries %d", plos, arc);

   return s;
}

// NRF_RPD

// NRF_RPD 1 << 0

char *NRF_format_RPD(nrf_p nrf, char *s)
{
   int v;
   char t[8];

   NRF_read_register(nrf, NRF_RPD, t, 1);
   v = t[0];

   sprintf(s, "NRF_RPD: received power detector %d", v&1);

   return s;
}


char *NRF_byte2hex(char *p, char *s, int count)
{
   static char str[64];
   int i;
   char t[32];

   strcpy(str, p);
   for (i=0; i<count; i++)
   {
      sprintf(t, "%02x",  (unsigned char)s[i]);
      strcat(str, t);
   }
   strcat(str, " ");
   return str;
}

char *NRF_format_RX_ADDR_PX(nrf_p nrf, char *s)
{
   char p0[8];
   char p1[8];
   char p2[8];
   char p3[8];
   char p4[8];
   char p5[8];

   NRF_read_register(nrf, NRF_RX_ADDR_P0, p0, 5);
   NRF_read_register(nrf, NRF_RX_ADDR_P1, p1, 5);
   NRF_read_register(nrf, NRF_RX_ADDR_P2, p2, 1);
   NRF_read_register(nrf, NRF_RX_ADDR_P3, p3, 1);
   NRF_read_register(nrf, NRF_RX_ADDR_P4, p4, 1);
   NRF_read_register(nrf, NRF_RX_ADDR_P5, p5, 1);

   strcpy(s, "RX ADDR_PX: ");
   strcat(s, NRF_byte2hex("P0=", p0, 5));
   strcat(s, NRF_byte2hex("P1=", p1, 5));
   strcat(s, NRF_byte2hex("P2=", p2, 1));
   strcat(s, NRF_byte2hex("P3=", p3, 1));
   strcat(s, NRF_byte2hex("P4=", p4, 1));
   strcat(s, NRF_byte2hex("P5=", p5, 1));

   return s;
}


char *NRF_format_TX_ADDR(nrf_p nrf, char *s)
{
   char p0[8];

   NRF_read_register(nrf, NRF_TX_ADDR, p0, 5);

   sprintf(s, NRF_byte2hex("NRF_TX_ADDR: ", p0, 5));

   return s;
}


char *NRF_format_RX_PW_PX(nrf_p nrf, char *s)
{
   int i;
   char p[8];
   char t[16];

   NRF_read_register(nrf, NRF_RX_PW_P0, p, 1);
   NRF_read_register(nrf, NRF_RX_PW_P1, p+1, 1);
   NRF_read_register(nrf, NRF_RX_PW_P2, p+2, 1);
   NRF_read_register(nrf, NRF_RX_PW_P3, p+3, 1);
   NRF_read_register(nrf, NRF_RX_PW_P4, p+4, 1);
   NRF_read_register(nrf, NRF_RX_PW_P5, p+5, 1);

   strcpy(s, "RX_PW_PX: ");

   for (i=0; i<6; i++)
   {
      sprintf(t, "P%d=%d ", i, p[i]);
      strcat(s, t);
   }

   return s;
}


char *NRF_format_FIFO_STATUS(nrf_p nrf, char *s)
{
   int v;
   char t[8];

   NRF_read_register(nrf, NRF_FIFO_STATUS, t, 1);

   v = t[0];

   strcpy(s, "NRF_FIFO_STATUS: ");

   if (v & NRF_FTX_REUSE) strcat(s, "TX reuse set, ");
   else               strcat(s, "TX reuse not set, ");

   if (v & NRF_FTX_FULL)       strcat(s, "TX FIFO full, ");
   else if (v & NRF_FTX_EMPTY) strcat(s, "TX FIFO empty, ");
   else                    strcat(s, "TX FIFO has data, ");

   if (v & NRF_FRX_FULL)       strcat(s, "RX FIFO full, ");
   else if (v & NRF_FRX_EMPTY) strcat(s, "RX FIFO empty");
   else                    strcat(s, "RX FIFO has data");

   return s;
}


char *NRF_format_DYNPD(nrf_p nrf, char *s)
{
   int i, v;
   char t[16];

   NRF_read_register(nrf, NRF_DYNPD, t, 1);

   v = t[0];

   strcpy(s, "NRF_DYNPD: ");

   for (i=0; i<6; i++)
   {
      if (v & (1<<i)) sprintf(t, "P%d:on ", i);
      else            sprintf(t, "P%d:off ", i);
      strcat(s, t);
   }

   return s;
}

char *NRF_format_FEATURE(nrf_p nrf, char *s)
{
   int v;
   char t[8];

   NRF_read_register(nrf, NRF_FEATURE, t, 1);

   v = t[0];

   strcpy(s, "NRF_FEATURE: ");

   if (v & NRF_EN_DPL) strcat(s, "Dynamic payload on, ");
   else            strcat(s, "Dynamic payload off, ");

   if (v & NRF_EN_ACK_PAY) strcat(s, "ACK payload on, ");
   else                strcat(s, "ACK payload off, ");

   if (v & NRF_EN_DYN_ACK) strcat(s, "W_TX_PAYLOAD_NOACK on");
   else                strcat(s, "W_TX_PAYLOAD_NOACK off");

   return s;
}

void NRF_show_registers(nrf_p nrf)
{
   char s[256];

   printf("%s\n", NRF_format_CONFIG(nrf, s));
   printf("%s\n", NRF_format_EN_AA(nrf, s));
   printf("%s\n", NRF_format_EN_RXADDR(nrf, s));
   printf("%s\n", NRF_format_SETUP_AW(nrf, s));
   printf("%s\n", NRF_format_SETUP_RETR(nrf, s));
   printf("%s\n", NRF_format_RF_CH(nrf, s));
   printf("%s\n", NRF_format_RF_SETUP(nrf, s));
   printf("%s\n", NRF_format_STATUS(nrf, s));
   printf("%s\n", NRF_format_OBSERVE_TX(nrf, s));
   printf("%s\n", NRF_format_RPD(nrf, s));
   printf("%s\n", NRF_format_RX_ADDR_PX(nrf, s));
   printf("%s\n", NRF_format_TX_ADDR(nrf, s));
   printf("%s\n", NRF_format_RX_PW_PX(nrf, s));
   printf("%s\n", NRF_format_FIFO_STATUS(nrf, s));
   printf("%s\n", NRF_format_DYNPD(nrf, s));
   printf("%s\n", NRF_format_FEATURE(nrf, s));
}

void NRF_set_defaults(nrf_p nrf)
{
   nrf->spi_channel=0;   // SPI channel
   nrf->spi_device=0;    // SPI device
   nrf->spi_speed=50e3;  // SPI bps
   nrf->mode=NRF_RX;     // primary mode (RX or TX)
   nrf->channel=1;       // radio channel
   nrf->payload=8;       // message size in bytes
   nrf->pad=32;          // value used to pad short messages
   nrf->address_bytes=5; // RX/TX address length in bytes
   nrf->crc_bytes=1;     // number of CRC bytes

   nrf->sbc=-1;          // sbc connection
   nrf->CE=-1;           // GPIO for chip enable
   nrf->spih=-1;         // SPI handle
   nrf->chip=-1;         // gpiochip handle
   nrf->PTX=-1;          // RX or TX
   nrf->CRC=-1;          // CRC bytes
}

void NRF_init(nrf_p nrf)
{
   char txBuf[256];

   nrf->chip = gpiochip_open(nrf->sbc, 0);

   gpio_claim_output(nrf->sbc, nrf->chip, 0, nrf->CE, 0);

   NRF_unset_CE(nrf);

   nrf->spih = spi_open(nrf->sbc,
      nrf->spi_channel, nrf->spi_device, nrf->spi_speed, 0);

   NRF_set_channel(nrf, nrf->channel);

   NRF_set_payload(nrf, nrf->payload);

   NRF_set_pad_value(nrf, nrf->pad);

   NRF_set_address_bytes(nrf, nrf->address_bytes);

   NRF_set_CRC_bytes(nrf, nrf->crc_bytes);

   nrf->PTX = 0;

   NRF_power_down(nrf);

   txBuf[0] = 0x1F;

   NRF_write_register(nrf, NRF_SETUP_RETR, txBuf, 1);

   NRF_flush_rx(nrf);
   NRF_flush_tx(nrf);

   NRF_power_up_rx(nrf);
}

void NRF_term(nrf_p nrf)
{
   NRF_power_down(nrf);

   spi_close(nrf->sbc, nrf->spih);

   gpio_free(nrf->sbc, nrf->chip, nrf->CE);

   gpiochip_close(nrf->sbc, nrf->chip);
}


char *test_words[] = {
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
"Clarence", "comes"};

int number_of_test_words = sizeof(test_words) / sizeof(char *);

int main(int argc, char *argv[])
{
   int sending;
   int sbc;
   int count;
   double end_time;
   char *ver = "r";
   char s[256];
   nrf_t nrf;

   if (argc > 1) sending = 1;
   else sending = 0;

   sbc = rgpiod_start(0,0);

   if (sbc < 0)
   {
      printf("can't connect to rgpiod\n");
      return -1;
   }

   NRF_set_defaults(&nrf);

   nrf.sbc = sbc;
   nrf.CE = 27;

   nrf.payload = NRF_ACK_PAYLOAD;
   nrf.pad = '*';
   nrf.address_bytes=3;
   nrf.crc_bytes = 2;

   NRF_init(&nrf);

   NRF_show_registers(&nrf);

   end_time = lgu_time() + 3600;

   if (sending)
   {
      count = 0;

      NRF_set_local_address(&nrf, "h1");
      NRF_set_remote_address(&nrf, "h2");

      while (lgu_time() < end_time)
      {
         //printf("%s\n", NRF_format_FIFO_STATUS(&nrf, s));
         //printf("%s\n", NRF_format_OBSERVE_TX(&nrf, s));

         if (!NRF_is_sending(&nrf))
         {
            printf("%s> %s\n", ver, test_words[count]);
            NRF_send(&nrf, test_words[count], strlen(test_words[count]));
            count += 1;
            if (count >= number_of_test_words) count = 0;
         }

         lgu_sleep(0.5);

      }
   }
   else
   {
      NRF_set_local_address(&nrf, "h2");
      NRF_set_remote_address(&nrf,"h1");

      while (lgu_time() < end_time)
      {
         //printf("%s\n", NRF_format_FIFO_STATUS(&nrf, s));
         //printf("%s\n", NRF_format_OBSERVE_TX(&nrf, s));

         while (NRF_data_ready(&nrf))
         {
            printf("%s< %s\n", ver, NRF_get_payload(&nrf, s));
         }
         lgu_sleep(0.5);
      }
   }

   NRF_term(&nrf);

   rgpiod_stop(sbc);

   return 0;
}

