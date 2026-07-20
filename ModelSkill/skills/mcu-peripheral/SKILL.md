---
name: mcu-peripheral
description: "Write and configure MCU peripheral drivers/init code: GPIO, UART/USART, SPI, I2C, ADC, Timer/PWM, DMA, EXTI/NVIC, and the clock tree. Platform-agnostic skeletons (HAL/LL or bare register) with a per-peripheral configuration & timing checklist; asks for the MCU/datasheet to fill register details. 外设驱动/初始化：GPIO/UART/SPI/I2C/ADC/定时器PWM/DMA/中断/时钟树，平台无关骨架+配置时序清单。Triggers on: driver, peripheral, gpio, uart, usart, spi, i2c, adc, timer, pwm, dma, interrupt, nvic, clock tree, 写驱动, 外设, 外设配置, 串口, 时钟树, 定时器, 中断配置, 寄存器配置。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# mcu-peripheral — 外设驱动与配置

## 何时用
- 要写某个外设的初始化/驱动（GPIO/UART/SPI/I2C/ADC/TIM/DMA…）。
- 配置时钟树、中断(NVIC/EXTI)、DMA 搬运。

## 步骤
1. **明确目标**：MCU 型号 + 外设 + 引脚 + 期望参数（波特率/采样率/PWM 频率…）。
   缺型号先问；以 datasheet/参考手册寄存器为准。
2. **选层**：厂商 HAL（快、可移植）/ LL（轻量）/ CMSIS 寄存器裸机（最透明）。
3. **按外设清单配置**：见 [references/peripherals.md](references/peripherals.md)
   （每个外设的"时钟使能 → 引脚复用 → 参数 → 中断/DMA → 使能"五步 + 易错点）。
4. **封装**：`xxx_init()` + 读写/收发 API；返回状态码；加超时，不死等。
5. **验证**：先点灯/回环自测，再接外设；必要时转 `mcu-debug`。

## 通用范式（寄存器层）
```c
RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;   // 1. 开时钟
/* 2. 配置模式/复用/速度/上下拉 */       // GPIOA->MODER/AFR/OSPEEDR/PUPDR
/* 3. 配置外设寄存器参数 */
/* 4. (可选) 配 NVIC/DMA */
/* 5. 使能外设 */
```

## 注意
- 改外设前**先开对应总线时钟**（最常见 bug）。
- 引脚复用功能号(AF)查数据手册；5V 容忍、上拉电阻按需。
- ISR 短小：置标志/搬数据，重活留主循环或 RTOS 任务。

## 衔接
- 用 RTOS 调度 → `mcu-rtos`；工程/构建 → `mcu-project`；排错 → `mcu-debug`。
