# # -*- coding:utf-8 -*-
# from ApiManager.pf_netcar_monitoring.base_monitoring import BaseMonitoring
# from ApiManager.pf_netcar_api.sheet.activity_manager_api import AddActivityApi, GetActivityListApi, GetActivityDetailApi,CloseActivityApi,DownloadImportTemplateApi,ImportCouponRechargeApi,RechargeRecordInfoApi
# from ApiManager.pf_netcar_api.trade.get_coupon_list_api import GetCouponListApi
# from ApiManager.utils import hooks
# from ApiManager.utils.faker_data import BaseFaker
# from ApiManager.pf_netcar_api.login_api import TradeLoginApi
# from ApiManager.utils.XXL_job import XXLJob
# from ApiManager.utils.redis_helper import ACTIVITY_MANAGER_MONITORING_KEY
# import datetime, time,random
#
#
# class UserCouponListMonitoring(BaseMonitoring):
#     """
#     用户优惠券列表监控
#     """
#     activity_list = []
#
#     def setUp(self):
#         super(UserCouponListMonitoring,self).setUp()
#         # 查询活动状态查询当前生效的活动
#         get_activity_list_api = GetActivityListApi()
#         get_activity_list_api.get({'activityStatus': 1,'activityId':None, 'activityType': None, 'signId': None, 'pageSize': 100,'pageNum': 1})
#         assert get_activity_list_api.get_status_code() == 200
#         assert get_activity_list_api.get_resp_code() == 0
#         assert get_activity_list_api.get_resp_message() == 'OK'
#         activity_list = get_activity_list_api.get_resp_data()['list']
#         if activity_list:
#             for x in activity_list:
#                 # 调用终止活动接口
#                 close_activity_api = CloseActivityApi()
#                 close_activity_api.post({'activityStatus': 2, 'id': x['id']})
#                 assert close_activity_api.get_status_code() == 200
#                 assert close_activity_api.get_resp_code() == 0
#                 assert close_activity_api.get_resp_message() == 'OK'
#             time.sleep(2)
#
#
#     def query_user_coupon(self):
#         """
#         查询用户优惠券
#         :return:
#         """
#         count = 1
#         max_count = 100
#         now_time = datetime.datetime.now()
#         start_time = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
#         end_time = (now_time + datetime.timedelta(hours=+3)).strftime("%Y-%m-%d %H:%M:%S")
#         # 创建通用满减券，无文字说明
#         create_activity_api = AddActivityApi()
#         full_cut_activity_id_one = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
#         create_activity_api.post({"activityObject": 4, "activityStartTime": start_time,
#                                   "activityEndTime": end_time, "activityName": '测试满减券通用',
#                                   "signId": '签报号-测试满减券通用',
#                                   "activityId": full_cut_activity_id_one, "couponExpireTime": 15, "grantTotal": 100,
#                                   "activityFrom": 1, "activityUseType": 1, "activityType": 1,
#                                   "couponDiscount": "",
#                                   "payAmount": 10000, "couponAmount": 5000, "payAmountMin": "", "payAmountMax": "",
#                                   "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
#                                   "activityCycleType": "", "activityCycleTotalTime": "",
#                                   "description": ''})
#         assert create_activity_api.get_status_code() == 200
#         assert create_activity_api.get_resp_code() == 0
#         assert create_activity_api.get_resp_message() == 'OK'
#         self.activity_list.append({'activity_id': full_cut_activity_id_one,'sign_id': '签报号-测试满减券通用'})  # 将该活动信息加入全局变量列表中
#         time.sleep(8)
#
#         # 用户登录
#         login_result = TradeLoginApi().login()
#         new_user_mobile = login_result['mobile']
#         time.sleep(8)
#         # 执行发券job
#         XXLJob().run_job(job_id=9,sheet_job=False)
#         time.sleep(8)
#         # trade端验证发券
#         while count < max_count:
#             get_coupon_list_api = GetCouponListApi(mobile=new_user_mobile)
#             get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
#             assert get_coupon_list_api.get_status_code() == 200
#             assert get_coupon_list_api.get_resp_code() == 0
#             assert get_coupon_list_api.get_resp_message() == 'OK'
#             coupon_list_data = get_coupon_list_api.get_resp_data()
#             if len(coupon_list_data['list']) == 0:
#                 time.sleep(5)
#                 count += 1
#             else:
#                 assert len(coupon_list_data['list']) == 1
#                 assert coupon_list_data['list'][0]['activityUseType'] == 1
#                 assert coupon_list_data['list'][0]['couponType'] == 1
#                 assert coupon_list_data['list'][0]['couponName'] == '测试满减券通用'
#                 assert coupon_list_data['list'][0]['payAmount'] == 10000
#                 assert coupon_list_data['list'][0]['couponState'] == '1'
#                 assert coupon_list_data['list'][0]['couponAmount'] == 5000
#                 assert coupon_list_data['list'][0]['couponDiscount'] == 0
#                 assert coupon_list_data['list'][0]['maxCouponAmount'] == 5000
#                 assert coupon_list_data['list'][0]['description'] == ''
#                 coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
#                 timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
#                 coupon_start_time_timeStamp = int(time.mktime(timeArray))
#                 assert int(time.time()) - coupon_start_time_timeStamp < 120
#                 assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+15)).strftime("%Y-%m-%d 23:59")
#                 break
#         assert count < max_count
#
#         # 创建专车满减券，有文字说明
#         create_activity_api = AddActivityApi()
#         description = BaseFaker().create_sentence()  # 随机生成一段文字
#         full_cut_activity_id_two = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
#         create_activity_api.post({"activityObject": 4, "activityStartTime": start_time,
#                                   "activityEndTime": end_time, "activityName": '测试满减券专车',
#                                   "signId": '签报号-测试满减券专车',
#                                   "activityId": full_cut_activity_id_two, "couponExpireTime": 15, "grantTotal": 100,
#                                   "activityFrom": 1, "activityUseType": 2, "activityType": 1,
#                                   "couponDiscount": "",
#                                   "payAmount": 10000, "couponAmount": 5000, "payAmountMin": "", "payAmountMax": "",
#                                   "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
#                                   "activityCycleType": "", "activityCycleTotalTime": "",
#                                   "description": description})
#         assert create_activity_api.get_status_code() == 200
#         assert create_activity_api.get_resp_code() == 0
#         assert create_activity_api.get_resp_message() == 'OK'
#         self.activity_list.append({'activity_id': full_cut_activity_id_two,'sign_id': '签报号-测试满减券专车'})  # 将该活动信息加入全局变量列表中
#         time.sleep(8)
#         # 执行发券job
#         XXLJob().run_job(job_id=9,sheet_job=False)
#         time.sleep(8)
#         # trade端验证发券
#         while count < max_count:
#             get_coupon_list_api = GetCouponListApi(mobile=new_user_mobile)
#             get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
#             assert get_coupon_list_api.get_status_code() == 200
#             assert get_coupon_list_api.get_resp_code() == 0
#             assert get_coupon_list_api.get_resp_message() == 'OK'
#             coupon_list_data = get_coupon_list_api.get_resp_data()
#             if len(coupon_list_data['list']) == 1:
#                 time.sleep(5)
#                 count += 1
#             else:
#                 assert len(coupon_list_data['list']) == 2
#                 assert coupon_list_data['list'][0]['activityUseType'] == 1
#                 assert coupon_list_data['list'][0]['couponType'] == 1
#                 assert coupon_list_data['list'][0]['couponName'] == '测试满减券专车'
#                 assert coupon_list_data['list'][0]['payAmount'] == 10000
#                 assert coupon_list_data['list'][0]['couponState'] == '1'
#                 assert coupon_list_data['list'][0]['couponAmount'] == 5000
#                 assert coupon_list_data['list'][0]['couponDiscount'] == 0
#                 assert coupon_list_data['list'][0]['maxCouponAmount'] == 5000
#                 assert coupon_list_data['list'][0]['description'] == description
#                 coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
#                 timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
#                 coupon_start_time_timeStamp = int(time.mktime(timeArray))
#                 assert int(time.time()) - coupon_start_time_timeStamp < 120
#                 assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+15)).strftime("%Y-%m-%d 23:59")
#                 break
#         assert count < max_count
#
#         # # 创建接送机满减券，无文字说明
#         # create_activity_api = AddActivityApi()
#         # full_cut_activity_id_three = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
#         # create_activity_api.post({"activityObject": 4, "activityStartTime": start_time,
#         #                           "activityEndTime": end_time, "activityName": '测试满减券接送机',
#         #                           "signId": '签报号-测试满减券接送机',
#         #                           "activityId": full_cut_activity_id_three, "couponExpireTime": 15, "grantTotal": 100,
#         #                           "activityFrom": 1, "activityUseType": 3, "activityType": 1,
#         #                           "couponDiscount": "",
#         #                           "payAmount": 10000, "couponAmount": 5000, "payAmountMin": "", "payAmountMax": "",
#         #                           "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
#         #                           "activityCycleType": "", "activityCycleTotalTime": "",
#         #                           "description": ''})
#         # assert create_activity_api.get_status_code() == 200
#         # assert create_activity_api.get_resp_code() == 0
#         # assert create_activity_api.get_resp_message() == 'OK'
#         # self.activity_list.append({'activity_id': full_cut_activity_id_three,'sign_id': '签报号-测试满减券接送机'})  # 将该活动信息加入全局变量列表中
#         #
#         # # 创建通用折扣券，无文字说明
#         # create_activity_api = AddActivityApi()
#         # discount_activity_id_one = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
#         # create_activity_api.post({"activityObject": 4, "activityStartTime": start_time,
#         #                           "activityEndTime": end_time, "activityName": '测试折扣券通用',
#         #                           "signId": '签报号-测试折扣券通用',
#         #                           "activityId": discount_activity_id_one, "couponExpireTime": 15, "grantTotal": 100,
#         #                           "activityFrom": 1, "activityUseType": 1, "activityType": 2,
#         #                           "couponDiscount": "0.8",
#         #                           "payAmount": 10000, "couponAmount": 8000, "payAmountMin": "", "payAmountMax": "",
#         #                           "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
#         #                           "activityCycleType": "", "activityCycleTotalTime": "",
#         #                           "description": ''})
#         # assert create_activity_api.get_status_code() == 200
#         # assert create_activity_api.get_resp_code() == 0
#         # assert create_activity_api.get_resp_message() == 'OK'
#         # self.activity_list.append({'activity_id': discount_activity_id_one, 'sign_id': '签报号-测试折扣券通用'})  # 将该活动信息加入全局变量列表中
#         #
#         # # 创建专车折扣券，包含文字说明
#         # create_activity_api = AddActivityApi()
#         # description = BaseFaker().create_sentence()  # 随机生成一段文字
#         # discount_activity_id_one = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
#         # create_activity_api.post({"activityObject": 4, "activityStartTime": start_time,
#         #                           "activityEndTime": end_time, "activityName": '测试折扣券专车',
#         #                           "signId": '签报号-测试折扣券专车',
#         #                           "activityId": discount_activity_id_one, "couponExpireTime": 15, "grantTotal": 100,
#         #                           "activityFrom": 1, "activityUseType": 2, "activityType": 2,
#         #                           "couponDiscount": "0.8",
#         #                           "payAmount": 10000, "couponAmount": 8000, "payAmountMin": "", "payAmountMax": "",
#         #                           "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
#         #                           "activityCycleType": "", "activityCycleTotalTime": "",
#         #                           "description": description})
#         # assert create_activity_api.get_status_code() == 200
#         # assert create_activity_api.get_resp_code() == 0
#         # assert create_activity_api.get_resp_message() == 'OK'
#         # self.activity_list.append({'activity_id': discount_activity_id_one, 'sign_id': '签报号-测试折扣券专车'})  # 将该活动信息加入全局变量列表中
#         #
#         # # 创建接送机折扣券，无文字说明
#         # create_activity_api = AddActivityApi()
#         # discount_activity_id_one = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
#         # create_activity_api.post({"activityObject": 4, "activityStartTime": start_time,
#         #                           "activityEndTime": end_time, "activityName": '测试折扣券接送机',
#         #                           "signId": '签报号-测试折扣券接送机',
#         #                           "activityId": discount_activity_id_one, "couponExpireTime": 15, "grantTotal": 100,
#         #                           "activityFrom": 1, "activityUseType": 3, "activityType": 2,
#         #                           "couponDiscount": "0.8",
#         #                           "payAmount": 10000, "couponAmount": 8000, "payAmountMin": "", "payAmountMax": "",
#         #                           "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
#         #                           "activityCycleType": "", "activityCycleTotalTime": "",
#         #                           "description": ''})
#         # assert create_activity_api.get_status_code() == 200
#         # assert create_activity_api.get_resp_code() == 0
#         # assert create_activity_api.get_resp_message() == 'OK'
#         # self.activity_list.append({'activity_id': discount_activity_id_one, 'sign_id': '签报号-测试折扣券接送机'})  # 将该活动信息加入全局变量列表中
#         #
#         # # 根据活动状态查询验证生效活动个数
#         # get_activity_list_api = GetActivityListApi()
#         # get_activity_list_api.get({'activityStatus': 1,'activityId': None, 'activityType': None, 'signId': None,'pageSize': None, 'pageNum': None})
#         # assert get_activity_list_api.get_status_code() == 200
#         # assert get_activity_list_api.get_resp_code() == 0
#         # assert get_activity_list_api.get_resp_message() == 'OK'
#         # activity_list = get_activity_list_api.get_resp_data()['list']
#         # assert len(activity_list) == 6
#         #
#
#
#
#
#
#
#
#     def tearDown(self):
#         super(UserCouponListMonitoring, self).tearDown()
#         for x in self.activity_list:
#             hooks.delete_activity(x['activity_id'], sign_id=x['sign_id'])
#         self.activity_list = []
#
#
#
# if __name__ == '__main__':
#     api = UserCouponListMonitoring()
#     api.setUp()
#     api.query_user_coupon()
#     api.tearDown()
#
#
#
#
#
#
#
#
#
