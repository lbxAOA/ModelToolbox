/* RTX5 / CMSIS-RTOS2 最小骨架：两个任务 + 一个由 ISR 释放的信号量 */
#include "cmsis_os2.h"

static osSemaphoreId_t sem_evt;

/* 周期任务 */
static void task_blink(void *arg) {
  (void)arg;
  for (;;) {
    /* toggle LED */
    osDelay(500);                 /* ms（osKernelGetTickFreq 默认 1000Hz） */
  }
}

/* 事件任务：等 ISR 通知 */
static void task_worker(void *arg) {
  (void)arg;
  for (;;) {
    if (osSemaphoreAcquire(sem_evt, osWaitForever) == osOK) {
      /* 处理事件 */
    }
  }
}

/* 在外设中断里调用：osSemaphoreRelease(sem_evt); */

int app_main(void) {
  osKernelInitialize();
  sem_evt = osSemaphoreNew(1, 0, NULL);
  osThreadNew(task_blink,  NULL, &(osThreadAttr_t){ .priority = osPriorityNormal });
  osThreadNew(task_worker, NULL, &(osThreadAttr_t){ .priority = osPriorityAboveNormal });
  osKernelStart();               /* 不返回 */
  for (;;) {}
}
