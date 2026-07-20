---
name: mcu
description: "Orchestrator for embedded firmware on Arm Cortex-M with Keil MDK v6 / CMSIS-Solution (csolution) projects, CMSIS-Toolbox + CMake/Ninja, Arm Compiler. Platform-agnostic (STM32/GD32/NXP/Nordic…). Routes to: project scaffolding & build, peripheral drivers, RTOS integration, or debugging & review. 嵌入式固件总编排：MDK6/CMSIS-Solution 工程，平台无关，路由到工程脚手架、外设驱动、RTOS、调试与代码审查。Triggers on: embedded, firmware, microcontroller, mcu, cortex-m, keil, mdk, cmsis, 嵌入式, 单片机, 固件, 下位机, 微控制器, 写程序烧录, stm32, gd32。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# mcu — 嵌入式固件编排

工具链语境：**Keil MDK v6 / CMSIS-Solution**（`*.csolution.yml` + `*.cproject.yml`），
CMSIS-Toolbox 用 CMake/Ninja 后端，Arm Compiler for Embedded（或 Arm GNU）。

## 0. 先确认目标（平台无关，按需问）
- **MCU 型号**（如 STM32F4 / GD32F3 / nRF52…）——决定寄存器/外设细节。
- **抽象层**：厂商 HAL/LL、CMSIS 寄存器裸机，还是用 RTOS。

## 路由表（Intent → 子技能）
| 意图 | 子技能 |
|------|--------|
| 新建/配置 CMSIS-Solution 工程、构建、加包 | `mcu-project` |
| 写外设驱动/初始化（GPIO/UART/SPI/I2C/ADC/TIM/DMA） | `mcu-peripheral` |
| 集成/配置 RTOS（RTX5 / FreeRTOS） | `mcu-rtos` |
| 调试、HardFault、map 分析、代码审查 | `mcu-debug` |

## 通用约定
- 代码风格：C11，`stdint.h` 定宽类型；寄存器操作加 `volatile`；中断短、不阻塞。
- 可移植：外设访问尽量经 CMSIS/HAL 抽象；板级配置集中到 `board.h`。
- 安全：检查返回值/超时；ISR 里不调用阻塞或非可重入函数。
