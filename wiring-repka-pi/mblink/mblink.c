#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>
#include "wiringRP.h"

// Глобальные переменные и константы
const int LED_1 = 6;
const int LED_2 = 7;

// Функции для управления светодиодами в отдельных потоках
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
        delay(300); // Задержка для второго светодиода
        digitalWrite(LED_2, LOW);
        delay(150); // Задержка для второго светодиода
    }
    return NULL;
}

void setup() {
    // Инициализация библиотек wiringRP
    if (setupWiringRP(WRP_MODE_SUNXI) < 0)
        exit(EXIT_FAILURE);
    
    // Инициализация пользовательских объектов
    pinMode(LED_1, OUTPUT);
    pinMode(LED_2, OUTPUT);
    
    // Создание потоков для управления светодиодами
    pthread_t thread_led1, thread_led2;
    pthread_create(&thread_led1, NULL, led1_blink, NULL);
    pthread_create(&thread_led2, NULL, led2_blink, NULL);
}

void loop() {
    // Основной цикл программы
    // Ничего не делаем здесь, управление светодиодами происходит в отдельных потоках
}

ONDESTROY() {
    // Освобождение занятых ресурсов, выключение напряжения на пинах
    digitalWrite(LED_1, LOW);
    digitalWrite(LED_2, LOW);
    pinMode(LED_1, DISABLE);
    pinMode(LED_2, DISABLE);
    
    // Завершение работы библиотек
    releaseWiringRP();
    exit(0); // Выход из программы
}

MAIN_WIRINGRP();

