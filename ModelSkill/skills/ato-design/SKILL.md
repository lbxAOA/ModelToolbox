---
name: ato-design
description: "Author atopile circuits in the .ato language: define modules and interfaces, instantiate components with `new`, wire with ~ / ~>, set parameters with values+units, and let the parametric picker choose real parts from `assert` constraints. Reuse modules via `ato add` and `ato create component`. 用 .ato 语言写电路：模块/接口、new 实例化、~ 连接、参数+单位、assert 约束自动选元件、ato add 引入现成模块。Triggers on: atopile, ato, .ato, write module, component selection, part picker, 写ato, ato模块, atopile模块, 选型, 约束选元件, 元件选择, 接口模块, 电路代码。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# ato-design — atopile 模块编写与选型

代码定义电路。语法速查见 [references/ato-cheatsheet.md](references/ato-cheatsheet.md)。

## 何时用
- 新建/编写 `.ato` 模块（电源、传感器接口、MCU 外围…）。
- 用 `assert` 约束让编译器自动选具体元件（阻容、稳压器等）。
- 复用社区模块（[packages.atopile.io](https://packages.atopile.io)）。

## 步骤
1. 新建工程/组件（已装 atopile 时）：
   ```bash
   ato create            # 新工程
   ato create component  # 新组件骨架
   ato add <package>     # 引入现成模块（如电源、连接器）
   ```
2. 写模块：`module`/`interface`、`new` 实例化、`~`(直连)/`~>`(串联桥接)连接；
   参数带单位（`3.3V`、`10kohm`、`100nF`）。
3. 选型约束：用 `assert` 给容差/电压/封装范围，编译时自动 pick 真实料号。
4. 校验思路：先让结构/连接清晰、接口可复用，再交 `ato-build` 编译选料。

## 注意
- `.ato` 是**声明式**：无副作用、无过程式执行；重在结构与约束。
- 选型受 `assert` 约束 + 可用库存影响；约束太紧会选不到件。
- 引脚/接口命名清晰，方便 `~>` 串联与复用。

## 衔接
- 编译/出 BOM/同步 KiCad → `ato-build`；布线 → `quilter-flow`；制造 → `kicad-mfg`。
