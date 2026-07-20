---
name: quilter-flow
description: "Prepare a KiCad board for Quilter's AI placement & routing and bring results back. Quilter is a file-based web workflow (no public CLI): set the board outline, pre-place connectors/critical parts, define constraints (layers, net classes, keepouts, the critical 20%), upload, then retrieve and compare candidate layouts and DRC them in KiCad. Quilter 布局布线准备与回收：板框、预布局、约束(层/网类/禁布/关键20%)，上传 Quilter，回收候选并在 KiCad 跑 DRC 对比。Triggers on: quilter, auto place, auto route, autorouter, ai layout, 自动布局, 自动布线, 布局布线, 上传布线, 回收布局, 布线候选, 板框约束。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# quilter-flow — Quilter 布局布线准备与回收

Quilter 是**物理驱动的 AI 布局布线**，**基于文件的网页流程**（无公开 CLI/API）：
你在 KiCad 准备好工程 → 上传 → Quilter 返回**多个候选布局**（同格式）→ 回 KiCad
跑 DRC/收尾/投板。本技能负责**KiCad 侧准备 + 上传指引 + 结果回收**。

## 准备清单（见 [references/quilter-prep.md](references/quilter-prep.md)）
1. 原理图/网表完整（先 `ato-build` + `kicad-mfg` 的 ERC 过）。
2. **板框 (Edge.Cuts)** 画好、尺寸/安装孔确定。
3. **预布局**：连接器、按键、定位件等"位置固定"的元件先摆好并锁定。
4. **约束**：层叠(层数)、网类(电源/差分/高速)、线宽/间距、禁布区(keepout)、
   高度限制；标出你想自己控制的"关键 20%"(高速总线/敏感模拟/电源)。
5. （混合流程）关键 20% 自己预布线，其余 80% 交 Quilter。

## 上传与回收
- 上传：KiCad 工程（Quilter 读写原生 KiCad/Altium/Allegro/Xpedition）。
- 回收：拿回若干候选 → 在 KiCad 打开**逐个对比**（走线长度、过孔数、层使用、间距裕量）。
- 选定后回 KiCad 收尾。

## 衔接
- 准备前的网表/BOM → `ato-build`；回收后 **必做 DRC** 与导出制造文件 → `kicad-mfg`。

## 注意
- 无法在本地"自动上传/下载"Quilter——按其网页流程操作；本技能给清单与检查点。
- 上传前确保 ERC 干净、封装齐全，否则布局无意义。
