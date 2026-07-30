# ModelTraining

智能训练配置调度器和小数据集优化训练框架。

## 功能特性

- **数据集验证**: 检查训练数据的格式、质量和统计信息
- **架构推荐**: 根据数据集大小和硬件资源智能推荐模型架构
- **资源预估**: 预估训练所需的GPU内存、时间和成本
- **配置生成**: 为Hugging Face、Axolotl等工具生成训练配置
- **模型导出**: 支持多种格式（SafeTensors、ONNX、GGUF）

## 快速开始

### 1. 数据集验证

```bash
# 基本信息
mtb train data dataset.jsonl

# 验证格式和质量
mtb train data dataset.jsonl --validate

# 详细统计
mtb train data dataset.jsonl --stats --verbose

# 严格模式（将警告视为错误）
mtb train data dataset.jsonl --validate --strict
```

### 2. 架构推荐

```bash
# 获取推荐
mtb train recommend dataset.jsonl

# 指定GPU内存约束
mtb train recommend dataset.jsonl --gpu-memory 24GB

# JSON输出
mtb train recommend dataset.jsonl --json
```

### 3. 资源预估

```bash
# 预估资源需求
mtb train estimate dataset.jsonl --arch tiny-decoder --method lora

# 不同训练方法
mtb train estimate dataset.jsonl --arch llama2-7b --method qlora
```

### 4. 生成训练计划

```bash
# 生成训练计划
mtb train plan dataset.jsonl --arch tiny-decoder --output ./runs/exp1

# 使用推荐架构
mtb train plan dataset.jsonl --arch llama2-7b
```

### 5. 生成训练配置

```bash
# 生成Hugging Face配置
mtb train generate-config plan.json --format huggingface --output training_args.json

# 生成Axolotl配置
mtb train generate-config plan.json --format axolotl --output axolotl.yml
```

### 6. 模型导出

```bash
# 导出为SafeTensors
mtb train export ./runs/exp1 --format safetensors

# 导出为GGUF（用于llama.cpp）
mtb train export ./runs/exp1 --format gguf

# 导出为ONNX
mtb train export ./runs/exp1 --format onnx
```

## 架构预设

查看可用的架构预设：

```bash
mtb train arch

# 输出示例:
# tiny-decoder    decoder-only-transformer layers=4 hidden=256
# small-decoder   decoder-only-transformer layers=8 hidden=512
# llama2-7b       decoder-only-transformer layers=32 hidden=4096
# mistral-7b      decoder-only-transformer layers=32 hidden=4096
```

## 数据集格式

支持的格式：

### JSONL（推荐）
```jsonl
{"instruction": "What is AI?", "output": "Artificial Intelligence..."}
{"instruction": "Explain ML", "output": "Machine Learning..."}
```

### JSON
```json
[
  {"instruction": "What is AI?", "output": "Artificial Intelligence..."},
  {"instruction": "Explain ML", "output": "Machine Learning..."}
]
```

## 训练方法

| 方法 | 说明 | 适用场景 |
|------|------|----------|
| **LoRA** | 参数高效微调，只训练1%参数 | 小到中型数据集（< 10K样本） |
| **QLoRA** | 量化LoRA，使用INT8量化 | GPU内存受限 |
| **Full** | 全量微调，更新所有参数 | 大型数据集（> 100K样本） |
| **Prompt Tuning** | 只训练soft prompts | 极小数据集（< 1K样本） |

## 推荐规则

| 数据集大小 | 推荐方法 | 推荐模型 |
|------------|----------|----------|
| < 1K 样本 | LoRA (r=8) | tiny-decoder |
| 1K-10K | LoRA (r=16) | small-decoder |
| 10K-100K | QLoRA | llama2-7b |
| > 100K | Full | llama2-7b或更大 |

## 完整工作流示例

```bash
# 1. 验证数据集
mtb train data dataset.jsonl --validate

# 2. 获取推荐
mtb train recommend dataset.jsonl --gpu-memory 24GB

# 3. 预估资源
mtb train estimate dataset.jsonl --arch llama2-7b --method lora

# 4. 生成训练计划
mtb train plan dataset.jsonl --arch llama2-7b --output ./runs/exp1

# 5. 生成Hugging Face配置
mtb train generate-config runs/exp1/plan.json --format huggingface --output config.json

# 6. (训练完成后) 导出模型
mtb train export ./runs/exp1 --format gguf
```

## API参考

### Python API

```python
from modeltoolbox_training.core import (
    validate_dataset,
    compute_stats,
    recommend_architecture,
    estimate_resources,
    training_plan,
    generate_hf_config,
    generate_axolotl_config,
)

# 验证数据集
validation = validate_dataset("dataset.jsonl", strict=False)
print(f"Status: {validation.status}")

# 计算统计
stats = compute_stats("dataset.jsonl", verbose=True)
print(f"Samples: {stats.total_samples}, Avg length: {stats.avg_length}")

# 获取推荐
recommendation = recommend_architecture("dataset.jsonl", gpu_memory="24GB")
print(f"Recommended: {recommendation['recommended_model']}")

# 预估资源
resources = estimate_resources("dataset.jsonl", arch="llama2-7b", method="lora")
print(f"GPU Memory: {resources['gpu_memory']['recommended']}")

# 生成训练计划
plan = training_plan("dataset.jsonl", arch="llama2-7b")

# 生成配置
hf_config = generate_hf_config(plan)
axolotl_config = generate_axolotl_config(plan)
```

## 许可证

MIT License - 完全自有实现，未使用任何AGPL代码。
