# ltspice MCP 工具映射

> 工具名前缀 `mcp__ltspice__`。典型顺序：list → read → modify/write → run → read 结果。

## 读取 / 定位
- `list_schematics` —— 列出可用的 `.asc` 原理图。
- `read_schematic` —— 读某张图的结构（元件、网络、仿真指令）。
- `read_parameters` —— 读当前 `.param` / 指令参数。
- `read_op_point` —— 读上次仿真的直流工作点（节点电压、器件电流）。
- `read_waveforms` —— 读仿真波形数据（按节点/支路取序列）。

## 修改 / 设置
- `modify_component` —— 改某元件的值/型号（如 R、C、L、源、模型）。
- `write_parameters` —— 写 `.param` 与仿真指令（`.tran`/`.ac`/`.dc`/`.step`/`.meas`）。
- `write_schematic` —— 写回/新建 `.asc`（结构性改动时）。

## 运行
- `run_simulation` —— 运行 LTspice 仿真，产生 `.raw` 结果供读取。

## 常用指令(directives) 速查
| 目的 | 指令示例 |
|------|----------|
| 瞬态 | `.tran 0 5m 0 1u` |
| 交流(Bode) | `.ac dec 100 1 10Meg` |
| 直流扫描 | `.dc V1 0 5 0.01` |
| 工作点 | `.op` |
| 参数扫描 | `.step param R 1k 10k 1k` |
| 自动量取 | `.meas TRAN vpp PP V(out)` |
| 选项/收敛 | `.options reltol=1e-4 gmin=1e-12` |

## 排错
- 不收敛：给初值/`.ic`、加 `gmin`、减步长、检查悬空网络。
- AC 无响应：源要带 `AC 1` 小信号幅值。
- 找不到图：先 `list_schematics` 确认路径/活动工程。
