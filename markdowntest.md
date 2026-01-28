# 二维正态分布简介
若二维随机向量 $(X, Y)$ 的联合概率密度为
$$
f(x, y) = \Big( 2\pi \sigma_1 \sigma_2 \sqrt{1-\rho^2} \Big) ^{-1}
\exp 
\Bigg\{
    -\cfrac{1}{2(1-\rho^2)}
    \Big(
        \cfrac{(x-\mu_1)^2}{\sigma_1^2}
        - 2\rho \cfrac{(x-\mu_1)(y-\mu_2)}{\sigma_1\sigma_2}
        + \cfrac{(y-\mu_2)^2}{\sigma_2^2}
    \Big)
\Bigg\}
$$

其中 $-\infty < \mu_1, \mu_2 < + \infty, \quad \sigma_1^2 > 0, \quad \sigma_2^2 > 0, \quad \left| \rho \right| < 1$，则称随机向量 $(X, Y)$ 服从参数为 $\mu_1, \mu_2, \sigma_1, \sigma_2, \rho$ 的二维正态分布，记作
$(X, Y) \sim \mathcal N(\mu_1, \mu_2, \sigma_1, \sigma_2, \rho)$