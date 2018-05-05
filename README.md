Grayscale5110
=============

This Arduino code demonstrates how to produce grayscale images on a
monochrome Nokia5110 display. The Arduino code assumes a ESP8266
microcontroller.


Compiling
---------

First copy `secrets.hpp.in` to `secrets.hpp` and add your WiFi SSID
and password. Compilation can than be done with:

    $ make


Usage
-----

Once the ESP8266 has booted up and shows "Ready and Waiting", images
can be send to the display with:

    ./img2raw.py monalisa.png | nc 192.168.178.78 8080

