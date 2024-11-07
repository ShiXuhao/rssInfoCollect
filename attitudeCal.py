import json

def get_info_impact_details(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    result = {
        'total': 0,
        'positive': [],
        'neutral': [],
        'negative': []
    }
    
    for item in data:
        rel_rank = item['sentiment']['relevance']['relRank']
        info_impact = item['sentiment']['relevance']['infoImpact']
        
        if rel_rank >= 1:
            entry = {
                'title': item['title'],
                'source': item['source'],
                'link': item['link'],
                'description': item['description'][:300],
                'keyFacts': item['sentiment']['keyFacts'],
                'section': item['section']
            }
            
            if info_impact == 1:
                result['positive'].append(entry)
            elif info_impact == -1:
                result['negative'].append(entry)
            elif info_impact == 0:
                result['neutral'].append(entry)
            
            result['total'] += 1
    
    return result

# Example usage
if __name__ == "__main__":
    info_impact_details = get_info_impact_details('data/sentimentData.json')
    print(info_impact_details)