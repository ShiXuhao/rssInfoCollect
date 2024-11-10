from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import os
from openai import OpenAI
import json
from _jsonDecoder import json_decoder


prompt = """
---
判断上文是否与ai/人工智能/机器学习/深度学习等产业相关，然后概括其核心事实。
以如下json输出：
```json
{
    "keyFacts":...,
    "keyWords":...,
    "relevance":{
        "titleRel":...,
        "entityRel":...,
        "prodRel":...,
        "PolicyRel":...,
        "activityRel":...,
        "relRank":...,
        "infoImpact":...
    }
}
```
keyFacts:string，使用零度视角，一句话概括文章核心事实。
keyWords:string，使用零度视角，一句话概括文章核心关键词。
relevance:json object，根据全文，描述此资讯与行业的相关性，包含以下维度：
* titleRel:bool，描述标题是否与ai/人工智能/机器学习/深度学习相关；
* entityRel:bool，描述文中是否出现了与ai/人工智能/机器学习/深度学习相关的主体，包括人物/组织/公司等；
* prodRel:bool，描述文中是否出现了与ai/人工智能/机器学习/深度学习相关的产品或服务，包括软件/硬件/服务模式等；
* techRel:bool，描述文中是否出现了与ai/人工智能/机器学习/深度学习相关的技术或研究成果；
* PolicyRel:bool，描述文中是否出现了与ai/人工智能/机器学习/深度学习相关的政策；
* activityRel:bool，描述文中是否出现了与ai/人工智能/机器学习/深度学习相关的活动；
* relRank:int，记录上述所有项中，为True的数量；
* infoImpact:int，记录此资讯对ai/人工智能/机器学习/深度学习相关行业的影响，包含以下选项：
    * 0：无影响
    * 1：正面影响
    * -1：负面影响

"""

client = OpenAI(
    api_key=os.getenv("DOUBAO_API_KEY"),
    base_url = "https://ark.cn-beijing.volces.com/api/v3",
)


def sentiment_analysis(item):
    item = str(item)
    print("----- standard request -----")
    user_prompt = item+prompt
    completion = client.chat.completions.create(
        model = "ep-20241108133037-5vrjf",  # your model endpoint ID
        messages = [
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=2048,
        stream=False
    )

    try:
        result = json_decoder(completion.choices[0].message.content)
        tokens = completion.usage.total_tokens
    except:
        print(completion.choices[0].message.content)
        result = None
        tokens = 0
    return result, tokens

def process_item(item):
    result, tokens = sentiment_analysis(item)
    print(result)
    new_item = item.copy()
    new_item['sentiment'] = result
    new_item['tokens'] = tokens
    # 计算时间得分
    try:
        # 获取当前时间和消息时间
        current_time = datetime.now()
        msg_time = datetime.strptime(new_item['published'], '%Y-%m-%d %H:%M:%S')
        
        # 计算时间差(小时)
        time_diff = (current_time - msg_time).total_seconds() / 3600
        
        # 计算得分:24小时前为0分,当前为1分,线性分布
        if time_diff >= 24:
            time_score = 0
        elif time_diff <= 0:
            time_score = 1
        else:
            time_score = round((24 - time_diff) / 24, 2)
            
        new_item['time_score'] = time_score
    except:
        new_item['time_score'] = 0
    
    # 计算最终得分
    try:
        final_score = new_item['sentiment']['relevance']['relRank'] * new_item['time_score']
        new_item['final_score'] = round(final_score, 2)
    except:
        new_item['final_score'] = 0
    return new_item

def process_data_with_threads(raw_data, output_file, max_workers=15):
    """
    使用多线程处理数据并保存结果
    
    Args:
        raw_data: 待处理的原始数据列表
        output_file: 输出文件路径
        max_workers: 最大线程数,默认20
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            new_data = list(executor.map(process_item, raw_data))
            json.dump(new_data, f, ensure_ascii=False, indent=4)
    return new_data

if __name__ == "__main__":
    # 加载原始数据
    with open('data/rawData.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # 处理数据并保存
    process_data_with_threads(raw_data, 'data/sentimentData.json')
                # 将result从代码块中抽取并处理为python list[dict]