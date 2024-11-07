def testJudge(target):
    return True


def stringJudge(target):
    keywords = ['AI','ai','人工智能','gpt','GPT','claude','Claude','anthropic','Anthropic','glm','GLM','智谱','minimax','MINIMAX', '文心', '通义', '豆包', '百川']
    text = target['title']+target['description']
    for keyword in keywords:
        if keyword in text:
            print(keyword)
            return True
    return False