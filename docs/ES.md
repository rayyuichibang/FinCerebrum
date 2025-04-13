# Expected Shortfall (ES) 风险模型

## 模型解释
Expected Shortfall (ES)，又称条件风险价值(CVaR)，是比VaR更严格的尾部风险度量指标。它在VaR的基础上，进一步计算**当损失超过VaR阈值时的平均损失水平**。

核心特点：
- 衡量极端损失的平均程度
- 满足次可加性（Coherent Risk Measure）
- 对尾部风险更敏感
- 被巴塞尔协议III推荐为市场风险标准

## 数学原理

### 基本定义
对于置信水平α（通常取95%或99%），ES定义为：

$$
ES_\alpha = \frac{1}{1-\alpha} \int_{\alpha}^1 VaR_u(L)du
$$

其中：
- $VaR_u(L)$ = 置信水平u下的VaR值
- $L$ = 投资组合损失随机变量

### 离散形式计算
基于历史数据时，ES可表示为：

$$
ES_\alpha = \mathbb{E}[L | L \geq VaR_\alpha]
$$

### 参数法公式（正态分布假设）
当损失服从$N(\mu, \sigma^2)$时：

$$
ES_\alpha = \mu + \sigma \frac{\phi(\Phi^{-1}(\alpha))}{1-\alpha}
$$

其中：
- $\phi$ = 标准正态PDF
- $\Phi^{-1}$ = 标准正态逆CDF
