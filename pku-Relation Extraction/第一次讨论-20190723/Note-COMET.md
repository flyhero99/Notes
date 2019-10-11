##COMET

<p align="right"> <i>作者：李一飞  时间：2019-07-22</i> </p>

本文提出了一种能够用于自动构建常识知识图谱的Commonsense Transformer。利用一些pre-trained的深度学习语言模型，通过训练它们，使其能够生成常识知识。文章在ATOMIC和ConceptNet两个数据集上做了实验，分别达到了77.5%和91.7%的准确率，基本达到了人类的水平，并且提出利用这种生成commonsense的模型来自动构建常识知识图谱可能很快就会成为extractive method（*这里是指关系抽取的方法吗？*）的合理替代方案。（*这块没太懂，KG constructing和relation extraction有什么联系？*）

#### 1  Introduction

本文提出了COMmonsEnse Transformer (COMET)，利用已有的知识三元组作为seed set进行训练，使得pre-trained的语言模型将其学到的表示向知识生成迁移，并且生成高质量的新tuple。

主要的Contribution：

1. 提出了一个生成的方法（generative method）来构建知识库。模型通过学习产生新节点
2. 开发了一套框架，利用大规模的transformer来学习生成常识知识三元组(commonsense knowledge tuple)
3. 对利用我们的方法在两个知识库（ATOMIC和ConceptNet）上生成的常识知识的质量、新颖程度、多样性进行了实证研究，以及训练处一个有效的模型所需的seed tuples的数量问题。

#### 2  Learning to Generate Commonsense

按照文中所说，COMET是一套adaption framework，在由knowledge tuple构成的seed set上进行训练。这些seed tuples为COMET提供了KB的结构信息和关系信息。COMET学习去将pre-trained的语言模型学到的representation迁移到生成新的知识、关系上，作为节点和边，添加到seed KG中去。

**任务**：对于形如$\{s, r, o\}$ (s-subject, r-relation, o-object) 的三元组，给定s和r，模型需要生成o。

文章中说COMET和语言模型是无关的，本文选用了GPT模型（这个还没看，需要之后补一下）。下文基本也是介绍了一下用到的Transformer和Multi-headed Attention的具体结构，看起来和GPT原模型没太大区别。

**Encoder部分**，模型将$X^s$, $X^r$, $X^o$拼接起来作为输入：$X = \{X^s, X^r, X^o\}$。其中$X^s$, $X^r$, $X^o$均是一个序列，由若干个词构成。对于X中的每个词，还加了一个位置信息：$h_t^0 = e_t + p_t$，其中$e_t$是序列中每个词的embedding，$p_t$将当前词的位置信息编码到和embedding同维度的向量中，将二者相加作为输入。

![image-20190722112241053](/Users/flyhero/Library/Application Support/typora-user-images/image-20190722112241053.png)

（*这个图片里的mask没懂是干什么的。。貌似是和数据集有关系？*）

#### 3  Training COMET

目的是给定s和r，使得模型生成o。因此，模型将$X^s$与$X^r$的拼接作为输入，然后输出序列$X^o$。

**Loss Function**: $\mathcal{L}=-\sum_{t=|s|+|r|}^{|s|+|r|+|o|} \log P\left(x_{t} | x_{<t}\right)$。

**Datasets**：ATOMIC和ConceptNet作为seed set。文章说也可以用其他数据集，因为COMET是domain-agnostic的。

**Initialization**：基本和GPT训练好的保持一致。一些新添加进去的比如oReact等是由标准正态分布sample出来的。

**Hyperparameters**：和GPT一样，12层，hidden维度是768，12个attention heads。用了0.1的dropout，GeLU作为激活函数。训练时的batch size是64。

#### 4 Experiments

本部分介绍在ATOMIC和ConceptNet上做实验的一些细节。

自动化评价指标使用了BLEU-2指标、全新的sro tuple比例 (% N/T sro)、新生成的object比例 (% N/T o)、新生成的unique的object比例 (% N/U o)。手工评价在Amazon Mechanical Turk上建立了一些任务，志愿者们对其进行评价。COMET用的是Transformer，文章与只使用seq2seq的模型进行了对比（其实就是ATOMIC里边最初用到的那个），以及自己模型不用pre-trained好的参数做对比。结果是COMET相比于seq2seq、以及未pre-trained的模型，效果均有较大的提升。

**结果**：较ATOMIC那些基础的模型，整体上都有很大提升。自动评价指标有51%的提升。人工评价的指标也有18%的提升。COMET生成的tuple (object) 在质量和数量上均有较大提升。使用pre-trained的参数和随机初始化的参数相比，效果有14%的提升，说明通过GPT模型学到的自然语言表示的信息可以被迁移到生成自然语言的常识之水中去。（***什么是beam search和gold ATOMIC (distribution)？***）另外，模型只用10%的数据训练，效果也说得过去，并且使用pre-trained语言模型的COMET效果确实要比未使用pre-trained的要好。

ATOMIC：

![image-20190722234605110](/Users/flyhero/Library/Application Support/typora-user-images/image-20190722234605110.png)

ConceptNet：

![image-20190723001339757](/Users/flyhero/Library/Application Support/typora-user-images/image-20190723001339757.png)

#### Conclusion

本文提出了一种Commonsense Transformer，用于自动构建常识知识三元组。模型个在ATOMIC和ConceptNet上的自动、人为评价指标都达到了很好的效果。