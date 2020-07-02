# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.base_api import BaseApi,SheetBaseApi,PipeBaseApi
from ApiManager.pf_netcar_api.login_api import TradeLoginApi,SheetLoginApi,PipeLoginApi
from ApiManager.utils.base_logger import BaseLogger
from HttpRunnerManager import settings
import requests,time

logger = BaseLogger(__name__).get_logger()



class LoginBaseApi(BaseApi):
    """
    pf接口测试基类-包含登录操作
    """
    user_mobile = None
    time_sleep = 0.3

    def __init__(self,user_type=40,mobile=None,open_sign_force=True,*args, **kwargs):
        super(LoginBaseApi, self).__init__(*args, **kwargs)
        self.token = None
        self.user_type = user_type
        self.mobile = mobile
        self.open_sign_force = open_sign_force


    def get_token_id(self):
        """
        获取token
        :return:
        """
        self.token = TradeLoginApi().login(user_type=self.user_type,mobile=self.mobile,open_sign_force=self.open_sign_force)
        self.mobile = self.token['mobile']
        return self.token['token']

    def get(self, params=None):
        """
        请求方式：GET
        :param params:
        :return:
        """
        token_id = self.get_token_id()
        request_data = self.format_param(params)
        logger.info('Data:{0}'.format(request_data))
        s = requests.session()
        s.headers.setdefault('Authorization', token_id)
        self.response = s.get(url=self.api_url(), params=request_data)
        logger.info('Headers:{0}'.format(self.response.request.headers))
        logger.info('Response:{0}'.format(self.response.content))
        time.sleep(self.time_sleep)
        return self.response

    def post(self, params=None):
        """
        请求方式：POST
        :param params:
        :return:
        """
        token_id = self.get_token_id()
        request_data = self.format_param(params)
        logger.info('Data:{0}'.format(request_data))
        s = requests.session()
        s.headers.setdefault('Authorization', token_id)
        self.response = s.post(url=self.api_url(), json=request_data)
        logger.info('Headers:{0}'.format(self.response.request.headers))
        logger.info('Response:{0}'.format(self.response.content))
        time.sleep(self.time_sleep)
        return self.response



class SheetLoginBaseApi(SheetBaseApi):
    """
    Sheet平台接口测试基类-包含登录操作
    """

    def __init__(self, user_type='admin', *args, **kwargs):
        super(SheetLoginBaseApi, self).__init__(*args, **kwargs)
        self.user_type = user_type

    def get_cookie(self):
        """
        获取cookie
        :return:
        """
        cookie_value = SheetLoginApi().login(user_type=self.user_type)
        return cookie_value

    def get(self, params=None):
        """
        请求方式：GET
        :param params:
        :return:
        """
        cookie_value = self.get_cookie()
        request_data = self.format_param(params)
        logger.info('Data:{0}'.format(request_data))
        s = requests.session()
        s.headers.setdefault('Cookie', cookie_value)
        self.response = s.get(url=self.api_url(), params=request_data)
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
        cookie_value = self.get_cookie()
        request_data = self.format_param(params)
        logger.info('Data:{0}'.format(request_data))
        s = requests.session()
        s.headers.setdefault('Cookie', cookie_value)
        self.response = s.post(url=self.api_url(), json=request_data,headers=settings.SHEET_API_HEADERS)
        logger.info('Headers:{0}'.format(self.response.request.headers))
        logger.info('Response:{0}'.format(self.response.text))
        time.sleep(self.time_sleep)
        return self.response



class PipeLoginBaseApi(PipeBaseApi):
    """
    Pipe平台接口测试基类-包含登录操作
    """

    def __init__(self, user_name='admin',password='123123', *args, **kwargs):
        super(PipeLoginBaseApi, self).__init__(*args, **kwargs)
        self.user_name = user_name
        self.password = password
        self.headers = {'content-type': 'application/json; charset=UTF-8','referer':'http://testzx.ywsk.cn:38000/platformAdminVue/'}

    def get_cookie(self):
        """
        获取cookie
        :return:
        """
        cookie_value = PipeLoginApi().login(user_name=self.user_name,password=self.password)
        return cookie_value

    def get(self, url=None,params=None):
        """
        请求方式：GET
        :param params:
        :return:
        """
        cookie_value = self.get_cookie()
        request_data = self.format_param(params)
        logger.info('Data:{0}'.format(request_data))
        s = requests.session()
        s.headers.setdefault('Cookie', cookie_value)
        # request_url = self.api_url()
        self.response = s.get(url=url, params=request_data,headers=self.headers,verify=False)
        logger.info('Headers:{0}'.format(self.response.request.headers))
        logger.info('Response:{0}'.format(self.response.content))
        return self.response

    def post(self, params=None):
        """
        请求方式：POST
        :param params:
        :return:
        """
        cookie_value = self.get_cookie()
        request_data = self.format_param(params)
        logger.info('Data:{0}'.format(request_data))
        s = requests.session()
        s.headers.setdefault('Cookie', cookie_value)
        self.response = s.post(url=self.api_url(), json=request_data)
        logger.info('Headers:{0}'.format(self.response.request.headers))
        logger.info('Response:{0}'.format(self.response.content))
        return self.response