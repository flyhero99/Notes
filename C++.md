# 其实我也根本就不会C++

###重载 << 和 >> 运算符

cout 是 ostream 类的对象。ostream 类将 `<<` 重载为成员函数，而且重载了多次。为了使 `cout<<"Star War"` 能够成立，ostream类需要将 `<<` 进行如下重载：

```c++
ostream & ostream::operator << (const char* s) {
    //输出s的代码
    return * this;
}
```

为了使 `cout<<5;` 能够成立，ostream类还需要将 `<<` 进行如下重载：

```c++
ostream & ostream::operator << (int n) {
    //输出n的代码
    return *this;
}
```

重载函数的返回值类型为 ostream 的引用，并且函数返回 *this，就使得 `cout<<"Star War"<<5` 能够成立。有了上面的重载，`cout<<"Star War"<<5;` 就等价于：

```c++
( cout.operator<<("Star War") ).operator<<(5); // cout<<"xx"相当于执行了一个返回值为ostream&的函数，作为第二个<<的第一个参数输入，并将第二个参数输出，以此类推。
```

重载 << 和 >>时，需要声明为friend。

friend关键字定义：友元函数不是类的一部分，但可以访问类中的私有成员。

istream和ostream中是将 << 和 >> 重载了多次的，因此，如果在自己编写的类中将<<和>>作为成员运算符重载，则只能输入这个类的对象，无法读入其他，不能实现cin >> a >> b的功能

而若声明为friend，则只需实现自身的cin cout方法，作为友元函数使用，而与其他类型连用时，调用的还是iostream本身重载过的运算符。

###关于const

* const修饰成员变量：

```c++
#include<iostream>
using namespace std;
int main(){
    int a1=3;   ///non-const data
    const int a2=a1;    ///const data

    int * a3 = &a1;   ///non-const data,non-const pointer
    const int * a4 = &a1;   ///const data,non-const pointer
    int * const a5 = &a1;   ///non-const data,const pointer
    int const * const a6 = &a1;   ///const data,const pointer
    const int * const a7 = &a1;   ///const data,const pointer

    return 0;
}
```

* const修饰指针变量时：
  1. const在*左侧：表示指针可改，数据不能改
  2. const在*右侧：表示指针不能改，数据可以改
  3. 两个const，*左右各一个，表示指针和指针所指数据都不能修改。
* const修饰函数参数：表示传过来的参数在函数内不可以改变，与上面修饰变量时的性质一样。
* const修饰成员函数：
  1. const修饰的成员函数不能修改任何的成员变量。
  2. const的成员函数不能调用非const的成员函数，因为非const成员函数可以修改成员变量。
* const修饰返回值：指针的话，同（1）；值传递的话，加不加没有意义。



### 《C专家编程》

 