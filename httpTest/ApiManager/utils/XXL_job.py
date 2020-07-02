# -*- coding:utf-8 -*-
import requests, json, re,time


class XXLJob(object):
    """
    sheet
    19  批量定时监控
    18  每日红包平台充值优惠券差错对账
    17  用户登录统计
    12	随机立减数据统计
    11	线下清算扣款费用通知回调trade
    9	每日订单对账执行器
    8	线下扣款清算文件生成
    7	联机扣款数据统计
    6	线下扣款清算结果文件读取
    5	黑名单推送trade
    4	未支付订单统计
    3	优惠券活动数据统计
    2   支付及退款数据统计
    1   运营数据统计`

    trade
    20  应用监控数据更新
    15  重试清除超时未取消接送机订单
    14  退款定时任务
    13  查询订单支付状态
    12  交易端-强制扣款
    11	删除失败及执行成功的任务
    10  红包平台优惠券下发
    9	下发优惠券
    8   查询进行中的活动
    6	接送机超时取消
    3	网约车-推送费用确认通知
    2	接送机下单任务
    """

    trade_url = 'http://testzx.ywsk.cn:38000/netcar-job-admin'
    sheet_url = 'http://testzx.ywsk.cn:38000/netCarAdminJob'
    headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}

    def login(self,job):
        """
        调度平台登录
        :param job:
        :return:
        """
        if job == 'sheet':
            login_url = self.sheet_url + '/login'
        else:
            login_url = self.trade_url + '/login'

        login_data = {'userName': 'admin', 'password': '123456'}
        login_response = requests.post(url=login_url, data=login_data, headers=self.headers)
        resp_code = json.loads(login_response.content)['code']
        if resp_code == 200:
            identity = re.findall(r"XXL_JOB_LOGIN_IDENTITY=(.+?);", str(login_response.headers))
            return identity[0]

    def edit_config(self, sheet_ip='192.168.0.48:9003',trade_ip='192.168.0.18:9005',sheet_job=True):
        """
        修改执行器
        :param sheet_ip:
        :param trade_ip:
        :param sheet_job:
        :return:
        """
        if sheet_job == True:
            identity = self.login('sheet')
            job_url = self.sheet_url + '/jobgroup/update'
            job_data = {'appName': 'netcar-admin', 'title': '网约车内管端', 'order': '1', 'addressType': '1', 'addressList': sheet_ip,'id': '2'}
        else:
            identity = self.login('trade')
            job_url = self.sheet_url + '/jobgroup/update'
            job_data = {'appName': 'netcar-trade', 'title': '网约车内管端', 'order': '1', 'addressType': '0','addressList': trade_ip,'id': '2'}
        s = requests.session()
        s.cookies.set('XXL_JOB_LOGIN_IDENTITY', identity)
        response = s.post(url=job_url, data=job_data, headers=self.headers)
        resp_code = json.loads(response.content)['code']
        if resp_code == 200:
            print('Edit success!')
            return True
        else:
            print('failed!!!!')
            return False

    def run_job(self, job_id, executor_param=None,sheet_job=True):
        """
        执行job
        :param job_id:
        :return:
        """

        self.edit_config()
        if sheet_job == True:
            identity = self.login('sheet')
            job_url = self.sheet_url + '/jobinfo/trigger'
        else:
            identity = self.login('trade')
            job_url = self.trade_url + '/jobinfo/trigger'

        job_data = {'id': job_id, 'executorParam': executor_param}
        s = requests.session()
        s.cookies.set('XXL_JOB_LOGIN_IDENTITY', identity)
        response = s.post(url=job_url, data=job_data, headers=self.headers)
        resp_code = json.loads(response.content)['code']
        time.sleep(2)
        if resp_code == 200:
            print('Request success!')
            return True
        else:
            print('failed!!!!')
            return False

if __name__ == '__main__':
    XXLJob().run_job(job_id='9',sheet_job=False)
    # Job().run_job(job_id='6',sheet_job=False)
