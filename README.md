# yys-optimizer
阴阳师悬赏任务辅助方案
# 问题
阴阳师每天都会刷出悬赏任务，比如
```
怪物 A : 10
怪物 B : 13
怪物 C : 6
怪物 D : 10
...

```
按照正常的思路，也就是网易精灵给出的答案：找到含有 *单个目标怪物* **最多** 的副本

假设有副本 W, X, Y, Z 

相应的目标怪物数量 A:3, B:4, C:2, D:3

总共要下副本的次数为: 4 + 5 + 3 + 4 = 16 次

目标解法是 4\*W + 5\*X + 3\*Y + 4\*Z

在每个副本 *仅含* 有 **一个目标怪物** 时，这确实是最优解。但是，如果每个副本含有 **多个目标怪物** 时，这还是最优解吗？

# 原理
**纯整数线性规划** / **纯整数对偶规划** 

我们用一个矩阵来描述副本与怪物的关系

行为副本，列为怪物

|   | A | B | C | D |
| :----:| :----: | :----: | :----: | :----: |
| W | 3 | 0 | 0 | 0 |
| X | 0 | 4 | 0 | 0 |
| Y | 0 | 0 | 2 | 0 |
| Z | 0 | 0 | 0 | 3 |
| W‘ | 2 | 2 | 0 | 1 |
| X‘ | 1 | 3 | 1 | 0 |

W' 和 X' 均不是含有 **最多** 数量的副本，但是它们是最优解之一

```
怪物 A : 10
怪物 B : 13
怪物 C : 6
怪物 D : 10
...

```
同样的一个悬赏

现在的一个最优解是: 4\*W' + 2\*X' + 2\*Y + 2\*Z

总共要下副本的次数为: 4 + 2 + 2 + 2 = 10 次

比网易精灵推荐的少打了4次副本！

## 术语
设每个副本包含怪物数量为A，对应怪物为i，对应副本为j （行为怪物，列为副本）有矩阵

\[A00....A0j\] 

\[Ai0....Aij\]

其中行向量称为 ai

设每个副本攻打次数为X，对应副本索引为i，有向量 \[X0....Xi\]

设每个悬赏怪物为B，对应怪物索引为i，有向量 \[B0....Bi\]

优化目标: 

`min sum(X)`

约束: 
```
ai * X >= Bi
Xi >= 0

Xi 为整数解
```


# 应用地址（需要VPN）
https://yitiaoxiangsugou.tk
