/* FreeRTOS 最小骨架：两个任务 + 一个由 ISR 释放的二值信号量 */
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

static SemaphoreHandle_t sem_evt;

static void task_blink(void *arg) {
  (void)arg;
  for (;;) {
    /* toggle LED */
    vTaskDelay(pdMS_TO_TICKS(500));
  }
}

static void task_worker(void *arg) {
  (void)arg;
  for (;;) {
    if (xSemaphoreTake(sem_evt, portMAX_DELAY) == pdTRUE) {
      /* 处理事件 */
    }
  }
}

/* 在外设 ISR 里：
   BaseType_t hpw = pdFALSE;
   xSemaphoreGiveFromISR(sem_evt, &hpw);
   portYIELD_FROM_ISR(hpw);
*/

int app_main(void) {
  sem_evt = xSemaphoreCreateBinary();
  xTaskCreate(task_blink,  "blink",  256, NULL, 2, NULL);
  xTaskCreate(task_worker, "worker", 512, NULL, 3, NULL);
  vTaskStartScheduler();         /* 不返回 */
  for (;;) {}
}
