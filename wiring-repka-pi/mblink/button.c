#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "wiringRP.h"

const int LED_1 = 6;
const int LED_2 = 7;
const int BUTTON_1 = 10;

void setup() {
    if(setupWiringRP(WRP_MODE_SUNXI) < 0)
        exit(EXIT_FAILURE);
    pinMode(LED_1, OUTPUT);
	pinMode(LED_2, OUTPUT);
	pinMode(BUTTON_1, INPUT_PULLUP);
}

void loop() {
	if (digitalRead(BUTTON_1)) {
        delay(100);
        if (digitalRead(BUTTON_1)) {
            digitalWrite(LED_1, HIGH);
			digitalWrite(LED_2, LOW);
        }
    } else {
        digitalWrite(LED_1, LOW);
        digitalWrite(LED_2, HIGH);
    }	
}

ONDESTROY(){
    digitalWrite(LED_1, LOW);
    pinMode(LED_1, DISABLE);
	pinMode(LED_2, DISABLE);
	pinMode(BUTTON_1, DISABLE);
    releaseWiringRP();
    exit(0);
}

MAIN_WIRINGRP();
