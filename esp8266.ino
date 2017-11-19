// Copyright (C) 2017 Ingo Ruhnke <grumbel@gmail.com>
//
// This software is provided 'as-is', without any express or implied
// warranty.  In no event will the authors be held liable for any damages
// arising from the use of this software.
//
// Permission is granted to anyone to use this software for any purpose,
// including commercial applications, and to alter it and redistribute it
// freely, subject to the following restrictions:
//
// 1. The origin of this software must not be misrepresented; you must not
//    claim that you wrote the original software. If you use this software
//    in a product, an acknowledgment in the product documentation would be
//    appreciated but is not required.
// 2. Altered source versions must be plainly marked as such, and must not be
//    misrepresented as being the original software.
// 3. This notice may not be removed or altered from any source distribution.

#include <ESP8266WiFi.h>

#include "password.hpp"

WiFiServer server(8080);

#define PIN_SCE   D7 // Chip Select
#define PIN_RESET D6 // Reset
#define PIN_DC    D5 // Mode Select
#define PIN_SDIN  D4 // Data In
#define PIN_SCLK  D3 // Clock

#define LCD_C     LOW
#define LCD_D     HIGH

#define LCD_W     84
#define LCD_H     48

void LcdWrite(byte dc, byte data)
{
  digitalWrite(PIN_DC, dc);
  digitalWrite(PIN_SCE, LOW);
  shiftOut(PIN_SDIN, PIN_SCLK, MSBFIRST, data);
  digitalWrite(PIN_SCE, HIGH);
}

void LcdInitialise(void)
{
  pinMode(PIN_SCE, OUTPUT);
  pinMode(PIN_RESET, OUTPUT);
  pinMode(PIN_DC, OUTPUT);
  pinMode(PIN_SDIN, OUTPUT);
  pinMode(PIN_SCLK, OUTPUT);

  digitalWrite(PIN_RESET, LOW);
  digitalWrite(PIN_RESET, HIGH);

  // See page 14 of https://sparkfun.com/datasheets/LCD/Monochrome/Nokia5110.pdf
  LcdWrite(LCD_C, 0b100001 );  // LCD Extended Commands.
  LcdWrite(LCD_C, 0b10111000 );  // Set LCD Vop (Contrast).
  LcdWrite(LCD_C, 0b110 );  // Set Temp coefficent. //0x04
  LcdWrite(LCD_C, 0x14);  // LCD bias mode 1:48. //0x13
  LcdWrite(LCD_C, 0b100010 );  // LCD Basic Commands
  LcdWrite(LCD_C, 0b1101 );  // LCD in normal mode.
}

void setup()
{
  LcdInitialise();

  Serial.begin(115200);
  delay(10);

  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

byte g_bitmap[504 * 32];
size_t g_bitmap_len = 0;

void send_bitmap()
{
  // move cursor to 0,0
  LcdWrite(LCD_C, 0b01000000);  // X
  LcdWrite(LCD_C, 0b10000000);  // Y

  // write data to LCD
  digitalWrite(PIN_DC, LCD_D);
  digitalWrite(PIN_SCE, LOW);

  for(int i = 0; i < g_bitmap_len; ++i)
  {
    shiftOut(PIN_SDIN, PIN_SCLK, MSBFIRST, g_bitmap[i]);
  }

  digitalWrite(PIN_SCE, HIGH);
}

void loop()
{
  WiFiClient client = server.available();
  if (client)
  {
    while (client.connected())
    {
      if (client.available())
      {
        g_bitmap_len = client.readBytes(g_bitmap, sizeof(g_bitmap));
        client.stop();
      }
    }
  }

  send_bitmap();
}

/* EOF */
