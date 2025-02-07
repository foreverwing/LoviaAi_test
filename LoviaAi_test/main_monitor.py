import time
import logging
import os
from datetime import datetime
from server_connect import connect_to_server
from send_to_feishu import send_error_to_feishu

# 配置日志
log_dir = "server_log/main_monitor"
os.makedirs(log_dir, exist_ok=True)  # 自动创建目录，若目录已存在则不做任何操作
log_file = os.path.join(log_dir, f"main_monitor_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    filename=log_file,  # 日志文件名
    level=logging.INFO,  # 日志级别
    format="%(asctime)s - %(levelname)s - %(message)s"  # 日志格式
)

# 初始化连接相关
client = None
sftp_client = None
remote_file = None


def check_existing_log_for_errors(log_file_path):
    """
    检查现有日志文件中是否有错误信息，并将其发送到飞书
    """
    try:
        logging.info(f"Checking existing log file {log_file_path} for errors...")
        with open(log_file_path, "r") as log_file:
            for line in log_file:
                if "error" in line.lower() or "500" in line:
                    logging.info(f"Error found in existing log: {line.strip()}")
                    send_error_to_feishu(line.strip())  # 发送到飞书
    except FileNotFoundError:
        logging.error(f"Log file {log_file_path} not found.")
    except Exception as e:
        logging.critical(f"An error occurred while checking existing log file: {e}")


def monitor_log():
    """
    监控日志文件
    """
    global client, sftp_client, remote_file  # 使用全局变量，允许在其他地方访问并清理资源

    host = "47.91.121.232"  # 远程服务器的 IP 地址
    username = "root"  # 服务器的 SSH 用户名
    password = "Aionspark@2024!@#"  # 服务器的 SSH 密码（或者可以使用密钥认证）

    remote_log_path_template = "webman-{date}.log"  # 日志文件路径模板，{date} 会被当前日期替换

    last_checked_date = None  # 记录上次检查的日期

    while True:
        try:
            today_date = datetime.now().strftime("%Y-%m-%d")
            remote_log_path = remote_log_path_template.replace("{date}", today_date)

            if today_date != last_checked_date:
                logging.info(f"Checking log file for date: {today_date}")
                last_checked_date = today_date

                log_file_exists = False

                while not log_file_exists:
                    try:
                        client, sftp_client, remote_file = connect_to_server(host, username, password, remote_log_path,
                                                                             port=22)
                        log_file_exists = True
                    except FileNotFoundError:
                        logging.info(f"Log file {remote_log_path} not found. Waiting for file to be created...")
                        time.sleep(60)

                logging.info(f"Started monitoring the log file {remote_log_path}.")

                remote_file.seek(0, 2)  # 文件指针移动到文件末尾

                while True:
                    line = remote_file.readline()
                    if line:
                        if 'error' in line.lower() or '500' in line:
                            logging.info(f"Error detected: {line.strip()}")
                            send_error_to_feishu(line.strip())
                        else:
                            logging.debug(f"Line read but no error: {line.strip()}")
                    else:
                        time.sleep(1)

            else:
                logging.info(f"Already monitoring the log file for {today_date}, waiting for updates.")
                time.sleep(60)

        except Exception as e:
            logging.critical(f"An error occurred: {e}")
            send_error_to_feishu(f"Failed to monitor log file: {e}")
            time.sleep(60)


def start_monitoring():
    """
    启动日志监控
    """
    logging.info("Starting the log file monitoring...")
    monitor_log()


def stop_monitoring():
    """
    停止日志监控，并清理资源
    """
    logging.info("Stopping the log file monitoring...")
    try:
        if remote_file:
            remote_file.close()
            logging.info("Remote log file closed.")
    except Exception as e:
        logging.error(f"Error closing remote file: {e}")

    try:
        if sftp_client:
            sftp_client.close()
            logging.info("SFTP client closed.")
    except Exception as e:
        logging.error(f"Error closing SFTP client: {e}")

    try:
        if client:
            client.close()
            logging.info("SSH client closed.")
    except Exception as e:
        logging.error(f"Error closing SSH client: {e}")

    logging.shutdown()
    logging.info("Logging system shut down.")


# 直接调用启动监控
if __name__ == "__main__":
    # 在启动时检查已有日志文件的错误信息并发送到飞书
    log_file_path = os.path.join(log_dir, f"main_monitor_{datetime.now().strftime('%Y-%m-%d')}.log")
    check_existing_log_for_errors(log_file_path)

    # 启动日志监控
    start_monitoring()
