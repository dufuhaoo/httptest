# -*- coding:utf-8 -*-
from HttpRunnerManager import settings
from ApiManager.utils.faker_data import BaseFaker
from ApiManager.pf_netcar_api.base_api import BaseApi,SheetBaseApi
import random,requests,json,pyDes,base64,re
from ApiManager.utils.mysql_helper import mysql_execute
from ApiManager.utils.base_logger import BaseLogger
from ApiManager.utils.query_base_url import *


logger = BaseLogger(__name__).get_logger()


class TradeLoginApi(BaseApi):
    """s
    trade端用户登录接口
    """
    url = '/netCar/page/customer/login'
    user_mobile = None


    def login_encrypt(self,text):
        """
        DES加密，用与登录
        :param key:
        :param text:
        :return:
        """
        key = 'uatspdbcccgame2014061800'
        k = pyDes.triple_des(key, pyDes.ECB, IV=None, pad=None, padmode=pyDes.PAD_PKCS5)
        d = k.encrypt(json.dumps(text))
        result = base64.standard_b64encode(d)
        res = result.decode(encoding='utf-8')
        res.replace("\n", "")
        res.replace("\r", "")
        return res

    def get_new_mobile(self):
        """
        获取新手机号，确保数据库中该手机号不存在
        :return:
        """
        while True:
            user_mobile = BaseFaker().create_phone_number()
            try:
                user_detail = mysql_execute('select * from tbl_trade_customer where mobile=%s', params=(user_mobile))
            except:
                user_detail = None
            if user_detail:
                continue
            else:
                return user_mobile

    def login(self,user_type=40, mobile=None,open_sign_force=True):
        """
        用户登录
        """
        if mobile:
            self.user_mobile = mobile
        else:
            self.user_mobile = self.get_new_mobile()
        data = {
            'cardNo': '{0}00000'.format(self.user_mobile),
            'cardType': str(user_type),
            'certNo': '{0}9999999'.format(self.user_mobile),
            'certType': '01',
            'channel': '000000000000002',
            'city': 'beijing',
            'memberId': str(self.user_mobile),
            'telephone': str(self.user_mobile),
            'os': '01',
            'userId': str(self.user_mobile),
            'userName': '{0}user{1}'.format(random.randint(100,999),self.user_mobile)
        }
        logger.info('Data:{0}'.format(data))
        request_data = {'data':self.login_encrypt(text=data)}
        response = requests.post(url=self.api_url(), json=request_data, headers=settings.API_HEADERS)
        logger.info('Headers:{0}'.format(response.request.headers))
        logger.info('Response:{0}'.format(response.content))
        token = json.loads(response.content)['data']['token']

        if open_sign_force:

            sign_force_api_url = '/netCar/page/customer/signForcePayProtocol'
            s = requests.session()
            s.headers.setdefault('Authorization', token)
            logger.info('Test Url:{0}'.format(PF_API_BASE_URL + sign_force_api_url))
            sign_force_response = s.post(url=PF_API_BASE_URL + sign_force_api_url)
            logger.info('Response:{0}'.format(sign_force_response.text))
            assert sign_force_response.status_code == 200
            assert json.loads(sign_force_response.content)['code'] == 0

        return {'mobile':self.user_mobile,'token':token}




class SheetLoginApi(SheetBaseApi):
    """
    sheet端用户登录接口
    """
    headers = settings.SHEET_API_HEADERS

    def login(self,user_type='admin',cookie=True):
        """
        用户登录
        :param user_type:
        :param only_token:
        :return:
        """
        end_url = ''
        if user_type == 'admin':
            # 管理员 admin
            end_url = 'username=8lu4XRkZoVfn658E39KtNg%3D%3D&password=QEwd%2FDWmy%2F4yGncCqBofQQ%3D%3D'
        if user_type == 'op':
            # 运营 operation
            end_url = 'username=xuGeFgzo1p0b3QAp3QyVow%3D%3D&password=%2F7EQWL%2BpTZrC8v2JSXU9wA%3D%3D'
        if user_type == 'cu':
            # 客服 customer service
            end_url = 'username=dVLLedoVEF2TTMO4h49PXw%3D%3D&password=%2F7EQWL%2BpTZrC8v2JSXU9wA%3D%3D'

        url = PF_API_BASE_URL + '/netCarAdminAuth/login?' +end_url
        logger.info('Data:{0}'.format(url))
        response = requests.get(url=url,headers=self.headers)
        logger.info('Headers:{0}'.format(response.request.headers))
        logger.info('Response:{0}'.format(response.content))
        if cookie:
            headers = response.headers
            cookie_value = 'shiroCookie=' + str(re.findall(r"shiroCookie=(.+?);", str(headers))[0])
            return  cookie_value
        else:
            return response



class PipeLoginApi(BaseApi):
    """
    pipe端用户登录接口
    """
    url = '/auth/login'
    base_url = PF_API_BASE_URL

    def login(self,user_name='8lu4XRkZoVfn658E39KtNg%3D%3D',password='eNwcIeeCEGJMY32S0pL%2F%2Fg%3D%3D',cookie=True):
        """
        用户登录
        :return:
        """
        request_url = self.base_url + self.url + "?username={0}&password={1}".format(user_name,password)
        response = requests.get(url=request_url)
        logger.info('Headers:{0}'.format(response.request.headers))
        logger.info('Response:{0}'.format(response.content))
        if cookie:
            headers = response.headers
            cookie_value = 'shiroCookie=' + str(re.findall(r"shiroCookie=(.+?);", str(headers))[0])
            return cookie_value
        else:
            return response


if __name__ == '__main__':
    PipeLoginApi().login()