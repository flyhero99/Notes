# 一些DP题目

* 2018清软九推机试第三题

已知 $n$ 个数 $ (n <= 500), a_1, _…, a_n $
拿掉第 $i$ 个数收益 $a[i−1] ∗ a[i] ∗ a[i+1] $，注意是直接拿走了，所以影响左右的相邻关系 
求最大收益 

其中 $a_0$ 和 $a_{n+1} = 1$

思路：区间dp

考虑区间 $[i, j]$ 最后一个拿的元素是 $k$ 的结果

$ dp[i][j] = max(dp[i][j], dp[i][k-1] + dp[k+1][j] + a[k]*a[j-1]*a[j+1]) $

* 未完待续...