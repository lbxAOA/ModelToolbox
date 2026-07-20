---
name: kicad-mfg
description: "Validate a KiCad board and export manufacturing files via the kicad-mcp-pro MCP: run ERC/DRC, then export Gerbers, drill, BOM, pick-and-place (CPL), 3D STEP, and PDFs. Also board summary, stackup, net statistics, DFM checks. 用 kicad-mcp-pro MCP 校验与出制造文件：跑 ERC/DRC，导出 Gerber/钻孔/BOM/贴片(CPL)/STEP/PDF，含板卡概览与 DFM。Triggers on: drc, erc, gerber, fabrication, manufacturing, pick and place, cpl, bom export, kicad, 制造文件, 投板, 导出gerber, 钻孔, 贴片文件, 校验, 跑drc, 跑erc, 出图。"
allowed-tools: Read, Bash, Grep, Glob
---

# kicad-mfg — KiCad 校验与制造输出（kicad-mcp-pro）

所有 KiCad 操作经 **`kicad-mcp-pro` MCP**。工具映射见
[references/kicad-mcp-map.md](references/kicad-mcp-map.md)。

## 起手
1. `mcp__kicad-mcp-pro__kicad_get_version` 确认服务可用。
2. `mcp__kicad-mcp-pro__kicad_set_project` 指定工程。
3. `mcp__kicad-mcp-pro__pcb_get_board_summary` 看层数/尺寸/元件/网络概览。

## 校验（投板前必做）
- 原理图：`run_erc`（电气规则，未连/冲突/缺电源符号）。
- PCB：`run_drc`（间距/线宽/孔径/环宽/未布线）。
- 进阶：`validate_design`、`get_unconnected_nets`、`get_courtyard_violations`、
  `get_silk_to_pad_violations`、DFM(`dfm_run_manufacturer_check`)。
- **目标：ERC/DRC 0 错**（豁免需记录理由）。

## 导出制造包
- `export_gerber` + `export_drill`（或一体的制造包变体）
- `export_bom`（物料）+ `export_pick_and_place`（贴片 CPL）
- `export_step` / `export_3d_step`（3D，给结构）
- `export_pcb_pdf` / `export_sch_pdf`（评审/存档）

## 流程位置
布局布线（`quilter-flow` 回收）之后、送厂之前。先校验、后导出。

## 注意
- 导出前确认叠层(`pcb_get_stackup`)、原点/钻孔参考、单位与厂商要求一致。
- 贴片文件坐标系/旋转需匹配厂商规范（必要时按厂商模板转换）。

## 衔接
- 机械/结构件 STEP 给 `cad`；BOM 选型回 `ato-design`；仿真 `ltspice`。
