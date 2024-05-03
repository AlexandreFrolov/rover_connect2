#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>
#include "wiringRP.h"
#include "event_gpio.h"
#include "devices/pca9685.h"

const int LED_1 = 6;
const int LED_2 = 7;
const int RELAY_1 = 9;
const int BUTTON_1 = 10;
bool LED_1_ON = false;
bool LED_2_ON = false;
pthread_t thread_led1, thread_led2, thread_servo1, thread_servo2, thread_servo3;

int pca9685_fd = 0;
const float HERTZ = 50.0f;
//const float HERTZ = 239.0f;

const int MAX_PWM = 4096;
const int pca9685Address = 0x40;

const int pin_1 = 0;
float degree_1 = 0.0f;
int dir_1 = 0;

const int pin_2 = 4;
float degree_2 = 0.0f;
int dir_2 = 0;

const int pin_3 = 8;


const int pin_4 = 12;
float degree_4 = 0.0f;
int dir_4 = 0;



void pushButton1(__u32 event, __u64 time);

int calcTicks(float impulseMs, float hertz) {
    float cycleMs = 1000.0f / hertz;
    return (int) ((float)MAX_PWM * impulseMs / cycleMs + 1.0f);
}

float mapf(float x, float in_min, float in_max, float out_min, float out_max) {
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void setNeutralPos() {
    float millis = 1.5f;
    int tick = calcTicks(millis, HERTZ);
    pca9685PwmWrite(pca9685_fd, pin_1, 0, tick);
    pca9685PwmWrite(pca9685_fd, pin_2, 0, tick);

    tick = calcTicks(1.56f, HERTZ);
	printf("tick for 1.56: %d\n", tick);
	pca9685PwmWrite(pca9685_fd, pin_3, 0, tick);
	
    tick = calcTicks(1.56f, HERTZ);
	printf("tick for 1.56 %d\n", tick);
	pca9685PwmWrite(pca9685_fd, pin_4, 0, tick);
	
}

void* led1_blink(void* arg) {
    pinMode(RELAY_1, OUTPUT);
    delay(100);
	digitalWrite(RELAY_1, HIGH);
	
    for (int i = 0; i < 3; ++i) {
        digitalWrite(LED_1, HIGH);
        delay(1000);
        digitalWrite(LED_1, LOW);
        delay(500);
    }
	digitalWrite(RELAY_1, LOW);
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

void* thread_servo1_rotate(void* arg) {
	while (degree_1 < 180) {
		float millis = mapf(degree_1, 0.0f, 180.0f, 0.5f, 2.5f);
		printf("degree_1: %.2f, millis: %.2f\n", degree_1, millis);
		int tick = calcTicks(millis, HERTZ);
		printf("tick: %d\n", tick);
		pca9685PwmWrite(pca9685_fd, pin_1, 0, tick);
		delayMicroseconds(50);
		
		degree_1 += dir_1 == 1 ? 0.1f : -0.1f;
		
		if (degree_1 > 180) {
			degree_1 = 180;
			dir_1 = 0;
		} else if (degree_1 < 0) {
			degree_1 = 0;
			dir_1 = 1;
		}
	}
	degree_1 = 0;
    pthread_exit(NULL);
}

void* thread_servo2_rotate(void* arg) {
	delay(2000);
	while (degree_2 < 180) {
		float millis = mapf(degree_2, 0.0f, 180.0f, 0.5f, 2.5f);
		printf("degree_2: %.2f, millis: %.2f\n", degree_2, millis);
		int tick = calcTicks(millis, HERTZ);
		printf("tick: %d\n", tick);
		pca9685PwmWrite(pca9685_fd, pin_2, 0, tick);
		delayMicroseconds(50);
		
		degree_2 += dir_2 == 1 ? 0.1f : -0.1f;
		
		if (degree_2 > 180) {
			degree_2 = 180;
			dir_2 = 0;
		} else if (degree_2 < 0) {
			degree_2 = 0;
			dir_2 = 1;
		}
	}
	degree_2 = 0;
    pthread_exit(NULL);
}

void* thread_servo3_rotate(void* arg) {
	int tick;
	delay(1000);
	
	for (int i = 0; i < 3; ++i) {	
		tick = calcTicks(1.0f, HERTZ);
		pca9685PwmWrite(pca9685_fd, pin_3, 0, tick);
		delay(2000);
		tick = calcTicks(2.0f, HERTZ);
		pca9685PwmWrite(pca9685_fd, pin_3, 0, tick);
		delay(2000);
		tick = calcTicks(1.6f, HERTZ);
		pca9685PwmWrite(pca9685_fd, pin_3, 0, tick);
	}
    pthread_exit(NULL);
}

void pushButton1(__u32 event, __u64 time) {
    printf("Button 1 - is %s, timestamp: %lld\n", event == 1 ? "RISING" : "FALLING", time);
    delay(100);
	
    if(event && digitalRead(BUTTON_1)) {		
      pthread_create(&thread_led1, NULL, led1_blink, NULL);
	  pthread_create(&thread_led2, NULL, led2_blink, NULL);
	  pthread_create(&thread_servo1, NULL, thread_servo1_rotate, NULL);
	  pthread_create(&thread_servo2, NULL, thread_servo2_rotate, NULL);
	  pthread_create(&thread_servo3, NULL, thread_servo3_rotate, NULL);
	}
}

void setup() {
    if (setupWiringRP(WRP_MODE_SUNXI) < 0)
        exit(EXIT_FAILURE);
    pinMode(LED_1, OUTPUT);
    pinMode(LED_2, OUTPUT);
	pinMode(BUTTON_1, INPUT_PULLUP);
	interruptCreate(BUTTON_1, pushButton1);
	
	pca9685_fd = pca9685Setup(I2C1_BUS, pca9685Address, HERTZ);
    if (pca9685_fd < 0)
        exit(EXIT_FAILURE);
    pca9685PwmReset(pca9685_fd);
    setNeutralPos();
    delay(1000);	
}

void loop() {
  delay(100);
}

ONDESTROY() {
	setNeutralPos();
    delay(100);
    pca9685PwmReset(pca9685_fd);
    pca9685Release(pca9685_fd);
	
    digitalWrite(LED_1, LOW);
    digitalWrite(LED_2, LOW);
	digitalWrite(RELAY_1, HIGH);
    pinMode(LED_1, DISABLE);
    pinMode(LED_2, DISABLE);
    pinMode(RELAY_1, DISABLE);
	pinMode(BUTTON_1, DISABLE);
	interruptStopAll();
    releaseWiringRP();
    exit(0);
}

MAIN_WIRINGRP();
