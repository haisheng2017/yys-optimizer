# yys-optimizer
阴阳师悬赏任务辅助方案
# 为什么要做这个方案？
## 通常做法
阴阳师每天都会刷出悬赏任务，当你完成后你能够获得一些奖励，比如
```
名字   : 数量
妖怪 A : 10
妖怪 B : 13
妖怪 C : 6
妖怪 D : 10
...

```
按照正常的思路，也就是网易精灵给出的答案：找到含有 *单个目标妖怪* **最多** 的副本

假设有副本 W, X, Y, Z 

相应的目标妖怪数量 A:3, B:4, C:2, D:3

总共要下副本的次数为: 4 + 5 + 3 + 4 = 16 次

用数学来表达就是 4\*W + 5\*X + 3\*Y + 4\*Z

## 问题引出
在每个副本 *仅含* 有 **一个目标怪物** 时，这确实是最优解。但是，如果每个副本含有 **多个目标怪物** 时，这还是最优解吗？

而实际上，每个副本都含有不同种类的妖怪，他们的个数也并不完全相同

例如，有另一个副本 W'
含有目标妖怪 A:2 B:2 C:0 D:1

当我们不断地进行副本 W' 的时候，目标ABD妖怪的数量是不断减小的，我们可以称 W' 是一个复合副本
通过不断寻找复合副本的组合，一定可以优化下副本的次数。最坏情况就是按照单一情况去求解

# 怎么解决这个问题
## 动态规划
先拿一道例题：硬币找零
```
有 1 2 5 面值的硬币，给你一个目标金额 10，找到能组成的最小数量的硬币
首先来分析，什么是目标：使用硬币的总数最小
10个1 行不行？ 不行，太多了，总数是10
2个5 就可以解决问题，总数是2

所以我们从目标金额 1 开始，到 10 结束，找到每一个目标金额的最小的总数
用一维数据 dp 表示目标金额和使用硬币总数，索引为目标金额，值为硬币总数
例如 dp[1]=1  代表目标金额 1 需要使用的最小硬币数为 1 
当前题目面值数组 cost[i] i=0..2 cost[0]=1 cost[1]=2 cost[2]=5

推进dp的状态方程是
dp[i] = min(dp[i], dp[i-cost[j]]+1)
初始化时，当i=0时，dp[0]=0,其他时，dp[i]=目标金额（最坏情况就是1个1个找零）

时间复杂度是（MN）M是金额数，N是面值数
空间复杂度是（M）
```
这个题用这个方法做可以，但是回到我们的问题，如何迁移？我们不仅要优化最小数量，同时也要知道，哪些“面值”组成了我们的找零方案？

从这道例题出发，我们可以用递归+记忆化搜索的方法改写，用一个数组来模拟找零组合，最后返回最小的数组长度即可。
通过记忆化搜索，复杂度不亚于上面的动态规划。

回到我们原本的问题，难度在于“面值”的定义不再是一个标量的，而是一个向量
例如副本 W ，他的向量是\[3 0 0 0\]

不仅如此，我们原本的问题是找出能够完成目标数的方案，不是一定要等于这个目标数，你可以大于，但不能小于，所以递归退出的判断条件需要改为大于

这两点在递归和记忆化优化上有了很大的难点。虽然我最终实现了一个满足的算法，不过他跑4\*6的矩阵就已经很慢了
推算时间复杂度为指数级（枚举全部向量个数，同时还枚举了每个向量里的值）

## 纯整数线性规划 / 纯整数对偶规划
这个我直接放出一些参考资料

单纯形法：https://www.hrwhisper.me/introduction-to-simplex-algorithm/

python开源库：https://coin-or.github.io/pulp/

# 数据建模
## 基础
我们可以知道，阴阳师所有的妖怪名称，可以作如下数据收集

str_array Monster {'A','B'....} 假设共有 i 个

也可以知道所有副本

str_array Level {'W','X','Y','Z','W'','Z''.....} 假设共有 j 个

Monster\[0\] 代表 妖怪A
Level\[1\] 代表 副本X

## 数据
我们用一个矩阵 Matrix 来描述副本与怪物的关系

行为妖怪，列为副本，该矩阵大小为 (i,j)，举个例子

|   | W | X | Y | Z | W' | X' |
| :----:| :----: | :----: | :----: | :----: | :----: | :----: |
| A | 3 | 0 | 0 | 0 | 2 | 1 |
| B | 0 | 4 | 0 | 0 | 2 | 3 |
| C | 0 | 0 | 2 | 0 | 0 | 1 | 
| D | 0 | 0 | 0 | 3 | 1 | 0 |

从这个矩阵不难发现
W' 和 X' 均不是含有 **最多目标妖怪** 数量的副本，但是它们是最优解之一

```
名字   : 数量
妖怪 A : 10
妖怪 B : 13
妖怪 C : 6
妖怪 D : 10
...

```
同样的一个悬赏

现在的一个最优解是: 4\*W' + 2\*X' + 2\*Y + 2\*Z

总共要下副本的次数为: 4 + 2 + 2 + 2 = 10 次

比网易精灵推荐的少打了6次副本！

## 术语
为了方便和线性规划对应上，这里重新定义一下术语

刚刚的 Matrix 矩阵，叫做 A

A是一个包含i行j列的矩阵，(i,j)
```
A[0][0] 代表 妖怪A 在 副本W 中的数量
A[1][1] 代表 妖怪B 在 副本X 中的数量
...
```

假设副本的攻打次数为X，X是一个向量，里面初始化的数据全部为0

等同于 zeros((j,1)) 代表 X 是一个列向量 ，X的长度和 Level 副本等长
```
X[0] 代表 副本W 需要攻打的次数
```

假设悬赏怪物为B，里面是各个妖怪的目标数量，B也是一个列向量，长度和 Monster 妖怪等长
```
B[0] 代表 妖怪A 被悬赏的目标数量
将我们的例子转换为向量，就是一个4*1的向量
B [[10 13 6 10]]
```

现在我们来确定我们的优化目标
```
min sum(X)
为什么是sum，我们这里只做了简单的比较，即比较攻打副本次数，对X求和，就是总攻打次数
如果需要其他的判断条件，例如每次打副本是需要体力的，有些副本需要体力6，有些需要3，那么我们可以作另一向量体力 [6 6 6 3 3 3] 和 X 向量 进行数乘，之后再求和
```
优化目标确定后，来确定约束: 
```
A*X >= B
Xi >= 0

Xi 为整数解
```
是不是觉得很熟悉？和线性代数相仿？

没错，优化的结果和矩阵的rank，未知数的个数也是相关的，具体详阅参考资料

python的这个开源库，输入优化目标和约束后，调用求解即可

# UI 功能
1 带有前缀匹配搜索的输入框，用于输入悬赏妖怪名称及其目标数量
2 副本过滤，有一些副本很难很难，但是又很难取难度系数，因为对于一个老练玩家来说，这个副本容易，对于新手来说，很难。所以这里直接提供勾选机制，确定纳入计算的副本范围
3 计算并展示最佳方案

# 应用地址（需要VPN）
~~https://yitiaoxiangsugou.tk~~
（阴阳师悬赏系统加入了怪物信息提示，比较方便，无奈家境贫寒，这个地址就先释放了）

# 部署
前端 静态文件

Vue + Vuetify + axios + HTML5

后端 python3.8

nginx + uWSGI + Flask

