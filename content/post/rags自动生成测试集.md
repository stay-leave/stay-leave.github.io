---
title: "Rags自动生成测试集"
date: 2024-12-07T21:59:29+08:00
lastmod: 2024-12-07T21:59:29+08:00
draft: false
categories: ["RAG"]
tags: ["评测", "测试集"]
---

搭建一个RAG只需要一下午，但是优化却要一年。RAG的评估至关重要，现在最流行的就是RAGS了，社区非常活跃。

关于评估的指标，无非是从检索、生成、端到端这三部分来评估。
[参见](https://blog.csdn.net/qq_43814415/article/details/141229613)

今天的实践是自动生成测试集。官网链接：[链接](https://docs.ragas.io/en/latest/getstarted/rag_testset_generation/#knowledgegraph-creation)

后续真正能用的测试集，还得是自己定义数据加载方法，也可以把数据库的记录导出来。
还有非英语的处理，还有多种角色的定义。

## 数据加载

需要任意格式的文件。RAGS是默认使用langchain加载数据的，但是会报错：file is not a zip file的bug，需要安装nltk，[bug链接](https://github.com/langchain-ai/langchain/discussions/8212)，但是国内又下不了。

于是采用llama_index。代码是：

```python
path = "/root/RAG/evalation/Sample_Docs_Markdown/"
documents = SimpleDirectoryReader(path).load_data()
print("数据集加载完毕")
```

但是用llama_index会在下面生成的时候报错：

```python
NameError: name 'LCDocument' is not defined
```

需要先去本地的Python环境里找到对应的源码，把if t.type一行删除。[github链接](https://github.com/explodinggradients/ragas/issues/1695)

我本地的参考路径：

/root/miniconda3/envs/MinerU/lib/python3.10/site-packages/ragas/testset/synthesizers/generate.py

看到这个源码，其实要的就是Document的text，我们自己手动构造一个也是可以的，这样的分块更为合理，但是要至少每块100个token，不然会报错文本太少，信息量不足。

## 加载模型，实例化生成类

这里使用deepseek的大模型，使用本地的bce向量模型。

代码：

```python
generator_llm = LangchainLLMWrapper(ChatOpenAI(model="deepseek-chat", base_url="https://api.deepseek.com", api_key=""))
generator_embeddings = LangchainEmbeddingsWrapper(HuggingFaceEmbeddings(model_name="/root/RAG/models/bce-embedding-base_v1"))

generator = TestsetGenerator(llm=generator_llm, embedding_model=generator_embeddings)
print("模型加载完毕")
```

## 生成测试集

代码：

```python
dataset = generator.generate_with_llamaindex_docs(documents, testset_size=10)

df = dataset.to_pandas()
print(df.info())
```

测试集样例：

```python
RangeIndex: 11 entries, 0 to 10
Data columns (total 4 columns):
 #   Column              Non-Null Count  Dtype 
---  ------              --------------  ----- 
 0   user_input          11 non-null     object
 1   reference_contexts  11 non-null     object
 2   reference           11 non-null     object
 3   synthesizer_name    11 non-null     object
dtypes: object(4)
memory usage: 480.0+ bytes
```

设置的10个，但是生成了11个。可控性很差。

结果如下:
![2](/b_images/2024_12_7/2.png)

## 生成测试集的原理

思路：创建知识图谱，生成测试集。

### 1.创建知识图谱

1.创建一个空的 KnowledgeGraph 对象，这是存储文档信息和其关系的容器。

```python
from ragas.testset.graph import KnowledgeGraph
kg = KnowledgeGraph()
```

2.将文档添加到知识图谱。

```python
# convert the documents to Ragas nodes
nodes = []
for doc in documents:
            if doc.text is not None and doc.text.strip() != "":
                node = Node(
                    type=NodeType.DOCUMENT,
                    properties={
                        "page_content": doc.text,
                        "document_metadata": doc.metadata,
                    },
                )
                nodes.append(node)

kg = KnowledgeGraph(nodes=nodes)
```

3.应用转换

这个转换就是把文档，大模型，向量模型集合起来。得到更为丰富的知识图谱。

```python
# create the transforms
transforms = default_transforms(
                documents=[LCDocument(page_content=doc.text) for doc in documents],
                llm=llm_for_transforms,
                embedding_model=embedding_model_for_transforms,
            )
```

最后的知识图谱的内容，大模型负责总结摘要，向量模型负责向量化摘要。
![1](/b_images/2024_12_7/1.png)

### 2.测试集生成

1.创建测试集生成器

使用上面增强后的知识图谱实例化这个类。

```python
from ragas.testset import TestsetGenerator

generator = TestsetGenerator(llm=generator_llm, embedding_model=embedding_model, knowledge_graph=loaded_kg)
```

2.定义查询分布

默认的查询类型占比是2:1:1

SingleHopSpecificQuery: 单跳特定查询
MultiHopAbstractQuery: 多跳抽象查询
MultiHopSpecificQuery: 多跳特定查询

```python
from ragas.testset.synthesizers import default_query_distribution

query_distribution = default_query_distribution(generator_llm)

[
    (SingleHopSpecificQuerySynthesizer(llm=llm), 0.5),
    (MultiHopAbstractQuerySynthesizer(llm=llm), 0.25),
    (MultiHopSpecificQuerySynthesizer(llm=llm), 0.25),
]
```

3.生成

## 适应非英语语料

官方教程：
[https://docs.ragas.io/en/latest/howtos/customizations/testgenerator/_language_adaptation/](https://docs.ragas.io/en/latest/howtos/customizations/testgenerator/_language_adaptation/)

## 定义不同提问角色

官方教程：
[https://docs.ragas.io/en/latest/howtos/customizations/testgenerator/_persona_generator/](https://docs.ragas.io/en/latest/howtos/customizations/testgenerator/_persona_generator/)

## 参考

[https://blog.csdn.net/qq_43814415/article/details/141229613](https://blog.csdn.net/qq_43814415/article/details/141229613)
[https://blog.csdn.net/qq_43814415/article/details/138358371](https://blog.csdn.net/qq_43814415/article/details/138358371)
[https://blog.csdn.net/m0_59235945/article/details/143027480](https://blog.csdn.net/m0_59235945/article/details/143027480)
[https://docs.ragas.io/en/latest/getstarted/rag_testset_generation/](https://docs.ragas.io/en/latest/getstarted/rag_testset_generation/)
