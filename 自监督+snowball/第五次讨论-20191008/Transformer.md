## Transformer

模型结构图：

![image-20190812202201137](/Users/flyhero/Library/Application Support/typora-user-images/image-20190812202201137.png)

Encoder：由6个相同的层构成。每个层含有两个子层。

#### Multi-Headed Attention 自注意力机制

首先，将Encoder的输入（每个词的Embedding）变为三个向量。为每个词创建一个Query向量，一个Key向量，一个Value向量。这三个向量是由词嵌入的向量乘以训练得出的三个矩阵得到的。

