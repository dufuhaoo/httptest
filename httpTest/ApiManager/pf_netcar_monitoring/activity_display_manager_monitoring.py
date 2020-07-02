# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_monitoring.base_monitoring import BaseMonitoring
from ApiManager.pf_netcar_api.sheet.activity_manager_api import AddActivityApi,GetActivityListApi,CloseActivityApi
from ApiManager.pf_netcar_api.sheet.activity_display_api import AddActivityDisplayApi,GetActivityDisplayApi,EditActivityDisplayApi,RefreshActivityDisplayCacheApi
from ApiManager.utils import hooks
from ApiManager.pf_netcar_api.trade.query_can_use_coupon_api import QueryCanUseCouponApi,QueryLoginCustomerCanUseCouponApi
from ApiManager.utils.faker_data import BaseFaker
from ApiManager.utils.redis_helper import ACTIVITY_DISPLAY_MANAGER_MONITORING_KEY
import datetime, time


class ActivityDisplayManagerMonitoring(BaseMonitoring):
    """
    活动展示管理监控
    """
    now_time = datetime.datetime.now()
    start_time = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S")
    activity_list = []

    def setUp(self):
        super(ActivityDisplayManagerMonitoring,self).setUp()
        hooks.delete_activity_display()
        # 查询当前生效的随机立减活动
        get_activity_list = GetActivityListApi()
        get_activity_list.get({'activityStatus': 1,'activityId': None,'activityType': 3,'signId': None,'pageSize': 100,'pageNum': 1})
        assert get_activity_list.get_status_code() == 200
        assert get_activity_list.get_resp_code() == 0
        activity_list_data = get_activity_list.get_resp_data()
        # 如果存在生效的活动，则调用关闭活动接口终止该活动
        if activity_list_data['list']:
            for x in activity_list_data['list']:
                activity_id = x['id']
                close_activity_api = CloseActivityApi()
                close_activity_api.post({'activityStatus': 2, 'id':activity_id})
                assert close_activity_api.get_status_code() == 200
                assert close_activity_api.get_resp_code() == 0
            time.sleep(5)

    def activity_display(self):
        """
        测试创建活动展示
        :return:
        """
        grant_total = 100
        activity_cycle_total_time = 50
        # 创建随机立减活动
        create_activity_api = AddActivityApi()
        description = BaseFaker().create_sentence()  # 随机生成一段文字
        random_activity_id = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
        create_activity_api.post(
            {"activityStartTime": self.start_time, "activityEndTime": self.end_time,
             "activityType": "3", "activityObject": 1, "couponExpireTime": "", "grantTotal": str(grant_total),
             "couponDiscount": "", "payAmount": "", "couponAmount": "", "activityName": '测试活动查询随机立减',
             "signId": '签报号-测试活动展示', "activityId": random_activity_id, "payAmountMin": 10000, "discountAmountMin": 2000,
             "discountAmountMax": 3000, "activityPeopleCount": "2", "activityCycleType": 1,
             "activityCycleTotalTime": str(activity_cycle_total_time), "activityFrom": 1, "activityUseType": 1,
             "description": description})
        assert create_activity_api.get_status_code() == 200
        assert create_activity_api.get_resp_code() == 0
        assert create_activity_api.get_resp_message() == 'OK'
        self.activity_list.append({'activity_id': random_activity_id, 'sign_id': '签报号-测试活动展示'})  # 将该活动信息加入全局变量列表中
        time.sleep(10)
        # 查询活动id查询
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 0,'activityId': random_activity_id, 'activityType': None, 'signId': None, 'pageSize': 100,'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        assert activity_list[0]['activityId'] == random_activity_id
        a_id = activity_list[0]['id']
        # 测试添加时满足金额为空
        add_activity_display_api = AddActivityDisplayApi()
        add_activity_display_api.post({"orderPrice":None,"reducePrice":3000,"limitCount":20,"state":1})
        assert add_activity_display_api.get_status_code() == 200
        assert add_activity_display_api.get_resp_code() == 100101
        assert add_activity_display_api.get_resp_message() == '请检查输入项'
        assert add_activity_display_api.get_resp_data() == '字段[orderPrice]格式错误！'
        # 测试添加时优惠金额为空
        add_activity_display_api = AddActivityDisplayApi()
        add_activity_display_api.post({"orderPrice":10000,"reducePrice":None,"limitCount":20,"state":1})
        assert add_activity_display_api.get_status_code() == 200
        assert add_activity_display_api.get_resp_code() == 100101
        assert add_activity_display_api.get_resp_message() == '请检查输入项'
        assert add_activity_display_api.get_resp_data() == '字段[reducePrice]格式错误！'
        # 测试添加时剩余数量为空
        add_activity_display_api = AddActivityDisplayApi()
        add_activity_display_api.post({"orderPrice":10000,"reducePrice":3000,"limitCount":None,"state":1})
        assert add_activity_display_api.get_status_code() == 200
        assert add_activity_display_api.get_resp_code() == 100101
        assert add_activity_display_api.get_resp_message() == '请检查输入项'
        assert add_activity_display_api.get_resp_data() == '字段[limitCount]格式错误！'
        # 测试添加时状态为空时，默认为开启
        add_activity_display_api = AddActivityDisplayApi()
        add_activity_display_api.post({"orderPrice": 10000, "reducePrice": 3000, "limitCount": 20, "state": None})
        assert add_activity_display_api.get_status_code() == 200
        assert add_activity_display_api.get_resp_code() == 0
        assert add_activity_display_api.get_resp_message() == 'OK'
        # 刷新缓存
        refresh_cache_api = RefreshActivityDisplayCacheApi()
        refresh_cache_api.get()
        assert refresh_cache_api.get_status_code() == 200
        assert refresh_cache_api.get_resp_code() == 0
        assert refresh_cache_api.get_resp_message() == 'OK'
        # 获取活动展示列表
        get_activity_display_list_api = GetActivityDisplayApi()
        get_activity_display_list_api.get({'state':None})
        assert get_activity_display_list_api.get_status_code() == 200
        assert get_activity_display_list_api.get_resp_code() == 0
        assert get_activity_display_list_api.get_resp_message() == 'OK'
        activity_display_data = get_activity_display_list_api.get_resp_data()
        assert activity_display_data['list'][0]['orderPrice'] == '10000'
        assert activity_display_data['list'][0]['limitCount'] == '20'
        assert activity_display_data['list'][0]['reducePrice'] == '3000'
        assert activity_display_data['list'][0]['state'] == 1
        create_time = activity_display_data['list'][0]['createTime']
        timeArray = time.strptime(create_time, "%Y-%m-%d %H:%M:%S")
        create_time_timeStamp = int(time.mktime(timeArray))
        assert int(time.time()) - create_time_timeStamp < 120
        activity_display_id = activity_display_data['list'][0]['id']

        # 验证trade端已登录用户
        query_login_customer_can_use_coupon_api = QueryLoginCustomerCanUseCouponApi()
        query_login_customer_can_use_coupon_api.get()
        assert query_login_customer_can_use_coupon_api.get_status_code() == 200
        assert query_login_customer_can_use_coupon_api.get_resp_code() == 0
        assert query_login_customer_can_use_coupon_api.get_resp_message() == 'OK'
        query_login_customer_can_use_coupon_data = query_login_customer_can_use_coupon_api.get_resp_data()
        assert query_login_customer_can_use_coupon_data['orderPrice'] == 10000
        assert query_login_customer_can_use_coupon_data['reducePrice'] == 3000
        assert query_login_customer_can_use_coupon_data['canCompute'] == True
        # 验证trade端未登录用户
        query_can_use_coupon_api = QueryCanUseCouponApi()
        query_can_use_coupon_api.get()
        assert query_can_use_coupon_api.get_status_code() == 200
        assert query_can_use_coupon_api.get_resp_code() == 0
        assert query_can_use_coupon_api.get_resp_message() == 'OK'
        query_can_use_coupon_data = query_can_use_coupon_api.get_resp_data()
        assert query_can_use_coupon_data['orderPrice'] == 10000
        assert query_can_use_coupon_data['reducePrice'] == 3000
        assert query_can_use_coupon_data['canCompute'] == True

        # 修改活动展示满足金额为空
        edit_activity_display_api = EditActivityDisplayApi()
        edit_activity_display_api.post({"orderPrice":None,"reducePrice":500,"limitCount":5,"state":1,'id':activity_display_id})
        assert edit_activity_display_api.get_status_code() == 200
        assert edit_activity_display_api.get_resp_code() == 100101
        assert edit_activity_display_api.get_resp_message() == '请检查输入项'
        assert edit_activity_display_api.get_resp_data() == '字段[orderPrice]格式错误！'
        # 修改活动展示优惠金额为空
        edit_activity_display_api = EditActivityDisplayApi()
        edit_activity_display_api.post({"orderPrice":5000,"reducePrice":None,"limitCount":5,"state":1,'id':activity_display_id})
        assert edit_activity_display_api.get_status_code() == 200
        assert edit_activity_display_api.get_resp_code() == 100101
        assert edit_activity_display_api.get_resp_message() == '请检查输入项'
        assert edit_activity_display_api.get_resp_data() == '字段[reducePrice]格式错误！'
        # 修改活动展示剩余数量为空
        edit_activity_display_api = EditActivityDisplayApi()
        edit_activity_display_api.post({"orderPrice":5000,"reducePrice":500,"limitCount":None,"state":1,'id':activity_display_id})
        assert edit_activity_display_api.get_status_code() == 200
        assert edit_activity_display_api.get_resp_code() == 100101
        assert edit_activity_display_api.get_resp_message() == '请检查输入项'
        assert edit_activity_display_api.get_resp_data() == '字段[limitCount]格式错误！'
        # 修改活动展示id为空
        edit_activity_display_api = EditActivityDisplayApi()
        edit_activity_display_api.post({"orderPrice": 5000, "reducePrice": 500, "limitCount": 5, "state": 1, 'id': None})
        assert edit_activity_display_api.get_status_code() == 200
        assert edit_activity_display_api.get_resp_code() == 100101
        assert edit_activity_display_api.get_resp_message() == '请检查输入项'
        assert edit_activity_display_api.get_resp_data() == '字段[id]格式错误！'
        # 修改活动展示满足金额、优惠金额、剩余数量
        edit_activity_display_api = EditActivityDisplayApi()
        edit_activity_display_api.post({"orderPrice": 5000, "reducePrice": 500, "limitCount": 5, "state": 1, 'id': activity_display_id})
        assert edit_activity_display_api.get_status_code() == 200
        assert edit_activity_display_api.get_resp_code() == 0
        assert edit_activity_display_api.get_resp_message() == 'OK'
        # 刷新缓存
        refresh_cache_api = RefreshActivityDisplayCacheApi()
        refresh_cache_api.get()
        assert refresh_cache_api.get_status_code() == 200
        assert refresh_cache_api.get_resp_code() == 0
        assert refresh_cache_api.get_resp_message() == 'OK'
        # 获取活动展示列表
        get_activity_display_list_api = GetActivityDisplayApi()
        get_activity_display_list_api.get({'state':None})
        assert get_activity_display_list_api.get_status_code() == 200
        assert get_activity_display_list_api.get_resp_code() == 0
        assert get_activity_display_list_api.get_resp_message() == 'OK'
        activity_display_data = get_activity_display_list_api.get_resp_data()
        assert activity_display_data['list'][0]['orderPrice'] == '5000'
        assert activity_display_data['list'][0]['limitCount'] == '5'
        assert activity_display_data['list'][0]['reducePrice'] == '500'
        assert activity_display_data['list'][0]['state'] == 1
        create_time = activity_display_data['list'][0]['createTime']
        timeArray = time.strptime(create_time, "%Y-%m-%d %H:%M:%S")
        create_time_timeStamp = int(time.mktime(timeArray))
        assert int(time.time()) - create_time_timeStamp < 120
        # 验证trade端已登录用户
        query_login_customer_can_use_coupon_api = QueryLoginCustomerCanUseCouponApi()
        query_login_customer_can_use_coupon_api.get()
        assert query_login_customer_can_use_coupon_api.get_status_code() == 200
        assert query_login_customer_can_use_coupon_api.get_resp_code() == 0
        assert query_login_customer_can_use_coupon_api.get_resp_message() == 'OK'
        query_login_customer_can_use_coupon_data = query_login_customer_can_use_coupon_api.get_resp_data()
        assert query_login_customer_can_use_coupon_data['orderPrice'] == 5000
        assert query_login_customer_can_use_coupon_data['reducePrice'] == 500
        assert query_login_customer_can_use_coupon_data['canCompute'] == True
        # 验证trade端未登录用户
        query_can_use_coupon_api = QueryCanUseCouponApi()
        query_can_use_coupon_api.get()
        assert query_can_use_coupon_api.get_status_code() == 200
        assert query_can_use_coupon_api.get_resp_code() == 0
        assert query_can_use_coupon_api.get_resp_message() == 'OK'
        query_can_use_coupon_data = query_can_use_coupon_api.get_resp_data()
        assert query_can_use_coupon_data['orderPrice'] == 5000
        assert query_can_use_coupon_data['reducePrice'] == 500
        assert query_can_use_coupon_data['canCompute'] == True

        # 验证当日剩余数量达到6次时，trade端展示
        hooks.fix_random_activity_use_num(activity_id=a_id, type='all',number=activity_cycle_total_time - 6)
        hooks.fix_random_activity_use_num(activity_id=a_id,type='cycle',number=activity_cycle_total_time - 6)
        # 验证trade端已登录用户
        query_login_customer_can_use_coupon_api = QueryLoginCustomerCanUseCouponApi()
        query_login_customer_can_use_coupon_api.get()
        assert query_login_customer_can_use_coupon_api.get_status_code() == 200
        assert query_login_customer_can_use_coupon_api.get_resp_code() == 0
        assert query_login_customer_can_use_coupon_api.get_resp_message() == 'OK'
        query_login_customer_can_use_coupon_data = query_login_customer_can_use_coupon_api.get_resp_data()
        assert query_login_customer_can_use_coupon_data['orderPrice'] == 5000
        assert query_login_customer_can_use_coupon_data['reducePrice'] == 500
        assert query_login_customer_can_use_coupon_data['canCompute'] == True
        # 验证trade端未登录用户
        query_can_use_coupon_api = QueryCanUseCouponApi()
        query_can_use_coupon_api.get()
        assert query_can_use_coupon_api.get_status_code() == 200
        assert query_can_use_coupon_api.get_resp_code() == 0
        assert query_can_use_coupon_api.get_resp_message() == 'OK'
        query_can_use_coupon_data = query_can_use_coupon_api.get_resp_data()
        assert query_can_use_coupon_data['orderPrice'] == 5000
        assert query_can_use_coupon_data['reducePrice'] == 500
        assert query_can_use_coupon_data['canCompute'] == True
        # 验证当日剩余数量达到5次时，trade端展示
        hooks.fix_random_activity_use_num(activity_id=a_id, type='all',number=activity_cycle_total_time - 5)
        hooks.fix_random_activity_use_num(activity_id=a_id,type='cycle',number=activity_cycle_total_time - 5)
        # 验证trade端已登录用户
        query_login_customer_can_use_coupon_api = QueryLoginCustomerCanUseCouponApi()
        query_login_customer_can_use_coupon_api.get()
        assert query_login_customer_can_use_coupon_api.get_status_code() == 200
        assert query_login_customer_can_use_coupon_api.get_resp_code() == 0
        assert query_login_customer_can_use_coupon_api.get_resp_message() == 'OK'
        query_login_customer_can_use_coupon_data = query_login_customer_can_use_coupon_api.get_resp_data()
        assert query_login_customer_can_use_coupon_data['orderPrice'] == None
        assert query_login_customer_can_use_coupon_data['reducePrice'] == None
        assert query_login_customer_can_use_coupon_data['canCompute'] == False
        # 验证trade端未登录用户
        query_can_use_coupon_api = QueryCanUseCouponApi()
        query_can_use_coupon_api.get()
        assert query_can_use_coupon_api.get_status_code() == 200
        assert query_can_use_coupon_api.get_resp_code() == 0
        assert query_can_use_coupon_api.get_resp_message() == 'OK'
        query_can_use_coupon_data = query_can_use_coupon_api.get_resp_data()
        assert query_can_use_coupon_data['orderPrice'] == None
        assert query_can_use_coupon_data['reducePrice'] == None
        assert query_can_use_coupon_data['canCompute'] == False

        # 验证当日剩余数量达到4次时，trade端不展示
        hooks.fix_random_activity_use_num(activity_id=a_id, type='all',number=activity_cycle_total_time - 4)
        hooks.fix_random_activity_use_num(activity_id=a_id,type='cycle',number=activity_cycle_total_time - 4)
        # 验证trade端已登录用户
        query_login_customer_can_use_coupon_api = QueryLoginCustomerCanUseCouponApi()
        query_login_customer_can_use_coupon_api.get()
        assert query_login_customer_can_use_coupon_api.get_status_code() == 200
        assert query_login_customer_can_use_coupon_api.get_resp_code() == 0
        assert query_login_customer_can_use_coupon_api.get_resp_message() == 'OK'
        query_login_customer_can_use_coupon_data = query_login_customer_can_use_coupon_api.get_resp_data()
        assert query_login_customer_can_use_coupon_data['orderPrice'] == None
        assert query_login_customer_can_use_coupon_data['reducePrice'] == None
        assert query_login_customer_can_use_coupon_data['canCompute'] == False
        # 验证trade端未登录用户
        query_can_use_coupon_api = QueryCanUseCouponApi()
        query_can_use_coupon_api.get()
        assert query_can_use_coupon_api.get_status_code() == 200
        assert query_can_use_coupon_api.get_resp_code() == 0
        assert query_can_use_coupon_api.get_resp_message() == 'OK'
        query_can_use_coupon_data = query_can_use_coupon_api.get_resp_data()
        assert query_can_use_coupon_data['orderPrice'] == None
        assert query_can_use_coupon_data['reducePrice'] == None
        assert query_can_use_coupon_data['canCompute'] == False

        # 验证活动总剩余数量达到6次,当日使用次数为0时，trade端展示
        hooks.fix_random_activity_use_num(activity_id=a_id, type='all',number=grant_total - 6)
        hooks.fix_random_activity_use_num(activity_id=a_id,type='cycle',number=0)
        # 验证trade端已登录用户
        query_login_customer_can_use_coupon_api = QueryLoginCustomerCanUseCouponApi()
        query_login_customer_can_use_coupon_api.get()
        assert query_login_customer_can_use_coupon_api.get_status_code() == 200
        assert query_login_customer_can_use_coupon_api.get_resp_code() == 0
        assert query_login_customer_can_use_coupon_api.get_resp_message() == 'OK'
        query_login_customer_can_use_coupon_data = query_login_customer_can_use_coupon_api.get_resp_data()
        assert query_login_customer_can_use_coupon_data['orderPrice'] == 5000
        assert query_login_customer_can_use_coupon_data['reducePrice'] == 500
        assert query_login_customer_can_use_coupon_data['canCompute'] == True
        # 验证trade端未登录用户
        query_can_use_coupon_api = QueryCanUseCouponApi()
        query_can_use_coupon_api.get()
        assert query_can_use_coupon_api.get_status_code() == 200
        assert query_can_use_coupon_api.get_resp_code() == 0
        assert query_can_use_coupon_api.get_resp_message() == 'OK'
        query_can_use_coupon_data = query_can_use_coupon_api.get_resp_data()
        assert query_can_use_coupon_data['orderPrice'] == 5000
        assert query_can_use_coupon_data['reducePrice'] == 500
        assert query_can_use_coupon_data['canCompute'] == True

        # 验证活动总剩余数量达到5次,当日使用次数为1时，trade端展示
        hooks.fix_random_activity_use_num(activity_id=a_id, type='all',number=grant_total - 5)
        hooks.fix_random_activity_use_num(activity_id=a_id,type='cycle',number=1)
        # 验证trade端已登录用户
        query_login_customer_can_use_coupon_api = QueryLoginCustomerCanUseCouponApi()
        query_login_customer_can_use_coupon_api.get()
        assert query_login_customer_can_use_coupon_api.get_status_code() == 200
        assert query_login_customer_can_use_coupon_api.get_resp_code() == 0
        assert query_login_customer_can_use_coupon_api.get_resp_message() == 'OK'
        query_login_customer_can_use_coupon_data = query_login_customer_can_use_coupon_api.get_resp_data()
        assert query_login_customer_can_use_coupon_data['orderPrice'] == None
        assert query_login_customer_can_use_coupon_data['reducePrice'] == None
        assert query_login_customer_can_use_coupon_data['canCompute'] == False
        # 验证trade端未登录用户
        query_can_use_coupon_api = QueryCanUseCouponApi()
        query_can_use_coupon_api.get()
        assert query_can_use_coupon_api.get_status_code() == 200
        assert query_can_use_coupon_api.get_resp_code() == 0
        assert query_can_use_coupon_api.get_resp_message() == 'OK'
        query_can_use_coupon_data = query_can_use_coupon_api.get_resp_data()
        assert query_can_use_coupon_data['orderPrice'] == None
        assert query_can_use_coupon_data['reducePrice'] == None
        assert query_can_use_coupon_data['canCompute'] == False

        # 验证活动总剩余数量达到4次,当日使用次数为1时，trade端展示
        hooks.fix_random_activity_use_num(activity_id=a_id, type='all',number=grant_total - 4)
        hooks.fix_random_activity_use_num(activity_id=a_id,type='cycle',number=1)
        # 验证trade端已登录用户
        query_login_customer_can_use_coupon_api = QueryLoginCustomerCanUseCouponApi()
        query_login_customer_can_use_coupon_api.get()
        assert query_login_customer_can_use_coupon_api.get_status_code() == 200
        assert query_login_customer_can_use_coupon_api.get_resp_code() == 0
        assert query_login_customer_can_use_coupon_api.get_resp_message() == 'OK'
        query_login_customer_can_use_coupon_data = query_login_customer_can_use_coupon_api.get_resp_data()
        assert query_login_customer_can_use_coupon_data['orderPrice'] == None
        assert query_login_customer_can_use_coupon_data['reducePrice'] == None
        assert query_login_customer_can_use_coupon_data['canCompute'] == False
        # 验证trade端未登录用户
        query_can_use_coupon_api = QueryCanUseCouponApi()
        query_can_use_coupon_api.get()
        assert query_can_use_coupon_api.get_status_code() == 200
        assert query_can_use_coupon_api.get_resp_code() == 0
        assert query_can_use_coupon_api.get_resp_message() == 'OK'
        query_can_use_coupon_data = query_can_use_coupon_api.get_resp_data()
        assert query_can_use_coupon_data['orderPrice'] == None
        assert query_can_use_coupon_data['reducePrice'] == None
        assert query_can_use_coupon_data['canCompute'] == False

        # 修改活动展示状态为关闭
        edit_activity_display_api = EditActivityDisplayApi()
        edit_activity_display_api.post({"orderPrice": 5000, "reducePrice": 500, "limitCount": 5, "state": 2, 'id': activity_display_id})
        assert edit_activity_display_api.get_status_code() == 200
        assert edit_activity_display_api.get_resp_code() == 0
        assert edit_activity_display_api.get_resp_message() == 'OK'
        # 刷新缓存
        refresh_cache_api = RefreshActivityDisplayCacheApi()
        refresh_cache_api.get()
        assert refresh_cache_api.get_status_code() == 200
        assert refresh_cache_api.get_resp_code() == 0
        assert refresh_cache_api.get_resp_message() == 'OK'

        # 获取活动展示列表
        get_activity_display_list_api = GetActivityDisplayApi()
        get_activity_display_list_api.get({'state':None})
        assert get_activity_display_list_api.get_status_code() == 200
        assert get_activity_display_list_api.get_resp_code() == 0
        assert get_activity_display_list_api.get_resp_message() == 'OK'
        activity_display_data = get_activity_display_list_api.get_resp_data()
        assert activity_display_data['list'][0]['orderPrice'] == '5000'
        assert activity_display_data['list'][0]['limitCount'] == '5'
        assert activity_display_data['list'][0]['reducePrice'] == '500'
        assert activity_display_data['list'][0]['state'] == 2
        create_time = activity_display_data['list'][0]['createTime']
        timeArray = time.strptime(create_time, "%Y-%m-%d %H:%M:%S")
        create_time_timeStamp = int(time.mktime(timeArray))
        assert int(time.time()) - create_time_timeStamp < 120

        # 验证trade端已登录用户
        query_login_customer_can_use_coupon_api = QueryLoginCustomerCanUseCouponApi()
        query_login_customer_can_use_coupon_api.get()
        assert query_login_customer_can_use_coupon_api.get_status_code() == 200
        assert query_login_customer_can_use_coupon_api.get_resp_code() == 0
        assert query_login_customer_can_use_coupon_api.get_resp_message() == 'OK'
        query_login_customer_can_use_coupon_data = query_login_customer_can_use_coupon_api.get_resp_data()
        assert query_login_customer_can_use_coupon_data['orderPrice'] == None
        assert query_login_customer_can_use_coupon_data['reducePrice'] == None
        assert query_login_customer_can_use_coupon_data['canCompute'] == False
        # 验证trade端未登录用户
        query_can_use_coupon_api = QueryCanUseCouponApi()
        query_can_use_coupon_api.get()
        assert query_can_use_coupon_api.get_status_code() == 200
        assert query_can_use_coupon_api.get_resp_code() == 0
        assert query_can_use_coupon_api.get_resp_message() == 'OK'
        query_can_use_coupon_data = query_can_use_coupon_api.get_resp_data()
        assert query_can_use_coupon_data['orderPrice'] == None
        assert query_can_use_coupon_data['reducePrice'] == None
        assert query_can_use_coupon_data['canCompute'] == False


    def tearDown(self):
        super(ActivityDisplayManagerMonitoring,self).tearDown()
        hooks.delete_activity_display()
        for x in self.activity_list:
            hooks.delete_activity(x['activity_id'], sign_id=x['sign_id'])
        self.activity_list = []
        time.sleep(5)

if __name__ == '__main__':
    api = ActivityDisplayManagerMonitoring()
    api.run_method(monitoring_name='活动展示管理监控',monitoring_class=api,redis_key=ACTIVITY_DISPLAY_MANAGER_MONITORING_KEY)
    # api.setUp()
    # api.activity_display()
    # api.tearDown()