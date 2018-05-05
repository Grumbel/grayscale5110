ARDUINO_HOME=/home/ingo/run/arduino-1.8.3
ARDUINO=${ARDUINO_HOME}/arduino
SOURCE=grayscale5110.ino
OPTS=--board esp8266:esp8266:d1_mini \
     --pref custom_build.f_cpu=160000000L \
     --pref custom_upload.speed=921600 \
     --verbose \

compile:
	${ARDUINO} --verify ${OPTS} ${SOURCE}

upload:
	${ARDUINO} --upload ${OPTS} ${SOURCE}

.PHONY: compile upload

# EOF #
