"""
提示词(需要说明)
{
    '标的代码': ['新闻1', '新闻2']
}
新闻的标准格式: 据XXX报社于2024年XX月XX日报道, 
"""
import pandas as pd

def split_news_securities(df, news_col='title', securities_col='related_instruments'):   
    """
    一条新闻可能对应多个标的
    """ 
    other_cols = [col for col in df.columns if col not in [news_col, securities_col]]
    def split_securities(row):
        securities = row[securities_col].split(',')
        return [(row[news_col], security, *[row[col] for col in other_cols]) for security in securities]
    exploded_data = df.apply(split_securities, axis=1).explode()
    exploded_df = pd.DataFrame(exploded_data.tolist(), columns=[news_col, securities_col] + other_cols)
    return exploded_df

def table_to_query(df):
    """
    将新闻数据转化为query
    :params df: 新闻数据
    |related_instruments|title|publish_time|source|
    related_instruments: 关联标的
    title: 文本标题
    publish_time: 发布日期
    source: 报道源
    
    :return:
    返回字典数据, {'标的名称': ['新闻1', '新闻2', ...], ''}
    """
    df = split_news_securities(df)
    df['content'] = df['source'] + '于' + df['publish_time'].apply(lambda x: x.strftime('%Y-%m-%d')) + '时刻发表了一篇关于: "' + df['title'] + '"的报道'
    df = df[['related_instruments', 'content']]
    df = df.groupby('related_instruments').apply(lambda x: list(x['content'])).to_dict()
    return df

# 传入的query的格式
query_type = """
{
    '股票代码1': ['新闻1', '新闻2'], 
    '股票代码2': ['新闻3', '新闻4', '新闻5'], 
    '股票代码3': ['新闻6', '新闻7'], 
    '股票代码4': ['新闻8'], 
    ......
}
"""

output_type = """
{
    "search_content" : 这里是你搜索的内容, 如果没有调用'search'函数, 则值0
    "股票代码1": {
        respone: {
            "news_content": 新闻1的内容, 
            "date": 新闻报道的日期, 
            "score": 你给出的打分, 
            "reason": 你给出这个分数的理由
        }, 
        respone: {
            "news_content": 新闻2的内容, 
            "date": 新闻报道的日期, 
            "score": 你给出的打分, 
            "reason": 给出这个分数的理由
        }, 
        ......
    }, 
    "股票代码2": {
        respone: {
            "news_content": 新闻的内容, 
            "date": 新闻报道的日期, 
            "score": 你给出的打分, 
            "reason": 你给出这个分数的理由
        }, 
        ....
    }, 
    ......
}
"""

# prompt模板
main_prompt = """
请你对以下股票新闻进行打分, 并给出打分的理由. 0分表示新闻利空, 1分表示新闻中性, 2分表示新闻利好. 请根据新闻标题和搜索得到的新闻内容判断其对股票的影响. 

输入的目标格式: 
{query_type}

目标:
{query}

搜索内容会储存在以下内容当中: 
{agent_scratch}

你只能输出以下格式的内容, 禁止输出除以下内容以外的其他文字: 
{output_type}
这个格式是可以被python语言中的eval转化为字典的
"""

def generate_prompt(query, agent_scratch={}):
    """
    产生prompt
    """
    promt = main_prompt.format(
        query=query, 
        query_type=query_type, 
        output_type=output_type, 
        agent_scratch=agent_scratch, 
    )
    return promt
    