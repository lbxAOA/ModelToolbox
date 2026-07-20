---
name: ato-build
description: "Build atopile projects and produce outputs: run `ato build` (compiles .ato, runs the parametric part picker, generates netlist + BOM), select build targets/entrypoints, and sync results into the KiCad layout (.kicad_pcb). Hands off to KiCad validation/manufacturing. atopile 构建与产物：ato build 编译选料、生成网表/BOM、选 target、与 KiCad 布局同步。Triggers on: ato build, build atopile, generate netlist, generate bom, 编译ato, 构建atopile, 生成网表, 生成bom, 网表, 物料清单, 同步布局, targets。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# ato-build — 构建·BOM·KiCad 联动

## 何时用
- 把 `.ato` 编译成网表/BOM，并把结果同步进 KiCad PCB。
- 选择构建目标(target)或不同入口(entry)。

## 步骤
1. 构建（已装 atopile 时，工程根目录）：
   ```bash
   ato build                      # 默认 targets
   ato build <ENTRY>              # 指定入口
   ato build --target <name>      # 指定目标（如 bom / netlist / layout）
   ```
   未装则交付 `.ato` + 说明（`pip install atopile` 或按官方装）。
2. **产物**：网表、BOM（料号/数量/封装）、更新后的 KiCad 布局文件。
3. **同步 KiCad**：atopile 原生写 KiCad 文件；新增/改动元件后回 KiCad 更新布局
   （未布的元件成新 footprint，待布局布线）。
4. 检查：BOM 是否有未选到的件（picker 失败）、封装是否齐全。

## 注意
- 选料失败常因 `assert` 约束太紧或库存——回 `ato-design` 放宽。
- 构建后元件位号/网络变化要回 KiCad 增量更新，别覆盖已有布局。

## 衔接
- 布局布线 → `quilter-flow`；ERC/DRC 与导出制造文件 → `kicad-mfg`。
