---
name: mcu-rtos
description: "Integrate and configure an RTOS on Cortex-M: Keil RTX5 (CMSIS-RTOS2) or FreeRTOS. Create tasks/threads, synchronization (semaphore/mutex/queue/event flags), timers, stack/heap sizing, priorities, and ISR-to-task signaling. 嵌入式 RTOS 集成：RTX5(CMSIS-RTOS2) 或 FreeRTOS，建任务、信号量/互斥量/队列/事件标志、定时器、栈堆与优先级、中断与任务通信。Triggers on: rtos, rtx5, rtx, freertos, cmsis-rtos2, task, thread, semaphore, mutex, queue, scheduler, 实时操作系统, 任务, 线程, 信号量, 互斥量, 消息队列, 调度, 创建任务。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# mcu-rtos — RTOS 集成（RTX5 / FreeRTOS）

## 何时用
- 需要多任务/抢占调度、任务间同步与通信、软件定时器。
- 在 CMSIS-Solution 工程里加 RTOS 层。

## 选型
- **RTX5（CMSIS-RTOS2）**：Keil 原生，组件 `CMSIS:RTOS2:Keil RTX5`，与 MDK/事件记录器
  集成好。骨架：[templates/rtx5/app_main.c](templates/rtx5/app_main.c)。
- **FreeRTOS**：最通用，可经 `CMSIS:RTOS2:FreeRTOS` 包或直接移植。
  骨架：[templates/freertos/app_main.c](templates/freertos/app_main.c)。

## 步骤
1. 在 `cproject.yml` 加 RTOS 组件/层（见 `mcu-project`）。
2. 设计任务表：每个任务的职责、优先级、栈大小、周期/事件。
3. 选同步原语：互斥(共享资源) / 信号量(事件计数) / 队列(数据) / 事件标志(多条件)。
4. ISR → 任务：在中断里用 `osSemaphoreRelease` / `xSemaphoreGiveFromISR` 通知任务。
5. 配置：时钟节拍(1ms 常用)、堆模型、空闲/定时器任务栈。

## 注意
- ISR 只能调用 `...FromISR`（FreeRTOS）或 RTOS 允许的 ISR-safe API。
- 栈不足是常见崩溃源：开栈溢出检测；用事件记录器/uxTaskGetStackHighWaterMark 调栈。
- 优先级反转：共享资源用带优先级继承的互斥量。
- 临界区短；别在持锁时阻塞。

## 衔接
- 外设驱动 → `mcu-peripheral`；崩溃/卡死 → `mcu-debug`。
