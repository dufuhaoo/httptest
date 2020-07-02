# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_monitoring.base_monitoring import BaseMonitoring
from ApiManager.pf_netcar_api.sheet.activity_manager_api import AddActivityApi,CloseActivityApi,GetActivityListApi
from ApiManager.utils import hooks
from ApiManager.pf_netcar_api.login_api import TradeLoginApi
from ApiManager.utils.query_base_url import *
from ApiManager.utils.mysql_helper import mysql_execute
from ApiManager.utils.faker_data import BaseFaker
from ApiManager.utils.redis_helper import COUPON_RECHARGE_MONITORING_KEY
from ApiManager.pf_netcar_api.trade.get_coupon_list_api import GetCouponListApi
import datetime, time,random,hashlib,json,requests
from HttpRunnerManager import settings
from ApiManager.utils.XXL_job import XXLJob




class CouponRechargeMonitoring(BaseMonitoring):
    """
    红包充值监控
    """
    activity_list = []
    activity_id = None
    sign_id = '签报号-测试满减券红包充值1'
    activity_name = '测试红包充值满减券'
    description = BaseFaker().create_sentence()  # 随机生成一段文字
    pay_amount = 10000
    coupon_amount = 5000
    expire_time = 10

    def setUp(self):
        super(CouponRechargeMonitoring,self).setUp()
        # 查询活动状态查询当前生效的活动
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 1,'activityId':None, 'activityType': None, 'signId': None, 'pageSize': 100,'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        if activity_list:
            for x in activity_list:
                # 调用终止活动接口
                close_activity_api = CloseActivityApi()
                close_activity_api.post({'activityStatus': 2, 'id': x['id']})
                assert close_activity_api.get_status_code() == 200
                assert close_activity_api.get_resp_code() == 0
                assert close_activity_api.get_resp_message() == 'OK'
            time.sleep(2)


    def coupon_recharge(self):
        """
        测试红包充值
        :return:
        """
        now_time = datetime.datetime.now()
        start_time = (now_time + datetime.timedelta(hours=-5)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S")
        # 创建红包充值满减券
        create_activity_api = AddActivityApi()
        self.activity_id = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
        create_activity_api.post({"activityObject": 5, "activityStartTime": start_time,
                                  "activityEndTime": end_time, "activityName": self.activity_name,
                                  "signId": self.sign_id,
                                  "activityId": self.activity_id, "couponExpireTime": self.expire_time, "grantTotal": 100,
                                  "activityFrom": 5, "activityUseType": 1, "activityType": 1,
                                  "couponDiscount": "",
                                  "payAmount": self.pay_amount, "couponAmount": self.coupon_amount, "payAmountMin": "", "payAmountMax": "",
                                  "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
                                  "activityCycleType": "", "activityCycleTotalTime": "",
                                  "description": self.description})
        assert create_activity_api.get_status_code() == 200
        assert create_activity_api.get_resp_code() == 0
        assert create_activity_api.get_resp_message() == 'OK'
        self.activity_list.append({'activity_id': self.activity_id, 'sign_id': self.sign_id})  # 将该活动信息加入全局变量列表中
        time.sleep(10)
        # 查询活动id查询
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 0,'activityId': self.activity_id, 'activityType': None, 'signId': None, 'pageSize': 100,'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        assert activity_list[0]['activityId'] == self.activity_id
        assert activity_list[0]['activityStatusDesc'] == '生效'

        def recharge_logic(user_id,event_id,coupon_amount,expire_time,is_user_id):
            event_id = event_id
            coupon_amount = coupon_amount
            expire_time = expire_time
            sign_key = 'bksk123kvzcnAadDnmas1;fnopij'

            def get_random_trade_no():
                """
                随机生成订单号并且数据库中不存在
                :return:
                """
                while True:
                    num = str(int(time.time())) + str(random.randint(1000, 9999))
                    result = mysql_execute('select * from tbl_trade_order where id=%s', params=(num), trade=True)
                    if not result:
                        return num

            recharge_from = '1'  # 充值来源 1=红包平台充值
            trade_no = get_random_trade_no()  # 订单号
            customer_detail = mysql_execute('select * from tbl_trade_customer where user_id=%s', params=(user_id),
                                            trade=True)
            if customer_detail:
                logger.info('user is active!')
                id_num = customer_detail['id_num']
                logger.info(id_num)
            else:
                id_num = user_id + '9999999'
                logger.info(id_num)

            time_stamp = str(int(time.time()) * 1000)  # 时间戳（当前毫秒时间戳）
            sign_list = []
            if is_user_id:
                sign_list.append(user_id)
            if coupon_amount:
                sign_list.append(str(coupon_amount))
            if expire_time:
                sign_list.append(str(expire_time))
            sign_list.append(id_num)
            sign_list.append(trade_no)
            sign_list.append(event_id)
            sign_list.append(recharge_from)
            sign_list.append(time_stamp)
            sign_list.append(sign_key)
            sign_list.sort()
            sign_str = ''
            for x in sign_list:
                sign_str += x
            sign = hashlib.sha1(sign_str.encode()).hexdigest()
            logger.info('Sign is:{0}'.format(sign))

            if not coupon_amount:
                coupon_amount = None
            if not expire_time:
                expire_time = None

            data = {"eventId": event_id, "idNum": id_num, "rechargeFrom": recharge_from, "sign": sign,
                    "timestamp": time_stamp, "tradeNo": trade_no}
            if int(is_user_id) == 1:
                data.update({"userId": user_id})
            if coupon_amount:
                data.update({"couponAmount": coupon_amount})
            if expire_time:
                data.update({"expireTime": expire_time})

            logger.info('request url:{0}'.format(SPDB_COUPON_RECHARGE_API_URL))
            logger.info('request data:{0}'.format(data))

            response = requests.post(url=SPDB_COUPON_RECHARGE_API_URL, json=data, headers=settings.API_HEADERS)
            logger.info('response:{0}'.format(response.text))
            return json.loads(response.content)

        # 针对已存在用户发发放，不指定金额与有效期,传userId
        login_result = TradeLoginApi().login()
        user_id = login_result['mobile']
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=True)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        count = 1
        max_count = 30
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['couponDiscount'] == 0.0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+self.expire_time)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 针对已存在用户发发放，指定金额,传userId
        login_result = TradeLoginApi().login()
        user_id = login_result['mobile']
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=2000,expire_time=None,is_user_id=True)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['couponDiscount'] == 0.0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == 2000
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+self.expire_time)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 针对已存在用户发发放，指定有效期,传userId
        login_result = TradeLoginApi().login()
        user_id = login_result['mobile']
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=5,is_user_id=True)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['couponDiscount'] == 0.0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+5)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 针对已存在用户发发放，指定金额和过期时间,传userId
        login_result = TradeLoginApi().login()
        user_id = login_result['mobile']
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=2000,expire_time=5,is_user_id=True)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['couponDiscount'] == 0.0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == 2000
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+5)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 针对不存在用户发发放，不指定金额与有效期,传userId
        user_id = TradeLoginApi().get_new_mobile()
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=True)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['couponDiscount'] == 0.0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+self.expire_time)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 针对不存在用户发发放，指定金额,传userId
        user_id = TradeLoginApi().get_new_mobile()
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=2000,expire_time=None,is_user_id=True)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['couponDiscount'] == 0.0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == 2000
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+self.expire_time)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 针对不存在用户发发放，指定有效期,传userId
        user_id = TradeLoginApi().get_new_mobile()
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=5,is_user_id=True)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['couponDiscount'] == 0.0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+5)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 针对不存在用户发发放，指定金额和过期时间,传userId
        user_id = TradeLoginApi().get_new_mobile()
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=2000,expire_time=5,is_user_id=True)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['couponDiscount'] == 0.0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == 2000
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+5)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 先针对不存在用户发放，再针对已存在用户发放,传userId
        new_mobile = TradeLoginApi().get_new_mobile()
        login_result = TradeLoginApi().login()
        user_id = login_result['mobile']
        # 调用红包充值接口
        for x in [new_mobile,user_id]:
            recharge_resp = recharge_logic(user_id=x,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=True)
            assert recharge_resp['errCode'] == '000000'
            assert recharge_resp['success'] == True
            assert recharge_resp['msg'] == '成功'
            assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        for x in [new_mobile,user_id]:
            while count < max_count:
                get_coupon_list_api = GetCouponListApi(mobile=x)
                get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
                assert get_coupon_list_api.get_status_code() == 200
                assert get_coupon_list_api.get_resp_code() == 0
                assert get_coupon_list_api.get_resp_message() == 'OK'
                coupon_list_data = get_coupon_list_api.get_resp_data()
                if len(coupon_list_data['list']) == 0:
                    count += 1
                    time.sleep(1)
                    continue
                else:
                    assert len(coupon_list_data['list']) == 1
                    assert coupon_list_data['total'] == 1
                    assert coupon_list_data['list'][0]['activityUseType'] == 1
                    assert coupon_list_data['list'][0]['couponType'] == 1
                    assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                    assert coupon_list_data['list'][0]['couponDiscount'] == 0.0
                    assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                    assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                    assert coupon_list_data['list'][0]['couponState'] == '1'
                    assert coupon_list_data['list'][0]['couponAmount'] == self.coupon_amount
                    assert coupon_list_data['list'][0]['description'] == self.description
                    coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                    timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                    coupon_start_time_timeStamp = int(time.mktime(timeArray))
                    assert int(time.time()) - coupon_start_time_timeStamp < 180
                    assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+self.expire_time)).strftime("%Y-%m-%d 23:59")
                    break
            assert count < max_count

        # 先针对已存在用户发放，再针对已存在用户发放,传userId
        login_result_one = TradeLoginApi().login()
        user_id_one = login_result_one['mobile']
        login_result_two = TradeLoginApi().login()
        user_id_two = login_result_two['mobile']
        # 调用红包充值接口
        for x in [user_id_one,user_id_two]:
            recharge_resp = recharge_logic(user_id=x,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=True)
            assert recharge_resp['errCode'] == '000000'
            assert recharge_resp['success'] == True
            assert recharge_resp['msg'] == '成功'
            assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        for x in [user_id_one,user_id_two]:
            while count < max_count:
                get_coupon_list_api = GetCouponListApi(mobile=x)
                get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
                assert get_coupon_list_api.get_status_code() == 200
                assert get_coupon_list_api.get_resp_code() == 0
                assert get_coupon_list_api.get_resp_message() == 'OK'
                coupon_list_data = get_coupon_list_api.get_resp_data()
                if len(coupon_list_data['list']) == 0:
                    count += 1
                    time.sleep(1)
                    continue
                else:
                    assert len(coupon_list_data['list']) == 1
                    assert coupon_list_data['total'] == 1
                    assert coupon_list_data['list'][0]['activityUseType'] == 1
                    assert coupon_list_data['list'][0]['couponType'] == 1
                    assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                    assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                    assert coupon_list_data['list'][0]['couponState'] == '1'
                    assert coupon_list_data['list'][0]['couponAmount'] == self.coupon_amount
                    assert coupon_list_data['list'][0]['couponDiscount'] == 0
                    assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                    assert coupon_list_data['list'][0]['description'] == self.description
                    coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                    timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                    coupon_start_time_timeStamp = int(time.mktime(timeArray))
                    assert int(time.time()) - coupon_start_time_timeStamp < 180
                    assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+self.expire_time)).strftime("%Y-%m-%d 23:59")
                    break
            assert count < max_count

        # 先针对不存在用户发放，再针对不存在用户发放,传userId
        new_mobile_one = TradeLoginApi().get_new_mobile()
        new_mobile_two = TradeLoginApi().get_new_mobile()
        # 调用红包充值接口
        for x in [new_mobile_one, new_mobile_two]:
            recharge_resp = recharge_logic(user_id=x, event_id=self.activity_id, coupon_amount=None, expire_time=None,is_user_id=True)
            assert recharge_resp['errCode'] == '000000'
            assert recharge_resp['success'] == True
            assert recharge_resp['msg'] == '成功'
            assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10, sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        for x in [new_mobile_one, new_mobile_two]:
            while count < max_count:
                get_coupon_list_api = GetCouponListApi(mobile=x)
                get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
                assert get_coupon_list_api.get_status_code() == 200
                assert get_coupon_list_api.get_resp_code() == 0
                assert get_coupon_list_api.get_resp_message() == 'OK'
                coupon_list_data = get_coupon_list_api.get_resp_data()
                if len(coupon_list_data['list']) == 0:
                    count += 1
                    time.sleep(1)
                    continue
                else:
                    assert len(coupon_list_data['list']) == 1
                    assert coupon_list_data['total'] == 1
                    assert coupon_list_data['list'][0]['activityUseType'] == 1
                    assert coupon_list_data['list'][0]['couponType'] == 1
                    assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                    assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                    assert coupon_list_data['list'][0]['couponState'] == '1'
                    assert coupon_list_data['list'][0]['couponAmount'] == self.coupon_amount
                    assert coupon_list_data['list'][0]['couponDiscount'] == 0
                    assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                    assert coupon_list_data['list'][0]['description'] == self.description
                    coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                    timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                    coupon_start_time_timeStamp = int(time.mktime(timeArray))
                    assert int(time.time()) - coupon_start_time_timeStamp < 180
                    assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+self.expire_time)).strftime("%Y-%m-%d 23:59")
                    break
            assert count < max_count

        # 针对已存在用户发发放，不指定金额与有效期,不传userId
        login_result = TradeLoginApi().login()
        user_id = login_result['mobile']
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=False)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['couponDiscount'] == 0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+self.expire_time)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 针对已存在用户发发放，指定金额,不传userId
        login_result = TradeLoginApi().login()
        user_id = login_result['mobile']
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=2000,expire_time=None,is_user_id=False)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == 2000
                assert coupon_list_data['list'][0]['couponDiscount'] == 0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == 5000
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+self.expire_time)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 针对已存在用户发发放，指定有效期,不传userId
        login_result = TradeLoginApi().login()
        user_id = login_result['mobile']
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=5,is_user_id=False)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['couponDiscount'] == 0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+5)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 针对已存在用户发发放，指定金额和过期时间,不传userId
        login_result = TradeLoginApi().login()
        user_id = login_result['mobile']
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=2000,expire_time=5,is_user_id=False)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == 2000
                assert coupon_list_data['list'][0]['couponDiscount'] == 0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == 5000
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+5)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 针对不存在用户发发放，不指定金额与有效期,不传userId
        user_id = TradeLoginApi().get_new_mobile()
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=False)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['couponDiscount'] == 0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+self.expire_time)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 针对不存在用户发发放，指定金额,不传userId
        user_id = TradeLoginApi().get_new_mobile()
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=2000,expire_time=None,is_user_id=False)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == 2000
                assert coupon_list_data['list'][0]['couponDiscount'] == 0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == 5000
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+self.expire_time)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 针对不存在用户发发放，指定有效期,不传userId
        user_id = TradeLoginApi().get_new_mobile()
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=5,is_user_id=False)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['couponDiscount'] == 0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+5)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 针对不存在用户发发放，指定金额和过期时间,不传userId
        user_id = TradeLoginApi().get_new_mobile()
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=2000,expire_time=5,is_user_id=False)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        while count < max_count:
            get_coupon_list_api = GetCouponListApi(mobile=user_id)
            get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
            assert get_coupon_list_api.get_status_code() == 200
            assert get_coupon_list_api.get_resp_code() == 0
            assert get_coupon_list_api.get_resp_message() == 'OK'
            coupon_list_data = get_coupon_list_api.get_resp_data()
            if len(coupon_list_data['list']) == 0:
                count += 1
                time.sleep(1)
                continue
            else:
                assert len(coupon_list_data['list']) == 1
                assert coupon_list_data['total'] == 1
                assert coupon_list_data['list'][0]['activityUseType'] == 1
                assert coupon_list_data['list'][0]['couponType'] == 1
                assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                assert coupon_list_data['list'][0]['couponState'] == '1'
                assert coupon_list_data['list'][0]['couponAmount'] == 2000
                assert coupon_list_data['list'][0]['couponDiscount'] == 0
                assert coupon_list_data['list'][0]['maxCouponAmount'] == 5000
                assert coupon_list_data['list'][0]['description'] == self.description
                coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                coupon_start_time_timeStamp = int(time.mktime(timeArray))
                assert int(time.time()) - coupon_start_time_timeStamp < 180
                assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+5)).strftime("%Y-%m-%d 23:59")
                break
        assert count < max_count

        # 先针对不存在用户发放，在针对已存在用户发放,不传userId
        new_mobile = TradeLoginApi().get_new_mobile()
        login_result = TradeLoginApi().login()
        user_id = login_result['mobile']
        # 调用红包充值接口
        for x in [new_mobile,user_id]:
            recharge_resp = recharge_logic(user_id=x,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=False)
            assert recharge_resp['errCode'] == '000000'
            assert recharge_resp['success'] == True
            assert recharge_resp['msg'] == '成功'
            assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        for x in [new_mobile,user_id]:
            while count < max_count:
                get_coupon_list_api = GetCouponListApi(mobile=x)
                get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
                assert get_coupon_list_api.get_status_code() == 200
                assert get_coupon_list_api.get_resp_code() == 0
                assert get_coupon_list_api.get_resp_message() == 'OK'
                coupon_list_data = get_coupon_list_api.get_resp_data()
                if len(coupon_list_data['list']) == 0:
                    count += 1
                    time.sleep(1)
                    continue
                else:
                    assert len(coupon_list_data['list']) == 1
                    assert coupon_list_data['total'] == 1
                    assert coupon_list_data['list'][0]['activityUseType'] == 1
                    assert coupon_list_data['list'][0]['couponType'] == 1
                    assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                    assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                    assert coupon_list_data['list'][0]['couponState'] == '1'
                    assert coupon_list_data['list'][0]['couponAmount'] == self.coupon_amount
                    assert coupon_list_data['list'][0]['couponDiscount'] == 0
                    assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                    assert coupon_list_data['list'][0]['description'] == self.description
                    coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                    timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                    coupon_start_time_timeStamp = int(time.mktime(timeArray))
                    assert int(time.time()) - coupon_start_time_timeStamp < 180
                    assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+self.expire_time)).strftime("%Y-%m-%d 23:59")
                    break
            assert count < max_count

        # 先针对不存在用户发放，在针对不存在用户发放,不传userId
        new_mobile_one = TradeLoginApi().get_new_mobile()
        new_mobile_two = TradeLoginApi().get_new_mobile()
        # 调用红包充值接口
        for x in [new_mobile_one,new_mobile_two]:
            recharge_resp = recharge_logic(user_id=x,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=False)
            assert recharge_resp['errCode'] == '000000'
            assert recharge_resp['success'] == True
            assert recharge_resp['msg'] == '成功'
            assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        for x in [new_mobile_one,new_mobile_two]:
            while count < max_count:
                get_coupon_list_api = GetCouponListApi(mobile=x)
                get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
                assert get_coupon_list_api.get_status_code() == 200
                assert get_coupon_list_api.get_resp_code() == 0
                assert get_coupon_list_api.get_resp_message() == 'OK'
                coupon_list_data = get_coupon_list_api.get_resp_data()
                if len(coupon_list_data['list']) == 0:
                    count += 1
                    time.sleep(1)
                    continue
                else:
                    assert len(coupon_list_data['list']) == 1
                    assert coupon_list_data['total'] == 1
                    assert coupon_list_data['list'][0]['activityUseType'] == 1
                    assert coupon_list_data['list'][0]['couponType'] == 1
                    assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                    assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                    assert coupon_list_data['list'][0]['couponState'] == '1'
                    assert coupon_list_data['list'][0]['couponAmount'] == self.coupon_amount
                    assert coupon_list_data['list'][0]['couponDiscount'] == 0
                    assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                    assert coupon_list_data['list'][0]['description'] == self.description
                    coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                    timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                    coupon_start_time_timeStamp = int(time.mktime(timeArray))
                    assert int(time.time()) - coupon_start_time_timeStamp < 180
                    assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+self.expire_time)).strftime("%Y-%m-%d 23:59")
                    break
            assert count < max_count

        # 先针对已存在用户发放，在针对已存在用户发放,不传userId
        login_result_one = TradeLoginApi().login()
        user_id_one = login_result_one['mobile']
        login_result_two = TradeLoginApi().login()
        user_id_two = login_result_two['mobile']
        # 调用红包充值接口
        for x in [user_id_one,user_id_two]:
            recharge_resp = recharge_logic(user_id=x,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=False)
            assert recharge_resp['errCode'] == '000000'
            assert recharge_resp['success'] == True
            assert recharge_resp['msg'] == '成功'
            assert recharge_resp['data'] == None
        # 执行发券job
        XXLJob().run_job(job_id=10,sheet_job=False)
        time.sleep(1)
        # trade端验证发券
        for x in [user_id_one,user_id_two]:
            while count < max_count:
                get_coupon_list_api = GetCouponListApi(mobile=x)
                get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
                assert get_coupon_list_api.get_status_code() == 200
                assert get_coupon_list_api.get_resp_code() == 0
                assert get_coupon_list_api.get_resp_message() == 'OK'
                coupon_list_data = get_coupon_list_api.get_resp_data()
                if len(coupon_list_data['list']) == 0:
                    count += 1
                    time.sleep(1)
                    continue
                else:
                    assert len(coupon_list_data['list']) == 1
                    assert coupon_list_data['total'] == 1
                    assert coupon_list_data['list'][0]['activityUseType'] == 1
                    assert coupon_list_data['list'][0]['couponType'] == 1
                    assert coupon_list_data['list'][0]['couponName'] == self.activity_name
                    assert coupon_list_data['list'][0]['payAmount'] == self.pay_amount
                    assert coupon_list_data['list'][0]['couponState'] == '1'
                    assert coupon_list_data['list'][0]['couponAmount'] == self.coupon_amount
                    assert coupon_list_data['list'][0]['couponDiscount'] == 0
                    assert coupon_list_data['list'][0]['maxCouponAmount'] == self.coupon_amount
                    assert coupon_list_data['list'][0]['description'] == self.description
                    coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
                    timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                    coupon_start_time_timeStamp = int(time.mktime(timeArray))
                    assert int(time.time()) - coupon_start_time_timeStamp < 180
                    assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+self.expire_time)).strftime("%Y-%m-%d 23:59")
                    break
            assert count < max_count

    def coupon_recharge_closed(self):
        """
        测试红包充值活动手动终止
        :return:
        """
        now_time = datetime.datetime.now()
        start_time = (now_time + datetime.timedelta(hours=-5)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S")
        sign_id = '签报号-测试满减券红包充值过期'
        activity_name = '测试红包充值满减券过期'
        description = BaseFaker().create_sentence()  # 随机生成一段文字
        pay_amount = 10000
        coupon_amount = 5000
        expire_time = 10
        # 创建红包充值满减券
        create_activity_api = AddActivityApi()
        self.activity_id = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
        create_activity_api.post({"activityObject": 5, "activityStartTime": start_time,
                                  "activityEndTime": end_time, "activityName": activity_name,
                                  "signId": sign_id,
                                  "activityId": self.activity_id, "couponExpireTime": expire_time, "grantTotal": 100,
                                  "activityFrom": 5, "activityUseType": 1, "activityType": 1,
                                  "couponDiscount": "",
                                  "payAmount": pay_amount, "couponAmount": coupon_amount, "payAmountMin": "", "payAmountMax": "",
                                  "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
                                  "activityCycleType": "", "activityCycleTotalTime": "",
                                  "description": description})
        assert create_activity_api.get_status_code() == 200
        assert create_activity_api.get_resp_code() == 0
        assert create_activity_api.get_resp_message() == 'OK'
        self.activity_list.append({'activity_id': self.activity_id, 'sign_id': sign_id})  # 将该活动信息加入全局变量列表中
        time.sleep(10)

        # 根据活动ID查询
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 0,'activityId': self.activity_id, 'activityType': None, 'signId': None, 'pageSize': 1000,'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        assert len(activity_list) == 1
        assert activity_list[0]['activityStatusDesc'] == '生效'
        a_id = activity_list[0]['id']

        # 调用终止活动接口
        close_activity_api = CloseActivityApi()
        close_activity_api.post({'activityStatus': 2, 'id': a_id})
        assert close_activity_api.get_status_code() == 200
        assert close_activity_api.get_resp_code() == 0
        assert close_activity_api.get_resp_message() == 'OK'
        time.sleep(15)
        # 根据活动ID查询
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 0,'activityId': self.activity_id, 'activityType': None, 'signId': None, 'pageSize': 1000,'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        assert len(activity_list) == 1
        assert activity_list[0]['activityStatusDesc'] == '终止'

        def recharge_logic(user_id,event_id,coupon_amount,expire_time,is_user_id):
            event_id = event_id
            coupon_amount = coupon_amount
            expire_time = expire_time
            sign_key = 'bksk123kvzcnAadDnmas1;fnopij'

            def get_random_trade_no():
                """
                随机生成订单号并且数据库中不存在
                :return:
                """
                while True:
                    num = str(int(time.time())) + str(random.randint(1000, 9999))
                    result = mysql_execute('select * from tbl_trade_order where id=%s', params=(num), trade=True)
                    if not result:
                        return num

            recharge_from = '1'  # 充值来源 1=红包平台充值
            trade_no = get_random_trade_no()  # 订单号
            customer_detail = mysql_execute('select * from tbl_trade_customer where user_id=%s', params=(user_id),
                                            trade=True)
            if customer_detail:
                logger.info('user is active!')
                id_num = customer_detail['id_num']
                logger.info(id_num)
            else:
                id_num = user_id + '9999999'
                logger.info(id_num)

            time_stamp = str(int(time.time()) * 1000)  # 时间戳（当前毫秒时间戳）
            sign_list = []
            if is_user_id:
                sign_list.append(user_id)
            if coupon_amount:
                sign_list.append(str(coupon_amount))
            if expire_time:
                sign_list.append(str(expire_time))
            sign_list.append(id_num)
            sign_list.append(trade_no)
            sign_list.append(event_id)
            sign_list.append(recharge_from)
            sign_list.append(time_stamp)
            sign_list.append(sign_key)
            sign_list.sort()
            sign_str = ''
            for x in sign_list:
                sign_str += x
            sign = hashlib.sha1(sign_str.encode()).hexdigest()
            logger.info('Sign is:{0}'.format(sign))

            if not coupon_amount:
                coupon_amount = None
            if not expire_time:
                expire_time = None

            data = {"eventId": event_id, "idNum": id_num, "rechargeFrom": recharge_from, "sign": sign,
                    "timestamp": time_stamp, "tradeNo": trade_no}
            if int(is_user_id) == 1:
                data.update({"userId": user_id})
            if coupon_amount:
                data.update({"couponAmount": coupon_amount})
            if expire_time:
                data.update({"expireTime": expire_time})

            logger.info('request url:{0}'.format(SPDB_COUPON_RECHARGE_API_URL))
            logger.info('request data:{0}'.format(data))

            response = requests.post(url=SPDB_COUPON_RECHARGE_API_URL, json=data, headers=settings.API_HEADERS)
            logger.info('response:{0}'.format(response.text))
            return json.loads(response.content)

        # 获取不存在用户手机号码
        user_id = TradeLoginApi().get_new_mobile()
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=True)
        assert recharge_resp['errCode'] == 'YC0303'
        assert recharge_resp['success'] == False
        assert recharge_resp['msg'] == '活动已结束'
        assert recharge_resp['data'] == None

        # 获取不存在用户手机号码
        user_id = TradeLoginApi().get_new_mobile()
        # 调用红包充值接口，不传userId
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=False)
        assert recharge_resp['errCode'] == 'YC0303'
        assert recharge_resp['success'] == False
        assert recharge_resp['msg'] == '活动已结束'
        assert recharge_resp['data'] == None

    def coupon_recharge_over_due(self):
        """
        测试红包充值活动自动过期
        :return:
        """
        now_time = datetime.datetime.now()
        start_time = (now_time + datetime.timedelta(hours=-5)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (now_time + datetime.timedelta(minutes=+2)).strftime("%Y-%m-%d %H:%M:%S")
        sign_id = '签报号-测试满减券红包充值自动过期'
        activity_name = '测试红包充值满减券自动过期'
        description = BaseFaker().create_sentence()  # 随机生成一段文字
        pay_amount = 10000
        coupon_amount = 5000
        expire_time = 10
        # 创建红包充值满减券
        create_activity_api = AddActivityApi()
        self.activity_id = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
        create_activity_api.post({"activityObject": 5, "activityStartTime": start_time,
                                  "activityEndTime": end_time, "activityName": activity_name,
                                  "signId": sign_id,
                                  "activityId": self.activity_id, "couponExpireTime": expire_time, "grantTotal": 100,
                                  "activityFrom": 5, "activityUseType": 1, "activityType": 1,
                                  "couponDiscount": "",
                                  "payAmount": pay_amount, "couponAmount": coupon_amount, "payAmountMin": "", "payAmountMax": "",
                                  "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
                                  "activityCycleType": "", "activityCycleTotalTime": "",
                                  "description": description})
        assert create_activity_api.get_status_code() == 200
        assert create_activity_api.get_resp_code() == 0
        assert create_activity_api.get_resp_message() == 'OK'
        self.activity_list.append({'activity_id': self.activity_id, 'sign_id': sign_id})  # 将该活动信息加入全局变量列表中

        # 根据活动ID查询
        count = 1
        max_count = 100
        while count < max_count:
            get_activity_list_api = GetActivityListApi()
            get_activity_list_api.get({'activityStatus': 0,'activityId': self.activity_id, 'activityType': None, 'signId': None, 'pageSize': 1000,'pageNum': 1})
            assert get_activity_list_api.get_status_code() == 200
            assert get_activity_list_api.get_resp_code() == 0
            assert get_activity_list_api.get_resp_message() == 'OK'
            activity_list = get_activity_list_api.get_resp_data()['list']
            assert len(activity_list) == 1
            if  activity_list[0]['activityStatusDesc'] != '生效':
                assert activity_list[0]['activityStatusDesc'] == '终止'
                time.sleep(15)
                break
            else:
                time.sleep(2)
                count += 1

        def recharge_logic(user_id,event_id,coupon_amount,expire_time,is_user_id):
            event_id = event_id
            coupon_amount = coupon_amount
            expire_time = expire_time
            sign_key = 'bksk123kvzcnAadDnmas1;fnopij'

            def get_random_trade_no():
                """
                随机生成订单号并且数据库中不存在
                :return:
                """
                while True:
                    num = str(int(time.time())) + str(random.randint(1000, 9999))
                    result = mysql_execute('select * from tbl_trade_order where id=%s', params=(num), trade=True)
                    if not result:
                        return num

            recharge_from = '1'  # 充值来源 1=红包平台充值
            trade_no = get_random_trade_no()  # 订单号
            customer_detail = mysql_execute('select * from tbl_trade_customer where user_id=%s', params=(user_id),
                                            trade=True)
            if customer_detail:
                logger.info('user is active!')
                id_num = customer_detail['id_num']
                logger.info(id_num)
            else:
                id_num = user_id + '9999999'
                logger.info(id_num)

            time_stamp = str(int(time.time()) * 1000)  # 时间戳（当前毫秒时间戳）
            sign_list = []
            if is_user_id:
                sign_list.append(user_id)
            if coupon_amount:
                sign_list.append(str(coupon_amount))
            if expire_time:
                sign_list.append(str(expire_time))
            sign_list.append(id_num)
            sign_list.append(trade_no)
            sign_list.append(event_id)
            sign_list.append(recharge_from)
            sign_list.append(time_stamp)
            sign_list.append(sign_key)
            sign_list.sort()
            sign_str = ''
            for x in sign_list:
                sign_str += x
            sign = hashlib.sha1(sign_str.encode()).hexdigest()
            logger.info('Sign is:{0}'.format(sign))

            if not coupon_amount:
                coupon_amount = None
            if not expire_time:
                expire_time = None

            data = {"eventId": event_id, "idNum": id_num, "rechargeFrom": recharge_from, "sign": sign,
                    "timestamp": time_stamp, "tradeNo": trade_no}
            if int(is_user_id) == 1:
                data.update({"userId": user_id})
            if coupon_amount:
                data.update({"couponAmount": coupon_amount})
            if expire_time:
                data.update({"expireTime": expire_time})

            logger.info('request url:{0}'.format(SPDB_COUPON_RECHARGE_API_URL))
            logger.info('request data:{0}'.format(data))

            response = requests.post(url=SPDB_COUPON_RECHARGE_API_URL, json=data, headers=settings.API_HEADERS)
            logger.info('response:{0}'.format(response.text))
            return json.loads(response.content)

        # 获取不存在用户手机号码
        user_id = TradeLoginApi().get_new_mobile()
        # 调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=True)
        assert recharge_resp['errCode'] == 'YC0303'
        assert recharge_resp['success'] == False
        assert recharge_resp['msg'] == '活动已结束'
        assert recharge_resp['data'] == None

        # 获取不存在用户手机号码
        user_id = TradeLoginApi().get_new_mobile()
        # 调用红包充值接口,不传userId
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=False)
        assert recharge_resp['errCode'] == 'YC0303'
        assert recharge_resp['success'] == False
        assert recharge_resp['msg'] == '活动已结束'
        assert recharge_resp['data'] == None

    def coupon_recharge_quota_full(self):
        """
        测试红包充值活动名额已满
        :return:
        """
        now_time = datetime.datetime.now()
        start_time = (now_time + datetime.timedelta(hours=-5)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (now_time + datetime.timedelta(minutes=+30)).strftime("%Y-%m-%d %H:%M:%S")
        sign_id = '签报号-测试满减券红包充值名额已满'
        activity_name = '测试红包充值满减券名额已满'
        description = BaseFaker().create_sentence()  # 随机生成一段文字
        pay_amount = 10000
        coupon_amount = 5000
        expire_time = 10
        # 创建红包充值满减券
        create_activity_api = AddActivityApi()
        self.activity_id = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
        create_activity_api.post({"activityObject": 5, "activityStartTime": start_time,
                                  "activityEndTime": end_time, "activityName": activity_name,
                                  "signId": sign_id,
                                  "activityId": self.activity_id, "couponExpireTime": expire_time, "grantTotal": 2,
                                  "activityFrom": 5, "activityUseType": 1, "activityType": 1,
                                  "couponDiscount": "",
                                  "payAmount": pay_amount, "couponAmount": coupon_amount, "payAmountMin": "", "payAmountMax": "",
                                  "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
                                  "activityCycleType": "", "activityCycleTotalTime": "",
                                  "description": description})
        assert create_activity_api.get_status_code() == 200
        assert create_activity_api.get_resp_code() == 0
        assert create_activity_api.get_resp_message() == 'OK'
        self.activity_list.append({'activity_id': self.activity_id, 'sign_id': sign_id})  # 将该活动信息加入全局变量列表中
        time.sleep(20)
        # 查询活动id查询
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 0,'activityId': self.activity_id, 'activityType': None, 'signId': None, 'pageSize': 100,'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        assert activity_list[0]['activityId'] == self.activity_id
        assert activity_list[0]['activityStatusDesc'] == '生效'

        def recharge_logic(user_id,event_id,coupon_amount,expire_time,is_user_id):
            event_id = event_id
            coupon_amount = coupon_amount
            expire_time = expire_time
            sign_key = 'bksk123kvzcnAadDnmas1;fnopij'

            def get_random_trade_no():
                """
                随机生成订单号并且数据库中不存在
                :return:
                """
                while True:
                    num = str(int(time.time())) + str(random.randint(1000, 9999))
                    result = mysql_execute('select * from tbl_trade_order where id=%s', params=(num), trade=True)
                    if not result:
                        return num

            recharge_from = '1'  # 充值来源 1=红包平台充值
            trade_no = get_random_trade_no()  # 订单号
            customer_detail = mysql_execute('select * from tbl_trade_customer where user_id=%s', params=(user_id),
                                            trade=True)
            if customer_detail:
                logger.info('user is active!')
                id_num = customer_detail['id_num']
                logger.info(id_num)
            else:
                id_num = user_id + '9999999'
                logger.info(id_num)

            time_stamp = str(int(time.time()) * 1000)  # 时间戳（当前毫秒时间戳）
            sign_list = []
            if is_user_id:
                sign_list.append(user_id)
            if coupon_amount:
                sign_list.append(str(coupon_amount))
            if expire_time:
                sign_list.append(str(expire_time))
            sign_list.append(id_num)
            sign_list.append(trade_no)
            sign_list.append(event_id)
            sign_list.append(recharge_from)
            sign_list.append(time_stamp)
            sign_list.append(sign_key)
            sign_list.sort()
            sign_str = ''
            for x in sign_list:
                sign_str += x
            sign = hashlib.sha1(sign_str.encode()).hexdigest()
            logger.info('Sign is:{0}'.format(sign))

            if not coupon_amount:
                coupon_amount = None
            if not expire_time:
                expire_time = None

            data = {"eventId": event_id, "idNum": id_num, "rechargeFrom": recharge_from, "sign": sign,
                    "timestamp": time_stamp, "tradeNo": trade_no}
            if int(is_user_id) == 1:
                data.update({"userId": user_id})
            if coupon_amount:
                data.update({"couponAmount": coupon_amount})
            if expire_time:
                data.update({"expireTime": expire_time})

            logger.info('request url:{0}'.format(SPDB_COUPON_RECHARGE_API_URL))
            logger.info('request data:{0}'.format(data))

            response = requests.post(url=SPDB_COUPON_RECHARGE_API_URL, json=data, headers=settings.API_HEADERS)
            logger.info('response:{0}'.format(response.text))
            return json.loads(response.content)

        # 获取不存在用户手机号码
        user_id = TradeLoginApi().get_new_mobile()
        # 第一次调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=True)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 获取不存在用户手机号码
        user_id = TradeLoginApi().get_new_mobile()
        # 第二次调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=True)
        assert recharge_resp['errCode'] == '000000'
        assert recharge_resp['success'] == True
        assert recharge_resp['msg'] == '成功'
        assert recharge_resp['data'] == None
        # 获取不存在用户手机号码
        user_id = TradeLoginApi().get_new_mobile()
        # 第三次调用红包充值接口
        recharge_resp = recharge_logic(user_id=user_id,event_id=self.activity_id,coupon_amount=None,expire_time=None,is_user_id=True)
        assert recharge_resp['errCode'] == 'YC0305'
        assert recharge_resp['success'] == False
        assert recharge_resp['msg'] == '优惠券库存数量不足'
        assert recharge_resp['data'] == None

    def tearDown(self):
        super(CouponRechargeMonitoring, self).tearDown()
        for x in self.activity_list:
            hooks.delete_activity(x['activity_id'], sign_id=x['sign_id'])
        self.activity_list = []
        time.sleep(5)

if __name__ == '__main__':
    # api = CouponRechargeMonitoring()
    # api.setUp()
    # api.coupon_recharge()
    # api.tearDown()
    api = CouponRechargeMonitoring()
    api.run_method(monitoring_name='红包充值监控',monitoring_class=api,redis_key=COUPON_RECHARGE_MONITORING_KEY)

