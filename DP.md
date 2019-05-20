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



### 2019-05-20

### 图论

* 图的bfs

```c++
void bfs(int st) {
    memset(vis, 0, sizeof vis);
    queue<int> q;
    q.push(st);
    while(!q.empty()) {
        int u = q.front(); q.pop();
        if(vis[u]) continue;
        vis[u] = true;
        cout << u << " ";
        for(int i = 0; i < vec[u].size(); i++) {
            int v = vec[u][i].v;
            q.push(v);
        }
    }
    cout << endl;
}
```

* 图的dfs

```c++
void dfs(int v) {
    if(vis[v]) return;
    vis[v] = 1;
    cout << v << ' ';
    for(int i = 0; i < vec[v].size(); i++) dfs(vec[v][i].v);
}
```

* Bellman-Ford

遍历所有边，进行n-1次松弛，如果第n次还能松弛说明有负环，否则已求出所有单源最短路。复杂度$O(VE)$

```c++
bool bellman_ford(int st) {
    memset(dis, inf, sizeof dis);
    dis[st] = 0;
    for(int i = 1; i <= n-1; i++) {
        for(int j = 1; j <= m; j++) {
            Edge2 t = e[j];
            int u = t.u, v = t.v, c = t.c;
            if(dis[u] + c < dis[v]) dis[v] = dis[u] + c;
        }
    }
    for(int j = 1; j <= m; j++) {
        Edge2 t = e[j];
        int u = t.u, v = t.v, c = t.c;
        if(dis[u] + c < dis[v]) return false;
    }
    return true;
}
```

* Dijk

将有向图$G = (V, E)$的节点分成两个集合，S是已经求出最短路的，U是还未求出的。从U中选出一个dis最小的节点k，将k加入S中，然后用k来松弛所有U中与k邻接的点。重复至多n-1次，直到所有点都进入S中。

```c++
void dijkn2(int st) {
    for(int i = 0; i <= n; i++) {
        dis[i] = inf; vis[i] = 0; // vis相当于表示节点是否在S集合里，1表示在，0表示不在
    }
    dis[st] = 0;
    for(int i = 1; i <= n-1; i++) {
        int minn = inf, t = -1;
        for(int j = 1; j <= n; j++) {
            if(!vis[j] && minn > dis[j]) {
                minn = dis[j];
                t = j; // 找到当前dis最小的点t
            }
        }
        vis[t] = true; // 把t加进集合S
        for(int j = 0; j < vec[t].size(); j++) {
            int v = vec[t][j].v, c = vec[t][j].c;
            if(!vis[v] && dis[v] > dis[t] + c) { // 与t邻接的未访问过的节点
                dis[v] = dis[t] + c;
            }
        }
    }
}

void dijknlogn(int st) {
    for(int i = 0; i <= n; i++) {
        dis[i] = inf; vis[i] = 0;
    }
    priority_queue<pii, vector<pii>, qcmp> q;
    dis[st] = 0; // vis
    q.push(make_pair(dis[st], st));
    while(!q.empty()) {
        pii t = q.top(); q.pop();
        int u = t.se;
        if(vis[u]) continue;
        vis[u] = true; // 相当于找到了dis最小的k，把它加入S中，下面开始用它更新
        for(int i = 0; i < vec[u].size(); i++) {
            int v = vec[u][i].v, c = vec[u][i].c;
            if(vis[v]) continue;
            if(dis[v] > dis[u] + c) {
                dis[v] = dis[u] + c;
                q.push(make_pair(dis[v], v));
            }
        }
    }
}
```

* Floyd

$dp[i][j]$表示从i到j只经过前k个点的最短路径，由于第k个点只有经过或不经过两种情况，因此第k个状态只依赖于状态k-1，用滚动数组的思想可以省略一维。

$dp^k[i][j] = min(dp^{k-1}[i][j], dp^{k-1}[i][k] + dp^{k-1}[k][j])$

```c++
bool floyd() {
    for(int k = 1; k <= n; k++) {
        for(int i = 1; i <= n; i++) {
            for(int j = 1; j <= n; j++) {
                if(g[i][j] > g[i][k] + g[k][j]) {
                    g[i][j] = g[i][k] + g[k][j];
                    // path[i][j] = k;
                }
              	if(g[i][i] < 0) return false; // 可以判断负环，g[i][i]初始应为0，若变负说明有负环
            }
        }
    }
  	return true;
}
```

* Kruskal

1. 把图中的所有边按代价从小到大排序； 
2. 把图中的n个顶点看成独立的n棵树组成的森林； 
3. 按权值从小到大选择边，所选的边连接的两个顶点ui,viui,vi,应属于两颗不同的树，则成为最小生成树的一条边，并将这两颗树合并作为一颗树。 
4. 重复(3),直到所有顶点都在一颗树内或者有n-1条边为止。

