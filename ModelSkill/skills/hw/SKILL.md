---
name: hw
description: "Orchestrator for embedded hardware / PCB design with atopile (code-defined circuits, .ato) + Quilter (AI placement & routing) on a KiCad backend. Routes to: .ato module authoring & part selection, ato build/BOM/KiCad sync, Quilter layout prep & retrieval, or KiCad validation (ERC/DRC) & manufacturing export. 硬件/PCB 设计总编排：atopile + quilter + KiCad，路由到 .ato 模块与选型、构建与BOM、Quilter 布局布线、KiCad 校验与制造输出。Triggers on: hardware, pcb, schematic, circuit board, electronics design, atopile, quilter, kicad, 硬件设计, 画板, 画pcb, 电路设计, 原理图, 电路板, layout, 布局布线, 制造文件。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# hw — 硬件 / PCB 设计编排

工具链：**atopile**（代码定义电路 `.ato`）→ **KiCad**（后端，原理图/网表/布局）→
**Quilter**（AI 布局布线）→ **KiCad** 出制造文件。

## 流程概览
```
ato-design (.ato 模块+选型)  →  ato-build (build/网表/BOM, 同步 KiCad)
   →  quilter-flow (准备约束/板框/预布局 → 上传 → 回收候选)
   →  kicad-mfg (ERC/DRC + 导出 Gerber/BOM/贴片/3D)
```

## 路由表（Intent → 子技能）
| 意图 | 子技能 |
|------|--------|
| 写 `.ato` 模块/接口、用约束自动选元件、引入现成模块 | `ato-design` |
| `ato build`、生成网表/BOM、与 KiCad 布局同步 | `ato-build` |
| 准备并上传 Quilter 自动布局布线、回收候选并对比 | `quilter-flow` |
| 跑 ERC/DRC、导出 Gerber/BOM/贴片/3D 投板 | `kicad-mfg` |
| 电路仿真（瞬态/交流/直流/工作点/波形） | `ltspice` |

## 转交其它技能
- 机械结构 / 外壳 / 标准件（螺丝、连接器、外壳）：转 `cad` / `step-parts` 技能。
- KiCad 操作统一经 `kicad-mcp-pro` MCP（见 `kicad-mfg`）。
