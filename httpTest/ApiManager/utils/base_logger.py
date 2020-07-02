# coding=utf-8
import logging

class BaseLogger(object):

    def __init__(self,name):
        """
        初始化logger
        :param name:
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)  # Log等级总开关

    def get_logger(self):
        """
        自定义logger
        :return:
        """
        # 定义handler的输出格式
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        # 创建一个handler，用于输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # 输出到console的log等级的开关
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        return self.logger