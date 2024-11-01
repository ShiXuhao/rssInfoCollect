import os
from openai import OpenAI
import json
from jsonDecoder import json_decoder


prompt = """
---
判断上文是否与特定产业相关，然后概括其核心事实。
以如下json输出：
```json
{
    "relevance":{
        "industry":...,
        "titleRel":...,
        "entityRel":...,
        "prodRel":...,
        "PolicyRel":...,
        "activityRel":...,
        "relRank":...,
        "infoImpact":...
    }
    "keyFacts":...

}
```
relevance:json object，根据全文，描述此资讯与行业的相关性，包含以下维度：
* industry:string，此资讯所属行业，包含以下选项：
    * 人工智能
    * 互联网
    * 硬件设施
    * 数据服务
    * 其他
* titleRel:bool，描述标题是否与industry相关；
* entityRel:bool，描述文中是否出现了与industry相关的主体，包括人物/组织/公司等；
* prodRel:bool，描述文中是否出现了与industry相关的产品或服务，包括软件/硬件/服务模式等；
* techRel:bool，描述文中是否出现了与industry相关的技术或研究成果；
* PolicyRel:bool，描述文中是否出现了与industry相关的政策；
* activityRel:bool，描述文中是否出现了与industry相关的活动；
* relRank:int，记录上述所有项中，为True的数量；
* infoImpact:int，记录此资讯对industry的影响，包含以下选项：
    * 0：无影响
    * 1：正面影响
    * -1：负面影响
keyFacts:string，使用零度视角，一句话概括文章核心事实。
"""

client = OpenAI(
    api_key = "9b64d9ac-3c5d-4cd6-8c04-b6381c9ce920",
    base_url = "https://ark.cn-beijing.volces.com/api/v3",
)


def sentiment_analysis(item):
    item = str(item)
    print("----- standard request -----")
    user_prompt = item+prompt
    completion = client.chat.completions.create(
        model = "ep-20241030145809-ndcw2",  # your model endpoint ID
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

if __name__ == "__main__":
    # Load raw data
    with open('data/rawData.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # Process each item
    new_data = []
    # 使用多线程并发处理数据
    from concurrent.futures import ThreadPoolExecutor
    from functools import partial
    
    def process_item(item):
        result, tokens = sentiment_analysis(item)
        print(result)
        new_item = item.copy()
        new_item['sentiment'] = result
        new_item['tokens'] = tokens
        return new_item
    
    # 使用线程池并发执行
    with open('data/sentimentData.json', 'a', encoding='utf-8') as f:
        with ThreadPoolExecutor(max_workers=20) as executor:
            new_data = list(executor.map(process_item, raw_data))
            
            # 将new_data写入json文件
            json.dump(new_data, f, ensure_ascii=False, indent=4)
                # 将result从代码块中抽取并处理为python list[dict]