---
name: mcu-project
description: "Scaffold and build Keil MDK v6 / CMSIS-Solution projects: csolution.yml + cproject.yml, device/board selection, CMSIS packs (add components/layers), and build via CMSIS-Toolbox (cbuild) with CMake/Ninja and Arm Compiler. 嵌入式工程脚手架与构建：CMSIS-Solution 的 csolution/cproject 配置、选器件/板、加 CMSIS 包与组件、用 cbuild(CMake/Ninja) 构建。Triggers on: new project, scaffold project, build firmware, csolution, cproject, cbuild, cmsis pack, 新建工程, 创建工程, 工程脚手架, 构建工程, 编译固件, 加包, 选器件。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# mcu-project — CMSIS-Solution 工程脚手架与构建

## 何时用
- 新建一个 MDK6/CMSIS-Solution 工程，或为已有工程加器件包/组件/层。
- 用命令行构建（CI 或无 IDE 环境）。

## 步骤
1. **建结构**：用骨架 [templates/csolution.yml](templates/csolution.yml) 与
   [templates/cproject.yml](templates/cproject.yml)，填 `device:`（如 `STM32F407VGTx`）、
   `compiler: AC6`（或 GCC）、源文件分组、`packs:`。
2. **加 CMSIS 组件**：在 `cproject.yml` 的 `components:` 列出（如 `Device:Startup`、
   `CMSIS:CORE`、`CMSIS Driver:USART`…）；RTOS/驱动层用 `layers:`。
3. **解析与构建**（装了 CMSIS-Toolbox 时）：
   ```bash
   csolution list packs -s my.csolution.yml     # 检查依赖包
   cbuild my.csolution.yml --packs --update-rte  # 拉包、生成 RTE、CMake+Ninja 构建
   ```
   未装工具链则交付 yml + 说明用 Keil Studio(VS Code) 打开构建。
4. **产物**：`out/<context>/` 下的 `.elf/.hex/.bin` + `.map`。

## 注意
- `context` = `project.buildType+target`（如 `MyApp.Debug+STM32F407`）。
- 选 `Arm Compiler for Embedded (AC6)` 默认；需 GNU 改 `compiler: GCC`。
- 时钟/启动文件来自 Device 包；别手改 RTE 生成文件。

## 衔接
- 外设代码 → `mcu-peripheral`；RTOS → `mcu-rtos`；构建报错/HardFault → `mcu-debug`。
