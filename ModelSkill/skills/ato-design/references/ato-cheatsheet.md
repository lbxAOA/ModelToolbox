# atopile (.ato) 语法速查

> 声明式 DSL，Python 风格但**无过程式执行/副作用**。重在结构、连接、参数约束。

## 模块与组件
```ato
import Resistor, Capacitor
from "generics/interfaces.ato" import Power

module VoltageDivider:
    power = new Power            # 接口实例
    r_top = new Resistor
    r_bot = new Resistor
    r_top.resistance = 10kohm +/- 5%
    r_bot.resistance = 10kohm +/- 5%
```

## 实例化
- 单个：`x = new Resistor`
- 数组：`leds = new LED[8]`

## 连接
- 直连：`a ~ b`（接口/引脚直接相连）
- 串联桥接：`power.vcc ~> r_top ~> r_bot ~> power.gnd`（依次穿过）

## 参数 + 单位 + 约束
```ato
c1.capacitance = 100nF
assert r_top.resistance within 9kohm to 11kohm
assert ldo.output_voltage is 3.3V
```
带单位字面量：`V`、`A`、`ohm/kohm/Mohm`、`F/uF/nF/pF`、`Hz/kHz/MHz`。
`assert ... within ...` / `is ...` 约束 → 编译时**参数化选元件**（picker）。

## 接口（interface）
```ato
interface Power:
    vcc = new Electrical
    gnd = new Electrical
```

## CLI
```bash
ato create                 # 新工程
ato create component       # 新组件骨架
ato add <package>          # 从 packages.atopile.io 安装模块
ato build                  # 编译、选料、更新 KiCad 布局（见 ato-build）
```

## 常见坑
- 约束过紧 → picker 选不到件；放宽容差/封装或换系列。
- 接口未连全 → 编译/ERC 报悬空；用 `~>` 串联确保通路。
- 复用优先：先到 packages.atopile.io / GitHub 找现成模块再自己写。
