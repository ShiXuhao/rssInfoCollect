import json

def count_total_tokens(file_path='data/sentimentData.json'):
    total_tokens = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if 'tokens' in item:
                    total_tokens += item['tokens']
    except Exception as e:
        print(f"Error reading file: {e}")
        return 0
    return total_tokens

if __name__ == "__main__":
    total = count_total_tokens()
    print(f"Total tokens: {total}")
