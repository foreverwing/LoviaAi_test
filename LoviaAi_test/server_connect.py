import paramiko
import logging
import os
from datetime import datetime

# 配置日志
log_dir = "server_log/server_connect"
os.makedirs(log_dir, exist_ok=True)  # 自动创建目录，若目录已存在则不做任何操作
log_file = os.path.join(log_dir, f"server_connect_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    filename=log_file,  # 日志文件名
    level=logging.INFO,  # 日志级别
    format="%(asctime)s - %(levelname)s - %(message)s"  # 日志格式
)


def connect_to_server(host, username, password, remote_log_path, port=22):
    """
    连接到远程服务器，进入指定目录，并返回日志文件对象
    :param host: 远程服务器的 IP 地址
    :param username: 远程服务器的 SSH 用户名
    :param password: 远程服务器的 SSH 密码
    :param remote_log_path: 日志文件的路径（包含日期）
    :param port: SSH 连接的端口号，默认为 22
    :return: 客户端对象、SFTP 客户端对象、日志文件对象
    """
    try:
        # 创建 SSH 客户端实例
        client = paramiko.SSHClient()
        # 自动添加 host key
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        logging.info(f"Attempting to connect to server {host} on port {port}...")

        # 连接到远程服务器（使用端口22）
        client.connect(host, username=username, password=password, port=port)

        # 连接成功时，输出调试信息
        logging.info(f"Successfully connected to server {host} on port {port}")

        # 获取 SFTP 客户端
        sftp_client = client.open_sftp()

        # 进入目录 /www/wwwroot/ai-rp-server/runtime/logs
        sftp_client.chdir('/www/wwwroot/ai-rp-server/runtime/logs')
        logging.info("Entered /www/wwwroot/ai-rp-server/runtime/logs directory.")


        # 获取今天的日期并生成日志文件名
        today_date = datetime.now().strftime("%Y-%m-%d")
        remote_log_path = remote_log_path.replace("{date}", today_date)

        logging.info(f"Trying to open log file at path: {remote_log_path}")

        try:
            remote_file = sftp_client.open(remote_log_path, 'r')
            logging.info(f"Log file {remote_log_path} opened successfully.")
            return client, sftp_client, remote_file
        except FileNotFoundError:
            logging.error(f"Log file {remote_log_path} not found.")
            raise

    except Exception as e:
        logging.critical(f"Failed to connect to server: {e}")
        raise
