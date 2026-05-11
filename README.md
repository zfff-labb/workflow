# Brand Multi-dimensional Scoring Workflow

本项目旨在构建一个自动化的品牌健康度评估系统，通过多源数据分析、量化评分以及大语言模型（LLM）的深度诊断，输出结构化的品牌分析报告。

## 核心流程

1. **数据加载 (Data Loading)**: 加载品牌基础信息、财务数据、产品列表、用户评论及流量数据。
2. **多维度指标提取 (Metric Extraction)**: 从原始数据中提取关键经营与市场指标。
3. **评分计算 (Scoring)**: 基于预定义的 8 个维度（品牌成熟度、产品质量等）进行量化评分。
4. **LLM 综合诊断 (LLM Diagnosis)**: 利用 DeepSeek-V4-Flash 模型对评分结果进行深度分析，生成专家级综述。
5. **报告输出 (Report Generation)**: 生成包含雷达图可视化、详细指标及 LLM 诊断的 Markdown 报告。

## 环境要求

- Python 3.8+
- [DeepSeek API Key](https://platform.deepseek.com/) (模型使用 `deepseek-v4-flash`)

## 安装与配置

1. **克隆仓库**
   ```bash
   git clone https://github.com/zfff-labb/workflow
   cd workflow
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   创建 `.env` 文件并填入你的 API Key：
   ```env
   DEEPSEEK_API_KEY=your_api_key_here
   ```
   你可以参考 `.env.example`。

## 运行 Workflow

在项目根目录下运行以下命令即可生成品牌评分报告：

```bash
python -m src.workflow
```

运行完成后，结果将保存在 `outputs/` 目录下：
- `brand_report.md`: 结构化的品牌分析报告。
- `metrics_and_scores.json`: 原始提取的指标与各项得分数据。
- `brand_score_radar.png`: 品牌各维度得分的雷达图。

## 项目结构

- `src/`: 源代码目录
  - `data/`: 数据加载模块
  - `features/`: 指标提取逻辑
  - `scoring/`: 评分引擎与权重配置
  - `llm/`: DeepSeek 模型调用与 Prompt 管理
  - `report/`: 报告与可视化生成
- `notebooks/`: 数据探查与验证过程
- `docs/`: 指标设计与计算逻辑说明文档
- `outputs/`: 报告输出目录

## 评分维度说明

详见 [METRIC_DESIGN.md](docs/METRIC_DESIGN.md)。本项目重点覆盖了品牌成熟度、产品质量、市场需求、创新力、供应链可靠性及性价比等核心维度。
