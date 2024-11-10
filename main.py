import json
from infoDownloader import get_last_24h, load_rss_urls, fetch_feed_data
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

emailList = ["563142863@qq.com","564786816@qq.com","wjjhenry@163.com","519769912@qq.com"]

def send_email(subject, body, to_emails):
    from_email = "sxh035068@gmail.com"
    from_password = "empa kbvk rbzg iuui"

    for to_email in to_emails:
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
            logging.info(f"邮件发送成功至 {to_email}")
        except smtplib.SMTPException as e:
            logging.error(f"邮件发送失败至 {to_email}: {e}")
        except Exception as e:
            logging.error(f"发送至 {to_email} 时发生未知错误: {e}")

def main():
    try:
        # 数据下载
        rss_urls = load_rss_urls()
        all_feed_data = []
        time_threshold = get_last_24h()  # 获取24小时前的时间戳
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

        # 获取当前时间戳
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 发送邮件
        send_email(f"AI行业动态快讯 - {current_time}", essay, emailList)
    except Exception as e:
        logging.error(f"程序运行失败: {e}")
        # 发送告警邮件，同样包含时间戳
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        error_msg = f"程序运行失败,错误信息:\n{str(e)}"
        send_email(f"AI行业动态快讯 - 运行异常 - {current_time}", error_msg, emailList)

if __name__ == "__main__":
    main()
