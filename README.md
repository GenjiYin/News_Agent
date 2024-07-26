# 以deepseek为大脑的新闻数据分析的Agent

## 1. 使用前请在LLM.py文件中填写deepseek_api, api获取地址: https://www.deepseek.com/zh, 以及tavily的api, 获取地址为: https://app.tavily.com/home; 
## 2. 使用test.ipynb导入新闻二维表格, 导入的表格格式请参考第二个block, 从头到尾运行即可; 
## 3. news.csv是我提供的样例数据. 

## 4. 项目思路: 
1. 对传入的表格数据转化为特定形式的字典;
2. 字典传入query当中；
3. 在query中定义输出格式;
4. 定义一个函数可以解析大模型的输出结果并转化为DataFrame.
