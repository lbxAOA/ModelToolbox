---
name: ltspice
description: "Simulate and analyze circuits with LTspice via the ltspice MCP: read/write .asc schematics, modify component values, set/read parameters and directives, run simulations (transient/AC/DC/op-point), and read back the operating point and waveforms. Part of the hardware (hw) domain, complements ato-design/kicad-mfg. 用 LTspice(经 ltspice MCP) 做电路仿真：读写 .asc 原理图、改元件值、设参数与仿真指令、跑瞬态/交流/直流/工作点、读回工作点与波形。Triggers on: ltspice, spice, circuit simulation, simulate circuit, transient, ac analysis, dc sweep, operating point, waveform, bode, 仿真, 电路仿真, ltspice仿真, spice仿真, 瞬态分析, 交流分析, 直流扫描, 工作点, 看波形, 频率响应, 扫参数。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# ltspice — 电路仿真（经 ltspice MCP）

所有操作经 **`ltspice` MCP**。工具映射见 [references/ltspice-mcp-map.md](references/ltspice-mcp-map.md)。

## 何时用
- 验证电路功能/性能：放大器、电源、滤波器、振荡器的瞬态/频响/工作点。
- 改元件值、扫参数、对比方案，读回波形与关键节点。

## 典型流程
1. **定位/读图**：`mcp__ltspice__list_schematics` 找到 `.asc`，
   `mcp__ltspice__read_schematic` 读结构（元件、网络、指令）。
2. **设置**：
   - 改元件值：`mcp__ltspice__modify_component`（如把 R1 改 4.7k）。
   - 参数/指令：`mcp__ltspice__write_parameters`（`.param`、`.tran`、`.ac`、`.dc`、`.step`）。
3. **运行**：`mcp__ltspice__run_simulation`。
4. **读结果**：
   - 工作点：`mcp__ltspice__read_op_point`（直流偏置、节点电压、器件电流）。
   - 波形：`mcp__ltspice__read_waveforms`（取节点/支路，分析幅值/相位/上升时间/纹波…）。
5. **迭代**：根据指标改值/扫参数再跑，记录对比。

## 分析类型速记
- `.tran <Tstop>` 瞬态；`.ac dec <N> <fstart> <fstop>` 交流(Bode)；
  `.dc <src> <start> <stop> <step>` 直流扫描；`.op` 工作点；
  `.step param X ...` 参数扫描；`.meas` 自动量取指标。

## 注意
- 先确认 MCP 指到正确 `.asc`；改图前可先 `read_schematic` 备份理解。
- AC 分析需要交流小信号源（`AC 1`）；瞬态看启动需设初始条件/`uic` 谨慎。
- 收敛问题：加 `.options`、给初值、缩小步长、检查悬空节点。

## 衔接（hw 域）
- 选型/拓扑来自 `ato-design`；仿真定参后回 `ato-design`/KiCad；
  PCB 校验出图 → `kicad-mfg`。
