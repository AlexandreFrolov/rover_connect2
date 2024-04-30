#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>
#include "wiringRP.h"

const int LED_1 = 6;
const int LED_2 = 7;

void* led1_blink(void* arg) {
    while (true) {
        digitalWrite(LED_1, HIGH);
        delay(1000);
        digitalWrite(LED_1, LOW);
        delay(500);
    }
    return NULL;
}

void* led2_blink(void* arg) {
    while (true) {
        digitalWrite(LED_2, HIGH);
        delay(300);
        digitalWrite(LED_2, LOW);
        delay(150);
    }
    return NULL;
}

void setup() {
    if (setupWiringRP(WRP_MODE_SUNXI) < 0)
        exit(EXIT_FAILURE);
   
    pinMode(LED_1, OUTPUT);
    pinMode(LED_2, OUTPUT);
    
    pthread_t thread_led1, thread_led2;
    pthread_create(&thread_led1, NULL, led1_blink, NULL);
    pthread_create(&thread_led2, NULL, led2_blink, NULL);
}

void loop() {
    delay(300);
}

ONDESTROY() {
    digitalWrite(LED_1, LOW);
    digitalWrite(LED_2, LOW);
    pinMode(LED_1, DISABLE);
    pinMode(LED_2, DISABLE);
    releaseWiringRP();
    exit(0);
}

MAIN_WIRINGRP();

