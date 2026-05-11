# 指标设计过程文档

## 1. 设计目标

本模块目标是将 `sample-data` 转换为可计算、可解释、可复现的评分指标，输出：

- 维度级原始指标（metrics）
- 维度得分（0-100）
- 维度置信度（high/medium/low）
- 品牌综合得分（加权汇总）

## 2. 数据可支撑性判断

数据源与可支撑信息：

1. `brand-info.json`：品牌基础、站点规模、估算访问量、渠道信息
2. `traffic-info.json`：近三月访问趋势、来源结构、排名
3. `review-info.json`：星级、用户文本反馈（质量/价格/供应链信号）
4. `products-info.json`：产品发布时间、变体价格、可售状态
5. `company-info.json`：时间线事件（用于创新活跃度代理）

维度取舍：

- 启用：品牌成熟度、产品质量、市场需求匹配度、创新力、供应链可靠性、性价比
- 降置信度：供应链可靠性（评论中的供应链问题信号相对稀疏）
- 暂不单独评分：可持续发展、市场趋势契合度（样例数据中缺少强结构化证据）

## 3. 指标构建原则

1. 每个维度 2-3 个子指标，避免单指标决定维度分
2. 统一映射到 0-100
3. 对“负向指标”使用反向归一化（值越大分越低）
4. 所有权重显式可见，便于审计与复现
5. 置信度低的维度在总分阶段降权处理

## 4. 计算公式（核心）

## 4.1 品牌成熟度（Brand Maturity）

子指标：

- 市场存在时长：`years_on_market`
- 品牌访问规模：`estimated_visits`
- 访问稳定性：`visits_cv_3m`（3 个月访问量变异系数）

标准化：

- `S_years = linear(years_on_market, 0, 8)`
- `S_scale = linear(log1p(estimated_visits), 0, log1p(2,000,000))`
- `S_stability = inverse_linear(visits_cv_3m, 0, 0.8)`

维度分：

- `Score_maturity = 0.35*S_years + 0.40*S_scale + 0.25*S_stability`

## 4.2 产品质量（Product Quality）

子指标：

- 平均星级：`avg_stars`
- 低星占比：`low_star_ratio`（`stars <= 2`）
- 负向质量关键词占比：`quality_negative_ratio`

标准化：

- `S_star = linear(avg_stars, 1, 5)`
- `S_low = inverse_linear(low_star_ratio, 0, 0.5)`
- `S_text = inverse_linear(quality_negative_ratio, 0, 0.4)`

维度分：

- `Score_quality = 0.50*S_star + 0.25*S_low + 0.25*S_text`

## 4.3 市场需求匹配度（Demand Fit）

子指标：

- 近三月访问均值：`visits_mean_3m`
- 高分评价占比：`high_star_ratio`（`stars >= 4`）
- 复购/粘性关键词占比：`repeat_purchase_ratio`

标准化：

- `S_traffic = linear(log1p(visits_mean_3m), 0, log1p(800,000))`
- `S_high = linear(high_star_ratio, 0, 1)`
- `S_repeat = linear(repeat_purchase_ratio, 0, 0.5)`

维度分：

- `Score_demand = 0.45*S_traffic + 0.35*S_high + 0.20*S_repeat`

## 4.4 创新力（Innovation）

子指标：

- 近一年新品占比：`new_products_last_365d / valid_product_count`
- 近一年公司时间线活跃事件数：`recent_activity_365d`
- 产品线新鲜度（中位上新天数）：`product_line_freshness_days`

标准化：

- `S_new = linear(new_products_ratio, 0, 0.5)`
- `S_activity = linear(recent_activity_365d, 0, 25)`
- `S_fresh = inverse_linear(product_line_freshness_days, 60, 1200)`

维度分：

- `Score_innovation = 0.40*S_new + 0.40*S_activity + 0.20*S_fresh`

## 4.5 供应链可靠性（Supply Chain Reliability）

子指标：

- 可售变体占比：`available_variant_ratio`
- 供应链问题关键词占比：`supply_issue_ratio`
- 物流承运商数量：`shipping_carrier_count`

标准化：

- `S_available = linear(available_variant_ratio, 0, 1)`
- `S_issue = inverse_linear(supply_issue_ratio, 0, 0.2)`
- `S_carrier = linear(shipping_carrier_count, 1, 3)`

维度分：

- `Score_supply = 0.45*S_available + 0.35*S_issue + 0.20*S_carrier`

## 4.6 性价比（Value for Money）

子指标：

- 均价信号：`avg_variant_price`
- 价值感知净值：`value_positive_ratio - value_negative_ratio`
- 星级支撑：`avg_stars`

标准化：

- `S_price = inverse_linear(avg_variant_price, 2, 40)`
- `S_value = linear((value_positive_ratio - value_negative_ratio + 1)/2, 0, 1)`
- `S_star = linear(avg_stars, 1, 5)`

维度分：

- `Score_value = 0.25*S_price + 0.45*S_value + 0.30*S_star`

## 5. 综合评分与置信度

基础维度权重：

- 品牌成熟度 0.22
- 产品质量 0.20
- 市场需求匹配度 0.18
- 创新力 0.14
- 供应链可靠性 0.12
- 性价比 0.14

置信度系数：

- `high = 1.00`
- `medium = 0.85`
- `low = 0.60`

最终总分：

- `TotalScore = weighted_mean(维度分, 基础权重 × 置信度系数)`

## 6. 关键词词典与可解释性

当前版本使用轻量关键词匹配提取评论信号（质量负向、供应链问题、价值感知、复购倾向）。优点是可解释、实现简单；缺点是语义覆盖有限。后续可替换为：

1. 情感分类器（aspect-based sentiment）
2. 主题模型/向量检索
3. LLM 批量标注后蒸馏

## 7. 局限性与后续优化

当前局限：

- 缺真实销量与库存时序，需求与供应链维度存在代理偏差
- 评论样本量有限，文本信号受采样影响
- 价格未做“单位规格标准化”，仅做近似比较

优化方向：

1. 引入外部趋势数据（Google Trends、类目季节性）
2. 接入物流履约与退货数据
3. 建立按品类分桶的价格基线
4. 做维度权重校准（专家标注 / 历史表现回归）