```c++
int kruskal() {
    sort(e+1, e+m+1);
    int cnt = 0, sum = 0;
    for(int i = 1; i <= m; i++) {
        int fu = Find(e[i].u), fv = Find(e[i].v);
        if(fu == fv) continue;
        pre[fv] = fu;
        sum += e[i].c;
        cnt++;
        if(cnt == n-1) break;
    }
    return sum;
}
```

* Prim

每次迭代选择代价最小的边对应的点，加入到最小生成树中。算法从某一个顶点s开始，逐渐长大覆盖整个连通网的所有顶点。

1. 图的所有顶点集合为V；初始令集合u = {s}, v = V − u;
2. 在两个集合u,v能够组成的边中，选择一条代价最小的边(u0,v0)，加入到最小生成树中，并把v0并入到集合u中。
3. 重复上述步骤，直到最小生成树有n-1条边或者n个顶点为止。

由于不断向集合u中加点，所以最小代价边必须同步更新；需要建立一个辅助数组closedge,用来维护集合v中每个顶点与集合u中最小代价边信息.

```c++
int lowcost[maxn]; // lowcost[j]表示节点j与u中节点相连的最小权值，0代表已选
int closest[maxn]; // closest[j]存储lowcost[j]对应的连接点

void prim(int st) {
    for(int i = 1; i <= n; i++) {
        closest[i] = st;
        lowcost[i] = g[s][i];
    }
    for(int i = 1; i <= n-1; i++) {
        int minn = inf, k;
        for(int j = 1; j <= n; j++) {
            if(!lowcost[j] && minn > lowcost[j]) {
                minn = lowcost[j];
                k = j;
            }
        }
        lowcost[k] = 0; // 将当前选定的节点k加进u集合
        for(int j = 1; j <= n; j++) {
            if(g[k][j] != 0  && g[k][j] < lowcost[j]) {
                lowcost[j] = g[k][j];
                closest[j] = k;
            }
        }
    }
}
```

* 拓扑排序

（1）找出图中0入度的顶点，依次在图中删除这些顶点，删除后再找出0入度的顶点，然后再删除……再找出……，直至删除所有顶点，即完成拓扑排序

（2）DFS实现拓扑排序，用**栈**来保存拓扑排序的顶点序列；并且保证在某顶点入栈前，其所有邻接点已入栈

```c++
bool topobfs() { // bfs+入度写法
    vector<int> res;
    queue<int> q;
    for(int i = 1; i <= n; i++)
        if(in[i] == 0) q.push(i);
    while(!q.empty()) {
        int u = q.front(); q.pop();
        res.push_back(u);
        for(int i = 0; i < vec[u].size(); i++) {
            int v = vec[u][i].v;
            in[v]--;
            if(in[v] == 0) q.push(v);
        }
    }
    return res.size() == n;
}

// dfs写法
stack<int> s;

void dfs(int u) {
    if(vis[u]) return;
    vis[u] = 1;
    for(int i = 0; i < vec[u].size(); i++) {
        int v = vec[u][i].v;
        if(!vis[v]) dfs(v);
    }
    s.push(u);
}

void topodfs() {
    while(!s.empty()) s.pop();
    for(int i = 1; i <= n; i++) {
        if(!vis[i]) dfs(i);
    }
    while(!s.empty()) { cout << s.top() << ' '; s.pop(); }
    cout << endl;
}
```

* 二分图最大匹配——匈牙利算法

初始时最大匹配为空。while 找得到增广路径——do 把增广路径加入到最大匹配中去。求增广路的方法：

从X部一个未匹配的顶点u开始，找一个未访问的邻接点v（v一定是Y部顶点）。对于 v，分两种情况： 
（1）如果v未匹配，则已经找到一条增广路。 
（2）如果v已经匹配，则取出v的匹配顶点w（w一定是X部顶点），边(w, v)目前是匹配的，根据“取反”的想法，要将(w, v)改为未匹配， (u, v)设为匹配，能实现这一点的条件是看从w为起点能否新找到一条增广路径P’ 。如果行，则u-v-P’ 就是一条以u为起点的增广路径。

```c++
bool dfs(int u) {
    for(int i = 0; i < vec[u].size(); i++) {
        int v = vec[u][i].v;
        if(vis[v]) continue;
        vis[v] = true;
        if(!match[v] || dfs(match[v])) {
            match[v] = u;
            match[u] = v;
            return true;
        }
    }
    return false;
}
```

