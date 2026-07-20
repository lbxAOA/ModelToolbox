---
name: mcu-debug
description: "Debug and review embedded firmware: diagnose HardFault/lockups by decoding fault registers and the stacked frame, analyze the .map (size, sections, stack/heap), set up CMSIS-Debugger / SWO / Event Recorder, and review C for embedded pitfalls (volatile, ISR safety, MISRA-style). 嵌入式调试与代码审查：HardFault/死机定位(故障寄存器+压栈帧)、map 文件分析、调试器/SWO 配置、嵌入式代码评审。Triggers on: debug, hardfault, hard fault, crash, lockup, fault, map file, swo, code review, misra, 调试, 死机, 卡死, 跑飞, hardfault, 故障定位, map分析, 代码审查, 内存溢出。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# mcu-debug — 调试与代码审查

## HardFault / 死机定位
见 [references/hardfault.md](references/hardfault.md)。要点：
1. 读 `SCB->CFSR`/`HFSR`/`BFAR`/`MMFAR` 看故障类型与出错地址。
2. 从压栈帧取 **PC/LR**，配 `.map`/反汇编定位出事函数。
3. 常见因：空指针/野指针、数组越界、栈溢出、未对齐访问、除零、
   非法外设访问(没开时钟)、ISR 优先级/重入。

## .map 分析
- 看各 section(`.text/.data/.bss`) 大小、Flash/RAM 占用、是否超容量。
- 查最大栈/堆配置是否够；找意外的大型静态对象。

## 调试环境
- CMSIS-Debugger（VS Code）或 µVision；SWD + SWO 打印/ITM；
  Event Recorder 观察 RTOS 调度与事件。

## 代码审查清单
- `volatile`：寄存器、ISR 与主程序共享变量、忙等标志。
- 并发：临界区保护共享数据；ISR 只调 ISR-safe API。
- 资源：缓冲区边界、返回值/超时检查、无动态分配(或受控)。
- 可移植/规范：定宽类型、避免未定义行为、MISRA-C 风格（无隐式窄化、单一退出按需）。

## 衔接
- 外设相关问题 → `mcu-peripheral`；RTOS 卡死/栈溢出 → `mcu-rtos`；
  构建/容量问题 → `mcu-project`。
