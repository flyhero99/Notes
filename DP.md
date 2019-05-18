# 一些题目

###2019-05-16

####一、最长上升子序列LIS

* $O(n^2)$做法

思路较为直接，设dp[i]表示前i个元素LIS的长度

转移方程为：$dp[i] = max(dp[i], dp[j]+1) (a[i] > a[j])$

关键代码：

```c++
for(int i = 1; i <= n; i++) {
  	for(int j = 1; j < i; j++)
    		if(a[i] > a[j]) dp[i] = max(dp[i], dp[j]+1);
}
```

* $O(nlogn)$做法

// 被一篇博客坑惨了....里面的符号写反了，百思不得其解-_-||

贪心思想，LIS目的是在一个序列中选出尽可能多的数组成一个上升子序列。对于最优的LIS，其最后一位一定是尽可能小的，这样在后面更新时才有更大的可能性让LIS变得更长

扫一遍数组，若比最后一位大则直接加到序列后面，否则二分找到第一个比他大的元素，用当前数更新之

此时dp[i]表示长度为i的LIS的最后一位数的值

关键代码：

```c++
for(int i = 1; i <= n; i++) {
		if(dp[m] > a[i]) dp[++m] = a[i]; // 这里m表示LIS的长度，也即最后一位
  	else { // 二分
    		int l = 0, r = m;
    		// l = lower_bound(dp+1, dp+m+1, a[i]) - dp; // 也可以使用lower_bound进行查找
   			while(l < r) {
          	if(dp[mid] > a[i]) r = mid;
			      else l = mid+1;
    		}
		    dp[l] = a[i]; // 更新
  	}
}
```

####二、最长公共子序列LCS

* O(n^2)做法

设$dp[i][j]$表示a串前i为与b串前b为的LCS长度

转移方程：若$a[i]==b[j]$，则$dp[i][j] = max(dp[i][j], dp[i-1][j-1]+1)$

否则$dp[i][j] = max(dp[i][j-1], dp[i-1][j])$

关键代码：

```c++
for(int i = 1; i <= lena; i++) {
  	for(int j = 1; j <= lenb; j++) {
				if(a[i] == b[j]) dp[i][j] = max(dp[i][j], dp[i-1][j-1]+1);
    		else dp[i][j] = max(dp[i-1][j], dp[i][j-1]);
  	}
}
```

* O(nlogn)做法

在$n^2$做法中，仅当$a[i]==b[j]$时dp才会被更新，不相等处对最终值没有影响，因此可以对枚举相等点处优化

转换为LIS问题，nlogn解决（其实时间复杂度不是严格的$O(nlogn)$，而且最坏情况更糟）

举例说明：A串：abdba，B串：dbaaba；

1）先顺序扫描A串，取其在B串中出现的所有位置：a(3, 4, 6), b(2, 5), d(1)

2）用每个字母出现位置的反序替换原序列，最终得到序列的LIS即为解，且每个解都对应一个LCS。（B串下标）

替换结果：643-52-1-52-643，LIS=3，共三种情况：126，124，123，对应的都是dba

反序是为了在递增子串中，每个字母对应的序列最多只有一个被选出

反证法可知不存在更大的公共子串，因为如果存在，则求得的最长递增子序列不是最长的，矛盾。

关键代码：

```c++
char a[maxn], b[maxn];
vector<int> location[26];
int c[100005], dp[100005];

int lcsnlogn() {
	for(int i = 0; i < 26; i++) location[i].clear();
  	for(int i = blen; i >= 1; i--) { // 为了得到反序的位置
      	location[b[i]-'a'].push_back(i);
    }
  	int k = 0;
  	for(int i = 1; i <= alen; i++) { // 替换原A串
      	int t = a[i]-'a';
      	for(int j = 0; j < location[t].size(); j++) c[++k] = location[t][j];
    }
  	dp[1] = c[1]; int m = 0;
  	for(int i = 2; i <= k; i++) { // 二分求LIS
      	if(c[i] > dp[m]) dp[++m] = c[i];
      	else {
          	int t = lower_bound(dp+1, dp+m+1, c[i]) - dp;
          	dp[t] = c[i];
        }
    }
  	return m;
}
```

