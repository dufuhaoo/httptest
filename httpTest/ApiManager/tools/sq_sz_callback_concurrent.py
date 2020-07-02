# -*- coding:utf-8 -*-
"""
首汽、神州渠道并发回调接单脚本
"""
from selenium import webdriver
from ApiManager.utils.mysql_helper import mysql_execute
from ApiManager.utils.redis_helper import redis_execute
import logging,grequests,hashlib
import json,redis
import requests
import time

logger = logging.getLogger(__name__)


r = redis.Redis(host='111.202.106.110', port='18011', db=1,password='5W4Jl6MN')

def string_to_md5(string):
    """
    创建md5加密字符串
    :param string:
    :return:
    """
    m = hashlib.md5()
    m.update(string.encode(encoding='UTF-8'))
    return m.hexdigest()


class CallBack(object):

    def __init__(self,trade_order_id):
        self.sq_call_back_url = 'http://tcnl.ywsk.cn:37000/pfCallbackGateway/callback/sqCallbackOrderStatusNotify'
        self.sz_call_back_url = 'http://tcnl.ywsk.cn:37000/pfCallbackGateway/callback/szCallbackOrderStatusNotify'
        self.sz_get_access_token_url = 'https://sandboxoauth.10101111.com/oauth/token'
        self.sz_encrypt_url = 'http://192.168.0.46:7003/szNetCarCallback/callback/getEncrypt'
        self.headers = {'content-type': 'application/json; charset=UTF-8'}
        self.trade_order_id = trade_order_id


    def sq_callback_accepted(self):
        """
        首汽订单回调接单
        :param request:
        :return:
        """
        sign_key = 'Py4CLvQZB5$A9hN3U'
        car_info_detail = mysql_execute('select * from netCarPlatform.tbl_platform_car_info where trade_order_id=%s and channel_type=2 limit 1',params=(self.trade_order_id))
        channel_order_id = car_info_detail['channel_order_id']  # 渠道ID
        partner_order_id = car_info_detail['id']
        car_type = int(car_info_detail['car_type'])  # 车型组代码

        car_type_name = ''  # 车型组名称
        if car_type == 34:
            car_type_name = '舒适型'
        elif car_type == 35:
            car_type_name = '商务6座'
        elif car_type == 40:
            car_type_name = '商务福祉车'
        elif car_type == 43:
            car_type_name = '畅享型'
        elif car_type == 61:
            car_type_name = '豪华型'

        event_time = int(time.time())
        expired_time = event_time + 300

        event_id = 'a6fb2b1034b54ca1a49c1239c6eb73af'
        driver_info = {"vehicleColor": '红色', "modelName": '奥迪A7', "groupName": car_type_name,"driverRate": '5.0', "driverId": "100026076",
                       "phone": "13501077762", "groupId": car_type,"driverTrumpetPhone": '15566662111',
                       "licensePlates": '京A77777', "name": '王永生', "vehiclePic": "",
                       "photoSrc": "http://m.360buyimg.com/pop/jfs/t23434/230/1763906670/10667/55866a07/5b697898N78cd1466.jpg"}

        json_meta = json.dumps({"driverInfo": driver_info, "orderNo": channel_order_id, "partnerOrderNo": partner_order_id,"status": "accepted"})
        sign_id_str = 'channel=shouqi&eventId={0}&eventTime={1}&expiredTime={2}&meta={3}&sqycKey={4}'.format(event_id,event_time,expired_time,json_meta,sign_key)
        sign_id = string_to_md5(sign_id_str)
        request_data = {"channel": "shouqi", "eventId": event_id, "eventTime": event_time, "expiredTime": expired_time,"meta": json_meta, "sign": sign_id}
        logger.info('sq request url: {0}'.format(self.sq_call_back_url))
        logger.info('sq request data: {0}'.format(request_data))
        return {'request_data':request_data}

    def sq_run(self,request_data):
        """
        首汽触发回调
        :param request_data:
        :return:
        """
        resp = requests.post(url=self.sq_call_back_url, params=request_data, headers=self.headers)
        if resp.status_code != 200:
            return '回调失败！状态码:{0}'.format(resp.status_code)
        logger.info(resp.content)
        resp_content = json.loads(resp.content)
        if resp_content['result'] == 0:
            return '回调成功！'
        else:
            return '回调失败！原因: {0}'.format(resp_content)

    def sz_callback_accepted(self):
        """
        神州订单回调接单
        :param request:
        :return:
        """
        # 查询渠道ID与pipe_id
        car_info_detail = mysql_execute('select * from netCarPlatform.tbl_platform_car_info where trade_order_id=%s and channel_type=4 limit 1',params=(self.trade_order_id))
        if not car_info_detail:
            return '未查询到该订单！'
        channel_order_id = car_info_detail['channel_order_id']  # 渠道ID
        partner_order_id = car_info_detail['id']

        # 定义请求参数
        change_status_request_data = {"bankFlag": 1, "content": {"dOrderId": partner_order_id, "eventExplanation": "","orderId": channel_order_id,"status": 'dispatched'},"operation": "statusChanged"}

        # 更新订单详情接口返回数据
        default_data = json.loads(mysql_execute('select api_response from mock_response where api_url="/v1/resource/order/getOrderDetail" and channel="sz"',platform=True)['api_response'])
        default_data['content']['order']['id'] = channel_order_id
        default_data['content']['order']['customData'] = json.dumps({"dOrderId": partner_order_id})
        default_data['content']['order']['status'] = 'dispatched'
        redis_execute().set(name=str(channel_order_id) + '_sz_order_detail_response',value=json.dumps(default_data))
        logger.info('redis key: {0}'.format(str(channel_order_id) + '_sz_order_detail_response'))
        logger.info('redis value: {0}'.format(json.dumps(default_data)))
        logger.info('update redis success!')

        # 请求参数加密
        request_encrypt = requests.get(url=self.sz_encrypt_url, params={'q': str(change_status_request_data)},headers=self.headers)
        logger.info('sz request encrypt url: {0}'.format(self.sz_encrypt_url))
        logger.info('sz request encrypt data: {0}'.format(change_status_request_data))
        logger.info(request_encrypt.text)
        return {'request_data':{'q': request_encrypt.text}}

    def sz_run(self,request_data):
        """
        神州触发回调
        :return:
        """
        resp = requests.get(url=self.sz_call_back_url, params=request_data, headers=self.headers)
        logger.info('sz request url: {0}'.format(self.sz_call_back_url))
        logger.info('sz request data: {0}'.format(request_data))
        if resp.status_code != 200:
            return '回调失败！状态码:{0}'.format(resp.status_code)
        logger.info(resp.content)
        resp_content = json.loads(resp.content)
        if resp_content['status'] == 200:
            return '回调成功！'
        else:
            return '回调失败！原因: {0}'.format(resp_content)



