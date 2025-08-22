import paramiko
from core.logger import logger

class SSHManager:
    """用于管理SSH连接和命令执行的上下文管理器"""

    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = None

    def connect(self):
        """建立SSH连接"""
        if self.client is not None and self.client.get_transport() and self.client.get_transport().is_active():
            logger.info("SSH客户端已连接")
            return

        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.hostname, self.port, self.username, self.password, timeout=10)
            logger.info(f"已建立到 {self.hostname} 的SSH连接")
        except Exception as e:
            logger.error(f"建立到 {self.hostname} 的SSH连接失败: {e}")
            self.client = None
            raise

    def disconnect(self):
        """关闭SSH连接"""
        if self.client:
            self.client.close()
            self.client = None
            logger.info(f"已关闭到 {self.hostname} 的SSH连接")

    def execute_command(self, command):
        """执行一个命令并返回其输出、错误和状态码"""
        if not self.client:
            raise ConnectionError("SSH客户端未连接")
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            return output, error, exit_status
        except Exception as e:
            logger.error(f"在 {self.hostname} 上执行命令 '{command}' 失败: {e}")
            raise

    def get_streaming_channel(self, command):
        """执行一个命令并返回一个可用于流式读取的通道"""
        if not self.client:
            raise ConnectionError("SSH客户端未连接")
        
        try:
            transport = self.client.get_transport()
            channel = transport.open_session()
            channel.exec_command(command)
            return channel
        except Exception as e:
            logger.error(f"在 {self.hostname} 上为命令 '{command}' 获取流式传输通道失败: {e}")
            raise