####三、区间DP

对小区间进行dp得出最优解，然后通过小区间的最优解得出一整个区间的最优解

####矩阵链乘

假设最后一次乘法是第k个乘号，$P = A_1*A_2*...*A_k$，$Q = A_{k+1} * A_{k+2} * ... * A_n$，枚举最后一次乘法

设$m[i, j]$代表第i到第j个矩阵做乘法的最少运算次数，也即区间i～j。设$A_i$的形状是$p_{i-1} * p_i$的。

转移方程如下：

​		$m[i, j]=\left\{\begin{array}{ll}{0} & {\text { if } i=j} \\ {\min _{i \leq k<j}\left\{m[i, k]+m[k+1, j]+p_{i-1} p_{k} p_{j}\right\}} & {\text { if } i<j}\end{array}\right.$

边界为$m[i, i] = 0$。为了保证DP的最优子结构性质，递推需要按j-i递增的顺序，因为长区间的值依赖于短区间的值。写成记忆化搜索也可。

关键代码：

```c++
int matrix() {
  	for(int len = 2; len <= n; len++) { // len表示[i, j]的元素个数（左闭右闭区间）
      	for(int i = 1; i <= n-len+1; i++) { // i表示左端点
          	int j = i+len-1; // j-i = l-1
          	dp[i][j] = inf;
          	for(int k = i; k < j; k++) // k是枚举区间[i, j]内部
              	dp[i][j] = min(dp[i][j], dp[i][k]+dp[k+1][j]+p[i-1]*p[k]*p[j]);
        }
    }
	  return dp[1][n];
}
```

###2019-05-17

#### 石子合并问题

n堆石子，每次可以将相邻的两堆合并成一堆，花费是两堆石子数量之和，求n堆合成一堆的最小花费。

枚举断点划分子问题，通过子问题的最优解得出整个区间的最优解，区间dp都是这种思路

设$f[i][j]$表示把区间$[i, j]$石子合并为一堆的最小花费

转移方程为：$f[i][j] = max(f[i][j], f[i][k] + f[k+1][j] + sum[j]-sum[j-1])$

石子个数用前缀和处理，这样可以O(1)得到i～j的石子数量

* $O(n^3)$做法

关键代码：

```c++
int f[maxn][maxn], c[maxn];

int work() {
		for(int len = 2; len <= n; len++) {
        for(int i = 1; i <= n-len+1; i++) {
            int j = i+len-1;
            f[i][i] = 0;
            for(int k = i; k < j; k++)
                f[i][j] = min(f[i][j], f[i][k] + f[k+1][j] + c[j]-c[j-1]);
        }
    }  	
}
```

* $O(n^2)$——四边形不等式优化

这篇博客讲的很详细：<a href="https://blog.csdn.net/noiau/article/details/72514812">链接</a>

性质：对于$a < b ≤ c < d$，若$f[a][c]+f[b][d] ≤ f[b][c]+f[a][d]$，则满足四边形不等式优化条件。（交叉小于包含）

大意就是说，对于转移方程为$dp[i][j] = min(dp[i][k] + dp[k+1][j] + cost[i][j])$这样的问题，如果问题的cost函数、dp数组以及决策方式都满足性质的话，就可以利用四边形不等式优化。

1）证明cost为凸：当$i < i+1 ≤ j < j+1$时，$cost[i][j]+cost[i+1][j+1]<=cost[i][j+1]+cost[i+1][j]$

2）证明dp为凸：当$i < i+1 ≤ j < j+1$时，$dp[i][j]+dp[i+1][j+1]<=dp[i+1][j]+dp[i][j+1]$

3）证明决策单调：$s[i][j-1]<=s[i][j]<=s[i+1][j] $

定义数组$s[i][j]$表示$dp[i][j]$取得最优值时对应的下标，即$i≤k≤j$时，k处的dp值最大，则$s[i][j] = k$

如果$dp[i][j]$满足四边形不等式，则$s[i][j]$单调，即$s[i][j] ≤ s[i][j+1] ≤ s[i+1][j+1]$。

关键代码：

```c++
int dp[maxn][maxn], c[maxn];

int work() {
  	for(int i = n; i >= 1; i--) {
      	for(int j = i+1; j <= n; j++) {
         		int tmp;
          	for(int k = s[i][j-1]; k <= s[i+1][j]; k++) {
              	if(dp[i][j] > dp[i][k] + dp[k+1][j] + c[j] - c[i-1]) {
                  	dp[i][j] = dp[i][k] + dp[k+1][j] + c[j] - c[i-1];
                  	tmp = k;
                }
            }
          	s[i][j] = tmp;
        }
    }
  	return dp[1][n];
}
```

遇到具体问题时可以直接写一个$O(n^3)$的打表看一下是否满足性质，不用手动证明。

####四、最大子段和问题

给一个序列，正负不定，求出$a[i] + a[i+1] + ... + a[j]$的最大值$(1 ≤ i ≤ j ≤ n)$

设f[i]表示从1到i的最大子段和，转移方程为：$f[i]=max(f[i−1]+a[i],a[i])$

#### 数字三角形

* 朴素递归写法：复杂度$O(2^n)$

```c++
int solve(int i, int j) {
  	return a[i][j] + (i==n ? 0 : max(solve(i+1, j), solve(i+1, j+1)));
}
```

* 递推计算：复杂度$O(n^2)$

```c++
for(int i = 1; i <= n; i++) d[n][i] = a[n][i];
for(int i = n-1; i >= 1; i--) { // 逆序是因为d[i][j]的计算依赖于d[i+1][j], d[i+1][j+1]
  	for(int j = 1; j <= i; j++)
      	d[i][j] = a[i][j] + max(d[i+1][j], d[i+1][j+1]);
}
```

* 记忆化搜索：复杂度$O(n^2)$，因为节点总数一共只有$n^2$个，保证每个节点只访问一次

```c++
int solve(int i, int j) {
  	if(d[i][j] >= 0) return d[i][j];
  	return d[i][j] = a[i][j] + (i==n ? 0 : max(solve(i+1, j), solve(i+1, j+1)));
}
```

#### DAG模型

* 嵌套矩形问题

矩形的可嵌套看成二元关系，用图来建模，求DAG上的最长路径

设d(i)表示从节点i出发的最长路长度，则$d(i) = max (d(j)+1 | (i, j) ∈ E)$。记忆化搜索代码如下：

```c++
int dp(int i) {
  	int& ans = d[i]; // 存引用，直接操作数组元素
  	if(ans > 0) return ans;
  	ans = 1;
  	for(int j = 1; j <= n; j++)
      	if(G[i][j]) ans = max(ans, dp(j)+1);
  	return ans;
}
void print_ans(int i) { // 输出保证字典序最小
  	printf("%d ", i);
  	for(int j = 1; j <= n; j++) {
      	if(G[i][j] && d[i] == d[j]+1) {
          	print_ans(j);
          	break;
        }
    }
}
```

* 硬币问题：初始状态S，终止状态0

d(i)：从节点i出发到节点0的最长路径长度，代码如下：

```c++
int dp(int s) {
  	int& ans = d[S]; // 由于S可以为0，因此d=0不能表示未访问，应该memset(S, -1)
  	if(ans != -1) return ans;
  	ans = -inf;
  	for(int i = 1; i <= n; i++) if(S >= V[i]) ans = max(ans, dp(S-V[i])+1);
  	return ans;
}
```

另一种常见写法：用vis数组

```c++
int dp(int s) {
  	if(vis[s]) return d[s];
  	vis[s] = 1;
  	int& ans = d[s];
  	ans = -inf;
  	for(int i = 1; i <= n; i++) if(s >= v[i]) ans = max(ans, dp(s-v[i])+1);
}
```

传统递推——填表法：对于每个状态i，找到f(i)依赖的所有状态，计算f(i)

刷表法：对于每个状态i，更新f(i)所影响到的状态

#### 树形DP



####状压DP



#### 数位DP



