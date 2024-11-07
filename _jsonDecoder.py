import json

def json_decoder(jsonSting:str) -> dict:
    left_point = jsonSting.find("{")
    right_point = jsonSting.rfind("}")
    target_string = jsonSting[left_point:right_point+1]
    return json.loads(target_string)


if __name__ == "__main__":
    data = """```json
{
    "relevance":{
        "entityRel": true,
        "prodRel": false,
        "techRel": false,
        "PolicyRel": false,
        "activityRel": false,
        "relRank": 1
    },
    "keyFacts": "10月30日三六零放量上涨1.62%，周鸿祎称人工智能是打造新质生产力的核心引擎。"
}
```"""
    print(json_decoder(data))