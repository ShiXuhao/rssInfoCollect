import os
from openai import OpenAI
from attitudeCal import get_info_impact_details

def generate_prompt():
    return """
    --------------------------------
    你是一名资深的行业自媒体写手，擅长撰写行业动态快讯。
    识别以上资讯中的ai相关资讯，尽可能充分地将其整理为一份24小时快讯；采用简洁明了的风格，避免冗长。正文约500~1000字；并在末尾以Markdown链接格式附上原文标题及链接。
    语言风格与以上资讯保持一致，专业、直接，具备媒体人的风格；确保你的语言语法简单易懂、且正确。
    直接从正文开始，不要有其他任何文字。
    """

def create_openai_client():
    return OpenAI(
        api_key=os.getenv("DOUBAO_API_KEY"),
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
