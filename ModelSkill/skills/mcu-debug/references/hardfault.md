# HardFault 排查速查（Cortex-M）

## 一、立即看的寄存器
- `SCB->CFSR` (0xE000ED28)：配置故障状态
  - UsageFault 高半字：`DIVBYZERO`(除零)、`UNALIGNED`(未对齐)、`INVSTATE`(非法状态/丢 Thumb 位)、`UNDEFINSTR`。
  - BusFault 中半字：`PRECISERR`(精确总线错，`BFAR` 有效)、`IMPRECISERR`(不精确)、`IBUSERR`。
  - MemManage 低半字：`DACCVIOL`/`IACCVIOL`(访问越权)，`MMARVALID` 时 `MMFAR` 有效。
- `SCB->HFSR`：`FORCED`=由可配置故障升级而来 → 回看 CFSR。
- `SCB->BFAR` / `SCB->MMFAR`：出错访问的地址（对应 VALID 位有效时）。

## 二、取压栈帧（定位 PC）
进入 HardFault 时硬件压栈 {R0-R3, R12, LR, PC, xPSR}。用如下处理函数打印：
```c
void HardFault_Handler(void) {
  __asm volatile (
    "tst lr, #4        \n"   // 判断用 MSP 还是 PSP
    "ite eq            \n"
    "mrseq r0, msp     \n"
    "mrsne r0, psp     \n"
    "b hardfault_report\n");
}
void hardfault_report(uint32_t *sp) {
  uint32_t pc = sp[6], lr = sp[5], psr = sp[7];
  volatile uint32_t cfsr = SCB->CFSR, hfsr = SCB->HFSR;
  volatile uint32_t bfar = SCB->BFAR, mmfar = SCB->MMFAR;
  (void)pc;(void)lr;(void)psr;(void)cfsr;(void)hfsr;(void)bfar;(void)mmfar;
  __asm("bkpt #0");           // 在调试器里看这些值
}
```
拿 `pc` 去 `.map`/反汇编（`fromelf --disassemble` 或 `arm-none-eabi-objdump -d`）定位函数与行。

## 三、高频根因对照
| 现象/寄存器 | 可能原因 |
|-------------|----------|
| UNALIGNED | 强转指针后非对齐访问、打包结构体 |
| DIVBYZERO | 除以运行时 0（开了 DIV_0_TRP） |
| INVSTATE  | 函数指针/中断向量丢失 Thumb 位、跳到数据区 |
| PRECISERR + BFAR=外设地址 | 访问未开时钟/不存在的外设 |
| DACCVIOL  | 空指针/野指针写、栈溢出冲掉相邻区 |
| 随机跑飞 | 栈溢出、缓冲区越界、未初始化指针 |

## 四、栈溢出快速判断
- RTOS：开 `configCHECK_FOR_STACK_OVERFLOW`，看 `uxTaskGetStackHighWaterMark`。
- 裸机：在栈尾填魔术字，运行后检查是否被覆盖；调大 `.map` 里的 Stack_Size。
