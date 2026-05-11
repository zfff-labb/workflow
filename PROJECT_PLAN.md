# 品牌多维度评分 Workflow 整体规划

## 1. 项目目标与范围

基于 `sample-data` 中的多源数据，构建一个可运行的品牌评分 Workflow，实现：

1. 数据加载
2. 多维度指标提取
3. 评分计算
4. LLM 综合诊断（使用 `deepseek-v4-flash`）
5. 报告输出（结构化、中文）

交付包含：

- 完整 Git 开发历史（分模块提交）
- 可运行代码与 `README.md`
- 数据探查 Jupyter Notebook
- 最终评分报告（含各维度得分、总分、LLM 100-200 字总结）

## 2. 目录规划

建议目录结构如下：

```text
workflow/
├─ sample-data/
├─ notebooks/
│  └─ 01_data_exploration.ipynb
├─ src/
│  ├─ config/
│  │  └─ settings.py
│  ├─ data/
│  │  └─ loader.py
│  ├─ features/
│  │  └─ metric_extractor.py
│  ├─ scoring/
│  │  └─ scorer.py
│  ├─ llm/
│  │  └─ diagnosis.py
│  ├─ report/
│  │  └─ generator.py
│  └─ workflow.py
├─ outputs/
│  ├─ brand_report.md
│  └─ score_radar.png
├─ tests/
│  └─ test_scoring.py
├─ .env.example
├─ requirements.txt
├─ README.md
└─ PROJECT_PLAN.md
```

## 3. 技术选型

- 语言：Python 3.10+
- 数据处理：`pandas`, `numpy`
- 可视化：`matplotlib`（雷达图可选）
- Notebook：`jupyter`
- 配置管理：`python-dotenv`
- LLM 调用：OpenAI 兼容方式接入 DeepSeek（模型固定为 `deepseek-v4-flash`）
- 测试：`pytest`

## 4. 评分维度设计（以数据可支撑为原则）

优先落地以下 6 个维度（其余维度若数据不足则标注低置信度并跳过）：

1. 品牌成熟度
2. 产品质量
3. 市场需求匹配度
4. 创新力
5. 供应链可靠性
6. 性价比

### 4.1 维度到数据映射（示例）

- 品牌成熟度：
  - `brand-info.json` 的品牌成立时间/市场覆盖信息
  - `traffic-info.json` 的官网流量规模与稳定性
- 产品质量：
  - `review-info.json` 的平均评分、质量相关负面评论占比
- 市场需求匹配度：
  - `products-info.json` 的销量、热度字段（若有）
  - `review-info.json` 的需求相关关键词
- 创新力：
  - `company-info.json` 近一年新品/里程碑事件数量
- 供应链可靠性：
  - `review-info.json` 中物流延迟、缺货、配送问题占比
- 性价比：
  - `products-info.json` 定价区间
  - `review-info.json` 中“值不值”倾向词占比

### 4.2 评分机制（建议）

- 每个维度构建 2-4 个可量化子指标并归一化到 0-100。
- 维度分 = 子指标加权和（权重需在文档中解释）。
- 总分 = 已启用维度加权平均。
- 若维度数据缺失或样本不足：
  - 输出 `confidence=low`
  - 不参与总分或降权参与（在报告中明确）

## 5. Workflow 设计

执行入口：`python -m src.workflow`

节点链路：

1. `load_data`：读取 JSON 数据并基础校验
2. `extract_metrics`：提取维度子指标
3. `compute_scores`：生成维度分、总分、置信度
4. `llm_diagnosis`：调用 `deepseek-v4-flash` 输出中文综合诊断（100-200 字）
5. `generate_report`：输出 `outputs/brand_report.md`，可选输出雷达图

## 6. Git 分支、提交与推送策略（严格执行）

分支命名建议：`feature/brand-scoring-workflow`

关键约束（按你的要求）：

- 必须按模块完成后立即推送到远程仓库
- 不做多个模块攒到一起再推送
- 每次只推进一个模块，再进入下一个模块

模块节奏（示例）：

1. 模块 A：项目初始化与依赖
   - 提交：`chore: init project structure and dependencies`
   - 推送：立即 `git push -u origin feature/brand-scoring-workflow`
2. 模块 B：数据探查 Notebook
   - 提交：`feat: add data exploration notebook with key findings`
   - 推送：立即 push
3. 模块 C：指标设计与评分逻辑
   - 提交：`feat: implement metric extraction and scoring engine`
   - 推送：立即 push
4. 模块 D：Workflow 主流程 + LLM 诊断
   - 提交：`feat: build workflow pipeline with deepseek diagnosis`
   - 推送：立即 push
5. 模块 E：报告输出与可视化
   - 提交：`feat: generate structured report and optional radar chart`
   - 推送：立即 push
6. 模块 F：README、测试与收尾
   - 提交：`docs: finalize readme and usage instructions`
   - 提交：`test: add scoring unit tests`
   - 每次提交后立即 push

远程仓库：

```bash
git remote add origin https://github.com/zfff-labb/workflow
```

## 7. API 与安全配置规范

`.env` 示例（本地保存，不提交）：

```bash
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

必须执行：

- 将 `.env` 写入 `.gitignore`
- 提交 `.env.example`（不含真实密钥）
- 代码中通过环境变量读取 API Key，禁止硬编码

## 8. 数据探查 Notebook 交付要求

Notebook 文件：`notebooks/01_data_exploration.ipynb`

最少包含：

1. 数据加载与字段概览（五份 JSON）
2. 缺失值、异常值、样本规模检查
3. 每个候选维度的数据可支撑性判断
4. 指标定义草案与可行性结论
5. 输出一页“维度取舍与置信度”总结

## 9. 报告输出模板（`outputs/brand_report.md`）

建议结构：

1. 品牌概览
2. 维度得分表（含计算方式说明）
3. 低置信度维度说明（如有）
4. 综合总分与解释
5. LLM 中文诊断（100-200 字）
6. 可视化图（可选）

## 10. README 必备内容

- 项目简介
- 目录结构
- 环境准备（Python 版本、安装依赖）
- 配置说明（`.env`）
- 运行方式（如何执行 Workflow）
- 输出说明（报告与图表路径）
- 方法说明（维度、权重、置信度策略）

## 11. 验收清单

- [ ] 数据探查以 Jupyter Notebook 呈现
- [ ] Workflow 可从命令行一键运行
- [ ] 使用模型 `deepseek-v4-flash`
- [ ] 维度得分可量化且有计算依据
- [ ] LLM 总结为中文 100-200 字
- [ ] 每完成一个模块立即提交并推送
- [ ] Git 历史体现清晰开发节奏
- [ ] README 可让他人复现

## 12. 48 小时建议排期

- 0-6h：项目初始化 + 数据探查 Notebook（完成并 push）
- 6-16h：指标设计 + 评分引擎（完成并 push）
- 16-28h：Workflow 编排 + LLM 接入（完成并 push）
- 28-38h：报告生成 + 可视化（完成并 push）
- 38-48h：测试、README、自检与最终整理（完成并 push）

