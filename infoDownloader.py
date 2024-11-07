import json
import feedparser
import uuid
# from judgers import stringJudge as judge
from _judgers import testJudge as judge
from datetime import datetime

def load_rss_urls():
    """
    从rssUrlList.json文件中加载RSS源配置
    返回: 包含RSS源信息的字典列表
    """
    try:
        with open('config/rssUrlList.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载RSS配置文件失败: {e}")
        return []

def fetch_feed_data(url, source_name, section_name, judge, time_threshold_str=None):
    """
    获取指定URL的RSS源数据
    参数:
        url: RSS源的URL地址
        source_name: RSS源的名称
        section_name: RSS源的板块名称
        time_threshold_str: 时间阈值字符串,格式为'YYYY-MM-DD HH:MM:SS',只返回该时间后的数据
    返回:
        包含每个推送条目信息的列表,每个条目包含:
        - title: 标题
        - link: 链接
        - description: 描述
        - published: 发布日期
        - id: 条目ID
        - source: 来源名称
        - section: 板块名称
    """
    print(f"正在获取 {url} 的数据...")
    feed = feedparser.parse(url)
    
    import concurrent.futures
    
    # 如果没有提供时间阈值,则不进行时间过滤
    time_threshold = None
    if time_threshold_str:
        try:
            time_threshold = datetime.strptime(time_threshold_str, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"解析时间阈值失败: {e}")
            return []
    
    def process_entry(entry):
        try:
            published_str = entry.get('published', '')
            # 使用feedparser的时间解析功能
            published_struct = entry.get('published_parsed')
            if published_struct:
                published_time = datetime(*published_struct[:6])
            else:
                # 如果published_parsed不可用，尝试手动解析常见的RSS日期格式
                from email.utils import parsedate_to_datetime
                published_time = parsedate_to_datetime(published_str)
            
            # 只添加在时间阈值之后的条目
            if not time_threshold or published_time >= time_threshold:
                entry_data = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'description': entry.get('description', ''),
                    'published': published_time.strftime('%Y-%m-%d %H:%M:%S'),  # 统一输出格式
                    'id': str(uuid.uuid4()),
                    'source': source_name,
                    'section': section_name
                }
                if judge(entry_data):
                    return entry_data
        except Exception as e:
            print(f"解析发布时间失败: {e}")
            return None
            
    entries = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_entry = {executor.submit(process_entry, entry): entry for entry in feed.entries}
        for future in concurrent.futures.as_completed(future_to_entry):
            result = future.result()
            if result:
                entries.append(result)
                
    print(f"{source_name}-{section_name} 获取到 {len(entries)} 条资讯")
    return entries

def fetch_all_feeds(time_threshold_str, judge):
    """
    获取所有RSS源的数据并保存到DATA.json文件
    """
    data = load_rss_urls()
    feed_result_list = []
    total_count = 0
    for source in data:
        source_count = 0
        for section_name, url in source['feeds'].items():
            feed_result = fetch_feed_data(
                url,
                source['name'],
                section_name,
                time_threshold_str=time_threshold_str,
                judge = judge
            )
            feed_result_list.extend(feed_result)
            source_count += len(feed_result)
        total_count += source_count
        print(f"{source['name']} 总计获取到 {source_count} 条资讯")
    
    print(f"所有来源总计获取到 {total_count} 条资讯")
    with open('data/rawData.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(feed_result_list, ensure_ascii=False))

def get_today_midnight():
    """获取当前时间最近一个凌晨的时间戳"""
    now = datetime.now()
    today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return today_midnight.strftime('%Y-%m-%d %H:%M:%S')


if __name__ == "__main__":
    time_threshold = get_today_midnight()
    fetch_all_feeds(time_threshold, judge=judge)