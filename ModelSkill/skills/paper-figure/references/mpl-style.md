# matplotlib 论文样式片段

## 通用 rcParams（放脚本开头）
```python
import matplotlib.pyplot as plt
plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "font.size": 9,            # 接近正文字号
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "legend.fontsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "lines.linewidth": 1.3,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,        # 嵌入字体，投稿要求
    "ps.fonttype": 42,
})
```

## 栏宽尺寸（英寸）
- 单栏：约 3.5 in 宽；双栏跨栏：约 7.16 in；高度按 0.62× 宽（黄金比）起调。
```python
fig, ax = plt.subplots(figsize=(3.5, 2.6))
```

## 中文字体（避免方块）
```python
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Noto Sans CJK SC"]
plt.rcParams["axes.unicode_minus"] = False
```

## 色盲友好配色（Okabe-Ito）
```python
CB = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#000000"]
```
黑白打印再叠加线型/marker：`linestyle` in `['-','--','-.',':']`，`marker` in `['o','s','^','D']`。

## 导出
```python
fig.savefig("figure.pdf")          # 矢量，首选
fig.savefig("figure.png", dpi=300) # 位图备用
```

## 最小可运行示例
```python
import numpy as np, matplotlib.pyplot as plt
x = np.linspace(0, 10, 200)
fig, ax = plt.subplots(figsize=(3.5, 2.6))
ax.plot(x, np.sin(x), label="sin")
ax.plot(x, np.cos(x), "--", label="cos")
ax.set_xlabel("x"); ax.set_ylabel("y"); ax.legend()
fig.savefig("demo.pdf")
```
