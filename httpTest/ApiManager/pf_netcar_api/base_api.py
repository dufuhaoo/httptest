# -*- coding:utf-8 -*-
from ApiManager.utils.query_base_url import PF_API_BASE_URL
from HttpRunnerManager import settings
from ApiManager.utils.base_logger import BaseLogger
import json
import requests
import time


logger = BaseLogger(__name__).get_logger()

class BaseApi(object):
    """
    pf接口测试基类-无登录操作
    """
    url = ''
    base_url = PF_API_BASE_URL
    headers = settings.API_HEADERS
    time_sleep = 0.3

    def __init__(self):
        self.response = None

    def api_url(self):
        """
        拼接url
        :return:
        """
        url = "{0}{1}".format(self.base_url,self.url)
        logger.info('Test Url:{0}'.format(url))
        return url

    def build_base_param(self):
        """
        构建共有入参
        :return:
        """
        return {}

    def build_custom_param(self, params):
        """
        构建除共有参数外其余参数，接口封装时将该方法重写
        :param data:
        :return:
        """
        return {}

    def format_param(self,params):
        """
        合并共有参数和其他所需参数
        :param data:
        :return:
        """
        if not params:
            params = {}
        base_param = self.build_base_param()
        custom_param = self.build_custom_param(params)
        params.update(base_param)
        params.update(custom_param)
        return custom_param

    def get(self, params=None):
        """
        请求方式：GET
        :param params:
        :return:
        """
        request_data = self.format_param(params)
        logger.info('Data:{0}'.format(request_data))
        s = requests.session()
        self.response = s.get(url=self.api_url(), params=request_data, headers=self.headers)
        logger.info('Headers:{0}'.format(self.response.request.headers))
        logger.info('Response:{0}'.format(self.response.text))
        time.sleep(self.time_sleep)
        return self.response

    def post(self, params=None):
        """
        请求方式：POST
        :param params:
        :return:
        """
        request_data = self.format_param(params)
        logger.info('Data:{0}'.format(request_data))
        s = requests.session()
        self.response = s.post(url=self.api_url(), json=request_data, headers=self.headers)
        logger.info('Headers:{0}'.format(self.response.request.headers))
        logger.info('Response:{0}'.format(self.response.text))
        time.sleep(self.time_sleep)
        return self.response

    def get_status_code(self):
        """
        返回请求网络状态码
        :return:
        """
        if self.response:
            return self.response.status_code

    def get_resp_content(self):
        """
        获取完整出参
        :return:
        """
        return json.loads(self.response.content)

    def get_resp_content_not_json(self):
        """
        获取完整出参不进行json转换
        :return:
        """
        return self.response.content

    def get_resp_code(self):
        """
        获取回参中code状态码
        :return:
        """
        if self.response:
            return int(json.loads(self.response.content)['code'])

    def get_resp_message(self):
        """
        获取回参中msg
        :return:
        """
        if self.response:
            return json.loads(self.response.content)['msg']

    def get_resp_data(self):
        """
        获取回参中data
        :return:
        """
        if self.response:
            return json.loads(self.response.content)['data']

    def get_resp_success(self):
        """
        获取回参中success值
        :return:
        """
        if self.response:
            return json.loads(self.response.content)['success']

    def get_resp_elapsed(self):
        """
        获取接口相应时间，单位：秒
        :return:
        """
        if self.response:
            return self.response.elapsed.total_seconds()



class SheetBaseApi(BaseApi):
    """
    接口测试基类(Sheet)
    """
    url = ''
    base_url = PF_API_BASE_URL
    headers = settings.API_HEADERS

    def get_resp_code(self):
        """
        获取回参中code状态码
        :return:
        """
        if self.response:
            return int(json.loads(self.response.content)['code'])


class PipeBaseApi(BaseApi):
    """
    接口测试基类(pipe)
    """
    url = ''
    base_url = PF_API_BASE_URL
    headers = settings.API_HEADERS

    def get_resp_code(self):
        """
        获取回参中code状态码
        :return:
        """
        if self.response:
            return int(json.loads(self.response.content)['errCode'])