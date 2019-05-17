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

设$m[i, j]$代表第i到第j个矩阵做乘法的最少运算次数，也即区间i～j。转移方程如下：

$m[i, j]=\left\{\begin{array}{ll}{0} & {\text { if } i=j} \\ {\min _{i \leq k<j}\left\{m[i, k]+m[k+1, j]+p_{i-1} p_{k} p_{j}\right\}} & {\text { if } i<j}\end{array}\right.$

关键代码：

#### 石子合并问题





