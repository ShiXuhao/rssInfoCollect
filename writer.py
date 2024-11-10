import os
from openai import OpenAI
from attitudeCal import get_info_impact_details

def generate_prompt():
    return """
    --------------------------------
    你是一名资深的行业自媒体写手，擅长撰写行业动态快讯。
    基于以上信息，撰写24小时内AI行业动态快讯，采用简洁明了的风格，避免冗长。正文约500~1000字，按照总-分-总结构行文，并在末尾以Markdown链接格式附上原文标题及链接。
    直接从正文开始，不要有其他任何文字。
    """

def create_openai_client():
    return OpenAI(
        api_key="39798ab9-8c18-4918-aa76-07c1cfdcfcf7",
        base_url="https://ark.cn-beijing.volces.com/api/v3",
    )

def essay_writer(client, item):
    item = str(item)
    if not item or len(item) < 200:
        raise ValueError("输入内容为空或少于200字,无法生成文章")
        
    print("----- standard writer -----")
    user_prompt = item + generate_prompt()
    completion = client.chat.completions.create(
        model="ep-20241108133037-5vrjf",  # your model endpoint ID
        messages=[
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=2048,
        stream=False
    )
    return completion.choices[0].message.content

if __name__ == "__main__":
    client = create_openai_client()
    info_impact_details = get_info_impact_details('data/sentimentData.json')
    data = str(info_impact_details)
    essay = essay_writer(client, data)
    print(essay)
