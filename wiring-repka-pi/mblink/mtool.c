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
pthread_t thread_led1, thread_led2;

int pca9685_fd = 0;
const float HERTZ = 50.0f;
const int MAX_PWM = 4096;
const int pca9685Address = 0x40;
const int pin_x = 15;
float degree_x = 0.0f;
int dir_x = 1;
const int pin_y = 4;
float degree_y = 50.0f;
int dir_y = 1;
const int pin_z = 0;
float degree_z = 120.0f;
int dir_z = 0;

void pushButton1(__u32 event, __u64 time);

/**
 * Calculate the number of ticks the signal should be high for the required amount of time
 */
int calcTicks(float impulseMs, float hertz) {
    float cycleMs = 1000.0f / hertz;
    return (int) ((float)MAX_PWM * impulseMs / cycleMs + 0.5f);
}
float mapf(float x, float in_min, float in_max, float out_min, float out_max) {
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}
void setNeutralPos() {
    // Set servo to neutral position at 1.5 milliseconds
    // (View http://en.wikipedia.org/wiki/Servo_control#Pulse_duration)
    float millis = 1.5f;
    int tick = calcTicks(millis, HERTZ);
    pca9685PwmWrite(pca9685_fd, pin_x, 0, tick);
    pca9685PwmWrite(pca9685_fd, pin_y, 0, tick);
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
	
	pca9685_fd = pca9685Setup(I2C1_BUS, pca9685Address, HERTZ);
    if (pca9685_fd < 0)
        exit(EXIT_FAILURE);
    pca9685PwmReset(pca9685_fd);
    setNeutralPos();
    delay(1000);	
}

void moveToX() {
    float millis = mapf(degree_x, 0.0f, 180.0f, 0.5f, 2.5f);
    printf("degree_x: %.2f, millis: %.2f\n", degree_x, millis);
    int tick = calcTicks(millis, HERTZ);
    printf("tick: %d\n", tick);
    pca9685PwmWrite(pca9685_fd, pin_x, 0, tick);
    delayMicroseconds(50);
    degree_x += dir_x == 1 ? 0.1f : -0.1f;
    if (degree_x > 180) {
        degree_x = 180;
        dir_x = 0;
    } else if (degree_x < 0) {
        degree_x = 0;
        dir_x = 1;
    }
}
void moveToY() {
    float millis = mapf(degree_y, 0.0f, 180.0f, 0.5f, 2.5f);
    printf("degree_y: %.2f, millis: %.2f\n", degree_y, millis);
    int tick = calcTicks(millis, HERTZ);
    printf("tick: %d\n", tick);
    pca9685PwmWrite(pca9685_fd, pin_y, 0, tick);
    delayMicroseconds(50);
    degree_y += dir_y == 1 ? 0.1f : -0.1f;
    if (degree_y > 110) {
        degree_y = 110;
        dir_y = 0;
    } else if (degree_y < 60) {
        degree_y = 60;
        dir_y = 1;
    }
}

void moveToZ() {
    float millis = mapf(degree_z, 0.0f, 180.0f, 0.5f, 2.5f);
    printf("degree_z: %.2f, millis: %.2f\n", degree_z, millis);
    int tick = calcTicks(millis, HERTZ);
    printf("tick: %d\n", tick);
    pca9685PwmWrite(pca9685_fd, pin_z, 0, tick);
    delayMicroseconds(50);
    degree_z += dir_z == 1 ? 0.1f : -0.1f;
    if (degree_z > 180) {
        degree_z = 180;
        dir_z = 0;
    } else if (degree_z < 120) {
        degree_z = 120;
        dir_z = 1;
    }
}

void loop() {
    moveToX();
    moveToY();
    moveToZ();	
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