if __name__ == '__main__':
    # 13544442222
    count = 1
    max_count = 100
    driver  = webdriver.Firefox()
    driver.maximize_window()
    driver.get(url='http://testzx.ywsk.cn:38000/netcar/')
    time.sleep(20)
    # 点击定位按钮
    driver.find_element_by_xpath('//*[@id="map-box"]/div[3]/div[2]/div[1]/div/div[1]/i').click()
    time.sleep(1)
    # 点击回家按钮
    driver.find_element_by_xpath('//*[@id="app"]/div/div[3]/div[2]/div/div[1]/div/div').click()
    time.sleep(10)

    while count < max_count:
        # 点击展开按钮
        driver.find_element_by_xpath('//*[@id="app"]/div/div[4]/div[3]/span/i').click()
        time.sleep(1)
        # 取消曹操车型选中状态
        driver.find_element_by_xpath('//*[@id="app"]/div/div[4]/div[2]/div[2]/div[2]/div/div/div[2]').click()
        time.sleep(0.3)
        # 勾选神州与首汽车型
        driver.find_element_by_xpath('//*[@id="app"]/div/div[4]/div[2]/div[3]/div[2]/div[1]/div/div[2]').click()
        time.sleep(0.3)
        driver.find_element_by_xpath('//*[@id="app"]/div/div[4]/div[2]/div[3]/div[2]/div[2]/div/div[2]').click()
        time.sleep(0.3)
        # 点击立即打车按钮
        driver.find_element_by_xpath('/html/body/div[1]/div/div[4]/div[3]/div/button').click()
        time.sleep(10)
        curr_url = driver.current_url
        print(curr_url)

        trade_order_id = curr_url[-19:]
        # trade_order_id = 1142643544858984448
        callback_class = CallBack(trade_order_id)
        sq_request_data = callback_class.sq_callback_accepted()['request_data']
        print('首汽请求参数:',sq_request_data)
        sz_request_data = callback_class.sz_callback_accepted()['request_data']
        print('神州请求参数',sz_request_data)

        # 定义并发请求列表
        req_list = [grequests.get(callback_class.sz_call_back_url,params=sz_request_data,headers=callback_class.headers),
                    grequests.post(callback_class.sq_call_back_url, params=sq_request_data,headers=callback_class.headers),]
        # 并行发送，等最后一个运行完后返回
        res_list = grequests.map(req_list)
        print('首汽响应:',res_list[0].text)  # 打印第一个请求的响应文本
        print('神州响应:',res_list[1].text)  # 打印第二个请求的响应文本
        #
        # 验证redis值
        redis_resp_value = json.loads(r.get(name='platform_actual:orderInfoRsp_{0}'.format(trade_order_id)))
        # if redis_resp_value['actualRespCount'] == 1:
        #     print('actualRespCount值正常')
        print(redis_resp_value)
        # if len(redis_resp_value['notifyResult']) != 2:
        #     print('出现异常数据，订单号为：{0}'.format(trade_order_id))
        #     break
        # else:
        #     print('数据正常!')

        f = open('./create_order_redis.txt','a')
        f.write(redis_resp_value + '\n')
        f.close()
        time.sleep(5)
        # 点击取消订单按钮
        driver.find_element_by_xpath('//*[@id="app"]/div/div[4]/button').click()
        time.sleep(0.5)
        # 点击二次确认框确定按钮
        driver.find_element_by_xpath('//*[@id="app"]/div/div[7]/div[3]/button[2]').click()
        time.sleep(5)
        # 点击重新打车按钮
        driver.find_element_by_xpath('//*[@id="app"]/div/div[3]/button').click()
        time.sleep(10)



