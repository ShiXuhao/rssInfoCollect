import json
from infoDownloader import get_today_midnight, load_rss_urls, fetch_feed_data
from sentimentAnalysisUnit import process_data_with_threads
from attitudeCal import get_info_impact_details
from writer import create_openai_client, essay_writer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from _judgers import testJudge as judge
import logging
from datetime import datetime

# 配置日志记录
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

emailList = ["564786816@qq.com"]

def send_email(subject, body, to_email):
    from_email = "sxh035068@gmail.com"
    from_password = "empa kbvk rbzg iuui"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        logging.info("邮件发送成功")
    except smtplib.SMTPException as e:
        logging.error(f"邮件发送失败: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}")

def main():
    try:
        # 数据下载
        rss_urls = load_rss_urls()
        all_feed_data = []
        time_threshold = get_today_midnight()  # 获取当前时间最近一个凌晨的时间戳
        for source in rss_urls:
            for section, url in source['feeds'].items():
                try:
                    feed_data = fetch_feed_data(url, source['name'], section, judge, time_threshold)
                    all_feed_data.extend(feed_data)
                except Exception as e:
                    logging.error(f"获取数据失败: {e}")

        # 使用多线程进行情感分析
        processed_data = process_data_with_threads(all_feed_data, 'data/sentimentData.json')

        # 数据筛选
        info_impact_details = get_info_impact_details('data/sentimentData.json')
        top_30_data = info_impact_details['positive'][:30] + info_impact_details['neutral'][:30] + info_impact_details['negative'][:30]

        # 结果写作
        client = create_openai_client()
        data = json.dumps(top_30_data, ensure_ascii=False)
        essay = essay_writer(client, data)

        # 发送邮件
        send_email("AI行业动态快讯", essay, "564786816@qq.com")
    except Exception as e:
        logging.error(f"程序运行失败: {e}")
        # 发送告警邮件
        error_msg = f"程序运行失败,错误信息:\n{str(e)}"
        send_email("AI行业动态快讯 - 运行异常", error_msg, "564786816@qq.com")

if __name__ == "__main__":
    main()
