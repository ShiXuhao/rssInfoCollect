import os
from openai import OpenAI

prompt = """

"""

client = OpenAI(
    api_key = "9b64d9ac-3c5d-4cd6-8c04-b6381c9ce920",
    base_url = "https://ark.cn-beijing.volces.com/api/v3",
)


def essay_writer(item):
    item = str(item)
    print("----- standard writer -----")
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