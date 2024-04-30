#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>
#include "wiringRP.h"
#include "event_gpio.h"

const int LED_1 = 6;
const int LED_2 = 7;
const int BUTTON_1 = 10;
bool LED_1_ON = false;
bool LED_2_ON = false;
pthread_t thread_led1, thread_led2;

void pushButton1(__u32 event, __u64 time);

void* led1_blink(void* arg) {
    for (int i = 0; i < 3; ++i) {
        digitalWrite(LED_1, HIGH);
        delay(1000);
        digitalWrite(LED_1, LOW);
        delay(500);
    }
    pthread_exit(NULL);
}

void* led2_blink(void* arg) {
    for (int i = 0; i < 5; ++i) {
        digitalWrite(LED_2, HIGH);
        delay(300);
        digitalWrite(LED_2, LOW);
        delay(150);
    }
    pthread_exit(NULL);
}

void pushButton1(__u32 event, __u64 time) {
    printf("Button 1 - is %s, timestamp: %lld\n", event == 1 ? "RISING" : "FALLING", time);
    delay(100);
	
    if(event && digitalRead(BUTTON_1)) {		
      pthread_create(&thread_led1, NULL, led1_blink, NULL);
	  pthread_create(&thread_led2, NULL, led2_blink, NULL);
	}
}

void setup() {
    if (setupWiringRP(WRP_MODE_SUNXI) < 0)
        exit(EXIT_FAILURE);
    pinMode(LED_1, OUTPUT);
    pinMode(LED_2, OUTPUT);
	pinMode(BUTTON_1, INPUT_PULLUP);
	interruptCreate(BUTTON_1, pushButton1);
}

void loop() {
	delay(50);
}

ONDESTROY() {
    digitalWrite(LED_1, LOW);
    digitalWrite(LED_2, LOW);
    pinMode(LED_1, DISABLE);
    pinMode(LED_2, DISABLE);
	pinMode(BUTTON_1, DISABLE);
	interruptStopAll();
    releaseWiringRP();
    exit(0);
}

MAIN_WIRINGRP();
