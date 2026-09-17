---
title: "Deepresearch的MCP实践"
date: 2025-04-06T17:51:29+08:00
lastmod: 2025-04-06T17:51:29+08:00
draft: false
categories: ["Agent"]
tags: ["MCP", "DeepResearch"]
---

deepresearch是目前最流行的大模型应用范式，将agent应用于调研报告上，实现了用户只需要输入自己的问题，大模型自动搜索信息完成报告的过程。

区别于rag的单次检索过程和定制化的流程，deepresearch建立在deepsearch的的基础上，由LLM自主控制整个流程。
deepsearch的核心在于搜索、阅读、推理的循环。接收到查询时，进行搜索和阅读，然后根据当前搜索结果，决定是否终止或是扩展查询继续搜索。
参考：
[https://jina.ai/news/a-practical-guide-to-implementing-deepsearch-deepresearch](https://jina.ai/news/a-practical-guide-to-implementing-deepsearch-deepresearch)

本项目，就是基于MCP工具的deepresearch实现。首先定义了满足MCP协议的工具，主要是本地知识库检索工具、网络检索工具、混合检索工具。然后建立MCP客户端，与工具函数进行链接，从而将不同类型的工具，以统一的方式集成到项目。

## 满足MCP协议的工具

无需手动定义工具的类型、参数等，直接用mcp库封装，只需要编写实际可执行的函数即可。

```gdscript3
# 本地知识库检索
@mcp.tool()
def retrieve(query: str) -> str:
    """本地知识库检索"""
    iteration_limit = 3  # 最大迭代次数
    iteration = 0
    aggregated_contexts = []  # 聚合的检索结果
    all_search_queries = []   # 所有查询记录
    
    # 初始查询改写
    current_query = rewrite_query(query)
    all_search_queries.append(current_query)

    while iteration  str:
        """使用 LLM 和 MCP 服务器提供的工具处理查询"""
        # 列出所有的工具
        response = await self.session.list_tools()
        
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in response.tools]
        print(f'available_tools:\n{available_tools}')
        
        # 初始规划，选择工具，返回工具名称和参数
        messages = [
            {
                "role": "system",
                "content": prompts["SYSTEM_PROMPT"] + str(available_tools)
            },
            {
                "role": "user",
                "content": query
            }
        ]
        response = self.client.chat.completions.create(
                model=model_name,
                messages=messages
            )
        
        message = response.choices[0].message
        print(f'llm_output(tool call)：{message.content}') # 这一步直接给我返回大模型的结果了，无语
        
        # 确定好工具，进行循环
        results = [] # 工具返回的结果聚合
        while True:
            
            flag, json_text = get_clear_json(message.content)# 根据是否能解析出json，执行不同的方法
            
            if flag == 0: # 没有生成json格式，直接用大模型生成回复
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": query}]
                )
                return response.choices[0].message.content
            
            # 成功生成json，解析出工具名和参数
            json_text = json.loads(json_text)
            tool_name = json_text['name']
            tool_args = json_text['params']
            # 执行工具函数，获得返回值
            result = await self.session.call_tool(tool_name, tool_args)
            print(f'tool name: \n{tool_name}\ntool call result: \n{result}')
            results.append(result.content[0].text)
            
            # 把返回工具回复加入历史消息列表
            messages.append({
                "role": "assistant",
                "content": message.content
            })
            messages.append({
                "role": "user",
                "content": f'工具调用结果如下：{result}'
            })
            
            # 在工具调用完成后，由大模型决定是否结束检索，还是继续检索
            messages.append({
                "role": "user",
                "content": prompts["NEXT_STEP_PROMPT"].format(query)
            })
            
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages
            )
            
            message = response.choices[0].message
            print(f'llm_output：\n{message.content}')
            # 检查是否该结束
            if 'finish' in message.content:
                break
            
            # 继续检索，就把大模型的回复加入历史消息，继续循环
            messages.append({
                "role": "assistant",
                "content": message.content
            })
        
        # 循环终止后，进入报告撰写阶段
        messages.append({
                "role": "user",
                "content": prompts["FINISH_GENETATE"].format('\n\n'.join(results), query)
                })
        
        response = self.client.chat.completions.create(
                model=model_name,
                messages=messages
            )
        # 返回报告内容
        message = response.choices[0].message.content
        return message
    

    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                print(response)
            except Exception as e:
                print(f"\nError: {str(e)}")
```

## 注意事项

1.LLM一定要满足：上下文窗口比较长，人类对齐能力强。否则无法容纳长文本的检索结果，或者无法成功调用工具。

2.无论是网络检索，还是本地检索，都只是信息检索的一种具体路径。
