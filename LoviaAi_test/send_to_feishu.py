import requests
import json
import logging
import os
from datetime import datetime

# 配置日志
log_dir = "server_log/send_to_feishu"
os.makedirs(log_dir, exist_ok=True)  # 自动创建目录，若目录已存在则不做任何操作
log_file = os.path.join(log_dir, f"send_to_feishu_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    filename=log_file,  # 日志文件名
    level=logging.INFO,  # 日志级别
    format="%(asctime)s - %(levelname)s - %(message)s"  # 日志格式
)
# Feishu Webhook URL
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/2e03c402-e5e3-45ab-803c-9ae4d55c3601"

def send_error_to_feishu(error_message):
    """
    发送错误信息到飞书
    :param error_message: 错误信息
    """
    # 在错误信息前添加 "黄菠萝提醒您："
    full_message = "黄菠萝提醒您：\n" + error_message
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "msg_type": "text",
        "content": {
            "text": full_message  # 加上提醒文本的完整错误消息
        }
    }

    try:
        # 发送错误信息到 Feishu
        response = requests.post(FEISHU_WEBHOOK_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # 如果返回状态码不是 200，会抛出异常
        logging.info(f"Successfully sent message to Feishu: {full_message}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send error message to Feishu: {e}")
