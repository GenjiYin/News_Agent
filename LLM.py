import os
import pandas as pd
import numpy as np
from langchain_community.tools.tavily_search import TavilySearchResults
from openai import OpenAI
deepseek_api = 'sk-09b2df08a3b2499189b7087b4a5ba98e'

os.environ['TAVILY_API_KEY'] = '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'

from prompt import table_to_query, generate_prompt

def search(query):
    """
    传入的query是字典型的新闻数据
    """
    def extract_quoted_content(input_string):
        import re
        # 使用正则表达式匹配双引号内的内容
        pattern = r'"(.*?)"'  # 匹配双引号内的内容
        matches = re.findall(pattern, input_string)[0]  # 找到所有匹配
        return matches
    
    contents = {}
    instruments = list(query.keys())
    tavily = TavilySearchResults(max_results=2)
    for ins in instruments:
        titles = query[ins]
        content = []
        for t in titles:
            try:
                ret = tavily.invoke(input=extract_quoted_content(t))
                content.append(ret[0]['content'])
            except Exception as err:
                print(f'{ins} {t} 新闻抓取失败: {err}')
                continue
        contents[ins] = content
    return contents

def dict_to_dataframe(data):
    """
    将包含股票信息的字典转换为 DataFrame。
    
    参数:
    data (dict): 包含股票信息的字典
    
    返回:
    pd.DataFrame: 转换后的 DataFrame，包含 date, instrument, score, reason 列
    """
    rows = []
    for instrument, details in data.items():
        if instrument == 'search_content':
            continue
        response = details['respone']
        row = {
            'date': response['date'],
            'instrument': instrument,
            'score': response['score'],
            'reason': response['reason']
        }
        rows.append(row)

    return pd.DataFrame(rows)

def call_llm(table):
    """
    考虑到任务的特殊性, 为了避免模型幻觉的出现, 事先调用搜索接口, 让模型了解新闻内容
    :params table: 传入你要分析的新闻数据, 这个数据是DataFrame类型的
    :params news_content: 大模型输出的新闻内容数据
    """
    max_try = 10          # 需要循环执行大模型
    query = table_to_query(table)         # 将数据转化为提示词
    news_content = search(query)          # 获取新闻的文本内容
    prompt = generate_prompt(query, news_content)
    client = OpenAI(api_key=deepseek_api, base_url="https://api.deepseek.com").chat.completions.create
    
    for _ in range(max_try):
        try:
            messages=[
                {"role": "system", "content": prompt}, 
            ]
            messages.append({'role': 'user', 'content': '请为我解决目标问题'})
            response = client(
                model="deepseek-chat", 
                messages=messages, 
                stream=False
            )
            result = eval(response.choices[0].message.content.replace('json', '').replace('```', ''))
            return dict_to_dataframe(result)
        except Exception as err:
            print('模型加载失败 {}'.format(err))
            return {}

if __name__ == '__main__':
    df = [['抵御价格波动风险，龙头猪企参与套期保值', pd.to_datetime('2023-07-01 03:54:29'), '快兰斯24小时财经', '01109.HK,600525.SZ']]
    df = pd.DataFrame(df, columns=['title', 'publish_time', 'source', 'related_instruments'])
    print(call_llm(df))