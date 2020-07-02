# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_monitoring.base_monitoring import BaseMonitoring
from ApiManager.pf_netcar_api.sheet.activity_manager_api import AddActivityApi, GetActivityListApi, GetActivityDetailApi,CloseActivityApi,DownloadImportTemplateApi,ImportCouponRechargeApi,RechargeRecordInfoApi
from ApiManager.pf_netcar_api.trade.get_coupon_list_api import GetCouponListApi
from ApiManager.utils import hooks
from ApiManager.utils.faker_data import BaseFaker
from ApiManager.pf_netcar_api.login_api import TradeLoginApi
from ApiManager.utils.redis_helper import ACTIVITY_MANAGER_MONITORING_KEY
import datetime, time,random


class ActivityManagerMonitoring(BaseMonitoring):
    """
    活动管理监控
    """
    activity_list = []


    def create_activity_full_cut(self):
        """
        测试创建新满减券
        :return:
        """
        now_time = datetime.datetime.now()
        start_time = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S")
        def create_full_cut_activity(name, activity_object, activity_from, use_type,sign_id=None):
            """
            创建满减券活动
            :param name:活动名称
            :param sign_id:签报号
            :param activity_object:适用类型
            :param activity_from:活动来源
            :param use_type:活动使用类型
            :return:
            """
            if not sign_id:
                sign_id_text = '《签报号》001abc' + str(int(time.time())) + str(random.randint(100,999))
            else:
                sign_id_text = sign_id
            # 正常创建满减券
            create_activity_api = AddActivityApi()
            description = BaseFaker().create_sentence()  # 随机生成一段文字
            activity_id = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
            create_activity_api.post({"activityObject": activity_object, "activityStartTime": start_time,
                                      "activityEndTime": end_time, "activityName": name,
                                      "signId": sign_id_text,
                                      "activityId": activity_id, "couponExpireTime": 15, "grantTotal": 100,
                                      "activityFrom": activity_from, "activityUseType": use_type, "activityType": 1,
                                      "couponDiscount": "",
                                      "payAmount": 10000, "couponAmount": 5000, "payAmountMin": "", "payAmountMax": "",
                                      "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
                                      "activityCycleType": "", "activityCycleTotalTime": "",
                                      "description": description})
            assert create_activity_api.get_status_code() == 200
            assert create_activity_api.get_resp_code() == 0
            assert create_activity_api.get_resp_message() == 'OK'
            time.sleep(0.5)

            activity_from_desc = None
            if activity_from == 1:
                activity_from_desc = '银行活动发放'
            elif activity_from == 2:
                activity_from_desc = '用户购买'
            elif activity_from == 3:
                activity_from_desc = '管理员发放'
            elif activity_from == 4:
                activity_from_desc = '投诉处理'
            elif activity_from == 9:
                activity_from_desc = '其他'
            elif activity_from == 5:
                activity_from_desc = '红包充值'

            activity_object_desc = None
            if activity_object == 1:
                activity_object_desc = '新用户 平台首单'
            elif activity_object == 2:
                activity_object_desc = '成功交易用户'
            elif activity_object == 3:
                activity_object_desc = '本行卡交易用户'
            elif activity_object == 4:
                activity_object_desc = '登录用户'
            elif activity_object == 5:
                activity_object_desc = '批量充值'

            use_type_desc = None
            if use_type == 1:
                use_type_desc = '通用'
            elif use_type == 2:
                use_type_desc = '专车'
            elif use_type == 3:
                use_type_desc = '接送机'
            self.activity_list.append({'activity_id': activity_id, 'activity_name': name,
                                       'activity_object': activity_object_desc, 'activity_object_id': activity_object,
                                       'activity_from_id': activity_from, 'activity_from': activity_from_desc,
                                       'use_type': use_type_desc, 'use_type_id': use_type,
                                       'sign_id': sign_id_text,'desc':description})  # 将该活动信息加入全局变量列表中

        # 正常创建满减券，适用类型：新用户首单，活动来源：银行活动发放，活动使用类型：通用
        create_full_cut_activity(name='测试满减券首单银行发放通用', activity_object=1, activity_from=1, use_type=1)
        # 正常创建满减券，适用类型：新用户首单，活动来源：银行活动发放，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券首单银行发放接送机', activity_object=1, activity_from=1, use_type=3)
        # 正常创建满减券，适用类型：新用户首单，活动来源：银行活动发放，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券首单银行发放实时单', activity_object=1, activity_from=1, use_type=2)
        # 正常创建满减券，适用类型：新用户首单，活动来源：用户购买，活动使用类型：通用
        create_full_cut_activity(name='测试满减券首单用户购买通用', activity_object=1, activity_from=2, use_type=1)
        # 正常创建满减券，适用类型：新用户首单，活动来源：用户购买，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券首单用户购买接送机', activity_object=1, activity_from=2, use_type=3)
        # 正常创建满减券，适用类型：新用户首单，活动来源：用户购买，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券首单用户购买实时单', activity_object=1, activity_from=2, use_type=2)
        # 正常创建满减券，适用类型：新用户首单，活动来源：管理员发放，活动使用类型：通用
        create_full_cut_activity(name='测试满减券首单管理员发放通用', activity_object=1, activity_from=3, use_type=1)
        # 正常创建满减券，适用类型：新用户首单，活动来源：管理员发放，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券首单管理员发放接送机', activity_object=1, activity_from=3, use_type=3)
        # 正常创建满减券，适用类型：新用户首单，活动来源：管理员发放，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券首单管理员发放实时单', activity_object=1, activity_from=3, use_type=2)
        # 正常创建满减券，适用类型：新用户首单，活动来源：投诉处理，活动使用类型：通用
        create_full_cut_activity(name='测试满减券首单投诉处理通用', activity_object=1, activity_from=4, use_type=1)
        # 正常创建满减券，适用类型：新用户首单，活动来源：投诉处理，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券首单投诉处理接送机', activity_object=1, activity_from=4, use_type=3)
        # 正常创建满减券，适用类型：新用户首单，活动来源：投诉处理，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券首单投诉处理实时单', activity_object=1, activity_from=4, use_type=2)
        # 正常创建满减券，适用类型：新用户首单，活动来源：其他，活动使用类型：通用
        create_full_cut_activity(name='测试满减券首单其他通用', activity_object=1, activity_from=9, use_type=1)
        # 正常创建满减券，适用类型：新用户首单，活动来源：其他，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券首单其他接送机', activity_object=1, activity_from=9, use_type=3)
        # 正常创建满减券，适用类型：新用户首单，活动来源：其他，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券首单其他实时单', activity_object=1, activity_from=9, use_type=2)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：银行活动发放，活动使用类型：通用
        create_full_cut_activity(name='测试满减券成功交易银行发放通用', activity_object=2, activity_from=1, use_type=1)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：银行活动发放，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券成功交易银行发放接送机', activity_object=2, activity_from=1, use_type=3)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：银行活动发放，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券成功交易银行发放实时单', activity_object=2, activity_from=1, use_type=2)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：用户购买，活动使用类型：通用
        create_full_cut_activity(name='测试满减券成功交易用户购买通用', activity_object=2, activity_from=2, use_type=1)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：用户购买，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券成功交易用户购买接送机', activity_object=2, activity_from=2, use_type=3)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：用户购买，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券成功交易用户购买实时单', activity_object=2, activity_from=2, use_type=2)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：管理员发放，活动使用类型：通用
        create_full_cut_activity(name='测试满减券成功交易管理员发放通用', activity_object=2, activity_from=3, use_type=1)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：管理员发放，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券成功交易管理员发放接送机', activity_object=2, activity_from=3, use_type=3)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：管理员发放，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券成功交易管理员发放实时单', activity_object=2, activity_from=3, use_type=2)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：投诉处理，活动使用类型：通用
        create_full_cut_activity(name='测试满减券成功交易投诉处理通用', activity_object=2, activity_from=4, use_type=1)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：投诉处理，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券成功交易投诉处理接送机', activity_object=2, activity_from=4, use_type=3)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：投诉处理，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券成功交易投诉处理实时单', activity_object=2, activity_from=4, use_type=2)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：其他，活动使用类型：通用
        create_full_cut_activity(name='测试满减券成功交易其他通用', activity_object=2, activity_from=9, use_type=1)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：其他，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券成功交易其他接送机', activity_object=2, activity_from=9, use_type=3)
        # 正常创建满减券，适用类型：成功交易用户，活动来源：其他，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券成功交易其他实时单', activity_object=2, activity_from=9, use_type=2)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：银行活动发放，活动使用类型：通用
        create_full_cut_activity(name='测试满减券本行卡交易银行发放通用', activity_object=3, activity_from=1, use_type=1)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：银行活动发放，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券本行卡交易银行发放接送机', activity_object=3, activity_from=1, use_type=3)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：银行活动发放，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券本行卡交易银行发放实时单', activity_object=3, activity_from=1, use_type=2)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：用户购买，活动使用类型：通用
        create_full_cut_activity(name='测试满减券本行卡交易用户购买通用', activity_object=3, activity_from=2, use_type=1)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：用户购买，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券本行卡交易用户购买接送机', activity_object=3, activity_from=2, use_type=3)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：用户购买，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券本行卡交易用户购买实时单', activity_object=3, activity_from=2, use_type=2)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：管理员发放，活动使用类型：通用
        create_full_cut_activity(name='测试满减券本行卡交易管理员发放通用', activity_object=3, activity_from=3, use_type=1)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：管理员发放，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券本行卡交易管理员发放接送机', activity_object=3, activity_from=3, use_type=3)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：管理员发放，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券本行卡交易管理员发放实时单', activity_object=3, activity_from=3, use_type=2)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：投诉处理，活动使用类型：通用
        create_full_cut_activity(name='测试满减券本行卡交易投诉处理通用', activity_object=3, activity_from=4, use_type=1)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：投诉处理，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券本行卡交易投诉处理接送机', activity_object=3, activity_from=4, use_type=3)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：投诉处理，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券本行卡交易投诉处理实时单', activity_object=3, activity_from=4, use_type=2)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：其他，活动使用类型：通用
        create_full_cut_activity(name='测试满减券本行卡交易其他通用', activity_object=3, activity_from=9, use_type=1)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：其他，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券本行卡交易其他接送机', activity_object=3, activity_from=9, use_type=3)
        # 正常创建满减券，适用类型：本行卡交易，活动来源：其他，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券本行卡交易其他实时单', activity_object=3, activity_from=9, use_type=2)
        # 正常创建满减券，适用类型：登录用户，活动来源：银行活动发放，活动使用类型：通用
        create_full_cut_activity(name='测试满减券登录用户银行发放通用', activity_object=4, activity_from=1, use_type=1)
        # 正常创建满减券，适用类型：登录用户，活动来源：银行活动发放，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券登录用户银行发放接送机', activity_object=4, activity_from=1, use_type=3)
        # 正常创建满减券，适用类型：登录用户，活动来源：银行活动发放，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券登录用户银行发放实时单', activity_object=4, activity_from=1, use_type=2)
        # 正常创建满减券，适用类型：登录用户，活动来源：用户购买，活动使用类型：通用
        create_full_cut_activity(name='测试满减券登录用户用户购买通用', activity_object=4, activity_from=2, use_type=1)
        # 正常创建满减券，适用类型：登录用户，活动来源：用户购买，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券登录用户用户购买接送机', activity_object=4, activity_from=2, use_type=3)
        # 正常创建满减券，适用类型：登录用户，活动来源：用户购买，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券登录用户用户购买实时单', activity_object=4, activity_from=2, use_type=2)
        # 正常创建满减券，适用类型：登录用户，活动来源：管理员发放，活动使用类型：通用
        create_full_cut_activity(name='测试满减券登录用户管理员发放通用', activity_object=4, activity_from=3, use_type=1)
        # 正常创建满减券，适用类型：登录用户，活动来源：管理员发放，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券登录用户管理员发放接送机', activity_object=4, activity_from=3, use_type=3)
        # 正常创建满减券，适用类型：登录用户，活动来源：管理员发放，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券登录用户管理员发放实时单', activity_object=4, activity_from=3, use_type=2)
        # 正常创建满减券，适用类型：登录用户，活动来源：投诉处理，活动使用类型：通用
        create_full_cut_activity(name='测试满减券登录用户投诉处理通用', activity_object=4, activity_from=4, use_type=1)
        # 正常创建满减券，适用类型：登录用户，活动来源：投诉处理，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券登录用户投诉处理接送机', activity_object=4, activity_from=4, use_type=3)
        # 正常创建满减券，适用类型：登录用户，活动来源：投诉处理，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券登录用户投诉处理实时单', activity_object=4, activity_from=4, use_type=2)
        # 正常创建满减券，适用类型：登录用户，活动来源：其他，活动使用类型：通用
        create_full_cut_activity(name='测试满减券登录用户其他通用', activity_object=4, activity_from=9, use_type=1)
        # 正常创建满减券，适用类型：登录用户，活动来源：其他，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券登录用户其他接送机', activity_object=4, activity_from=9, use_type=3)
        # 正常创建满减券，适用类型：登录用户，活动来源：其他，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券登录用户其他实时单', activity_object=4, activity_from=9, use_type=2)
        # 正常创建满减券，适用类型：批量充值，活动来源：银行活动发放，活动使用类型：通用
        create_full_cut_activity(name='测试满减券批量充值银行发放通用', activity_object=5, activity_from=1, use_type=1)
        # 正常创建满减券，适用类型：批量充值，活动来源：银行活动发放，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券批量充值银行发放接送机', activity_object=5, activity_from=1, use_type=3)
        # 正常创建满减券，适用类型：批量充值，活动来源：银行活动发放，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券批量充值银行发放实时单', activity_object=5, activity_from=1, use_type=2)
        # 正常创建满减券，适用类型：批量充值，活动来源：用户购买，活动使用类型：通用
        create_full_cut_activity(name='测试满减券批量充值用户购买通用', activity_object=5, activity_from=2, use_type=1)
        # 正常创建满减券，适用类型：批量充值，活动来源：用户购买，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券批量充值用户购买接送机', activity_object=5, activity_from=2, use_type=3)
        # 正常创建满减券，适用类型：批量充值，活动来源：用户购买，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券批量充值用户购买实时单', activity_object=5, activity_from=2, use_type=2)
        # 正常创建满减券，适用类型：批量充值，活动来源：管理员发放，活动使用类型：通用
        create_full_cut_activity(name='测试满减券批量充值管理员发放通用', activity_object=5, activity_from=3, use_type=1)
        # 正常创建满减券，适用类型：批量充值，活动来源：管理员发放，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券批量充值管理员发放接送机', activity_object=5, activity_from=3, use_type=3)
        # 正常创建满减券，适用类型：批量充值，活动来源：管理员发放，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券批量充值管理员发放实时单', activity_object=5, activity_from=3, use_type=2)
        # 正常创建满减券，适用类型：批量充值，活动来源：投诉处理，活动使用类型：通用
        create_full_cut_activity(name='测试满减券批量充值投诉处理通用', activity_object=5, activity_from=4, use_type=1)
        # 正常创建满减券，适用类型：批量充值，活动来源：投诉处理，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券批量充值投诉处理接送机', activity_object=5, activity_from=4, use_type=3)
        # 正常创建满减券，适用类型：批量充值，活动来源：投诉处理，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券批量充值投诉处理实时单', activity_object=5, activity_from=4, use_type=2)
        # 正常创建满减券，适用类型：批量充值，活动来源：其他，活动使用类型：通用
        create_full_cut_activity(name='测试满减券批量充值其他通用', activity_object=5, activity_from=9, use_type=1)
        # 正常创建满减券，适用类型：批量充值，活动来源：其他，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券批量充值其他接送机', activity_object=5, activity_from=9, use_type=3)
        # 正常创建满减券，适用类型：批量充值，活动来源：其他，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券批量充值其他实时单', activity_object=5, activity_from=9, use_type=2)
        # 正常创建满减券，适用类型：批量充值，活动来源：红包充值，活动使用类型：通用
        create_full_cut_activity(name='测试满减券批量充值红包充值通用', activity_object=5, activity_from=5, use_type=1)
        # 正常创建满减券，适用类型：批量充值，活动来源：红包充值，活动使用类型：接送机
        create_full_cut_activity(name='测试满减券批量充值红包充值接送机', activity_object=5, activity_from=5, use_type=3)
        # 正常创建满减券，适用类型：批量充值，活动来源：红包充值，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券批量充值红包充值实时单', activity_object=5, activity_from=5, use_type=2)

        # 创建满减券相同签报号不同来源，适用类型：批量充值，活动来源：红包充值，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券批量充值红包充值实时单', activity_object=5, activity_from=5, use_type=2,sign_id='满减券相同签报号不同来源')
        # 创建满减券相同签报号不同来源，适用类型：批量充值，活动来源：银行获得发放，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券批量充值红包充值实时单', activity_object=5, activity_from=1, use_type=2,sign_id='满减券相同签报号不同来源')
        # 创建满减券相同签报号不同来源，适用类型：批量充值，活动来源：用户购买，活动使用类型：实时单
        create_full_cut_activity(name='测试满减券批量充值红包充值实时单', activity_object=5, activity_from=2, use_type=2,sign_id='满减券相同签报号不同来源')
        # 查询活动列表
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 0,  # 查询全部状态
                                   'activityId': None, 'activityType': None, 'signId': None, 'pageSize': 100,
                                   'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        self.activity_list.reverse()
        for i in range(len(self.activity_list)):
            assert self.activity_list[i]['activity_id'] == activity_list[i]['activityId']
            assert self.activity_list[i]['activity_name'] == activity_list[i]['activityName']
            assert self.activity_list[i]['activity_object'] == activity_list[i]['activityObjectDesc']
            assert self.activity_list[i]['activity_object_id'] == activity_list[i]['activityObject']
            assert self.activity_list[i]['activity_from'] == activity_list[i]['activityFromDesc']
            assert self.activity_list[i]['activity_from_id'] == activity_list[i]['activityFrom']
            assert self.activity_list[i]['use_type'] == activity_list[i]['activityUseTypeDesc']
            assert self.activity_list[i]['use_type_id'] == activity_list[i]['activityUseType']
            assert activity_list[i]['expireTime'] == 15
            assert activity_list[i]['grantTotal'] == 100
            assert activity_list[i]['signId'] == self.activity_list[i]['sign_id']
            assert activity_list[i]['activityStartTime'] == start_time
            assert activity_list[i]['activityEndTime'] == end_time
            assert activity_list[i]['activityStatus'] == 1
            assert activity_list[i]['activityStatusDesc'] == '生效'
            assert activity_list[i]['activityType'] == 1
            assert activity_list[i]['activityTypeDesc'] == '满减券'
            self.activity_list[i].update({"id":activity_list[i]['id']})

        # 查询活动详情
        for x in self.activity_list:
            get_activity_detail_api = GetActivityDetailApi()
            get_activity_detail_api.get({'activityId': x['id']})
            assert get_activity_detail_api.get_status_code() == 200
            assert get_activity_detail_api.get_resp_code() == 0
            assert get_activity_detail_api.get_resp_message() == 'OK'
            activity_detail_data = get_activity_detail_api.get_resp_data()
            assert activity_detail_data['activityCycleTotalTime'] == ''
            assert activity_detail_data['activityCycleType'] == ''
            assert activity_detail_data['activityId'] == x['activity_id']
            assert activity_detail_data['activityName'] == x['activity_name']
            assert activity_detail_data['activityPeopleCount'] == ''
            assert activity_detail_data['activityUseType'] == x['use_type_id']
            assert activity_detail_data['activityUseTypeDesc'] == x['use_type']
            assert activity_detail_data['couponAmount'] == '5000'
            assert activity_detail_data['couponDiscount'] == ''
            assert activity_detail_data['description'] == x['desc']
            assert activity_detail_data['discountAmountMax'] == ''
            assert activity_detail_data['discountAmountMin'] == ''
            assert activity_detail_data['payAmount'] == '10000'
            assert activity_detail_data['payAmountMax'] == ''
            assert activity_detail_data['payAmountMin'] == ''


    def create_activity_discount(self):
        """
        测试创建折扣券
        :return:
        """
        now_time = datetime.datetime.now()
        start_time = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S")
        def create_discount_activity(name, activity_object, activity_from, use_type,sign_id=None):
            """
            创建折扣券活动
            :param name:活动名称
            :param sign_id:签报号
            :param activity_object:适用类型
            :param activity_from:活动来源
            :param use_type:活动使用类型
            :return:
            """
            if not sign_id:
                sign_id_text = '《签报号》001abc' + str(int(time.time())) + str(random.randint(100, 999))
            else:
                sign_id_text = sign_id
            # 正常创建折扣券
            create_activity_api = AddActivityApi()
            description = BaseFaker().create_sentence()  # 随机生成一段文字
            activity_id = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
            create_activity_api.post({"activityObject": activity_object, "activityStartTime": start_time,
                                      "activityEndTime": end_time, "activityName": name,
                                      "signId": sign_id_text,
                                      "activityId": activity_id, "couponExpireTime": 15, "grantTotal": 100,
                                      "activityFrom": activity_from, "activityUseType": use_type, "activityType": 2,
                                      "couponDiscount": "0.8",
                                      "payAmount": 10000, "couponAmount": 5000, "payAmountMin": "", "payAmountMax": "",
                                      "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
                                      "activityCycleType": "", "activityCycleTotalTime": "",
                                      "description": description})
            assert create_activity_api.get_status_code() == 200
            assert create_activity_api.get_resp_code() == 0
            assert create_activity_api.get_resp_message() == 'OK'
            time.sleep(0.5)
            activity_from_desc = None
            if activity_from == 1:
                activity_from_desc = '银行活动发放'
            elif activity_from == 2:
                activity_from_desc = '用户购买'
            elif activity_from == 3:
                activity_from_desc = '管理员发放'
            elif activity_from == 4:
                activity_from_desc = '投诉处理'
            elif activity_from == 9:
                activity_from_desc = '其他'
            elif activity_from == 5:
                activity_from_desc = '红包充值'

            activity_object_desc = None
            if activity_object == 1:
                activity_object_desc = '新用户 平台首单'
            elif activity_object == 2:
                activity_object_desc = '成功交易用户'
            elif activity_object == 3:
                activity_object_desc = '本行卡交易用户'
            elif activity_object == 4:
                activity_object_desc = '登录用户'
            elif activity_object == 5:
                activity_object_desc = '批量充值'

            use_type_desc = None
            if use_type == 1:
                use_type_desc = '通用'
            elif use_type == 2:
                use_type_desc = '专车'
            elif use_type == 3:
                use_type_desc = '接送机'
            self.activity_list.append({'activity_id': activity_id, 'activity_name': name,
                                       'activity_object': activity_object_desc, 'activity_object_id': activity_object,
                                       'activity_from_id': activity_from, 'activity_from': activity_from_desc,
                                       'use_type': use_type_desc, 'use_type_id': use_type,
                                       'sign_id': sign_id_text,'desc':description})  # 将该活动信息加入全局变量列表中

        # 正常创建折扣券，适用类型：新用户首单，活动来源：银行活动发放，活动使用类型：通用
        create_discount_activity(name='测试折扣券首单银行发放通用', activity_object=1, activity_from=1, use_type=1)
        # 正常创建折扣券，适用类型：新用户首单，活动来源：银行活动发放，活动使用类型：接送机
        create_discount_activity(name='测试折扣券首单银行发放接送机', activity_object=1, activity_from=1, use_type=3)
        # 正常创建折扣券，适用类型：新用户首单，活动来源：银行活动发放，活动使用类型：实时单
        create_discount_activity(name='测试折扣券首单银行发放实时单', activity_object=1, activity_from=1, use_type=2)
        # 正常创建折扣券，适用类型：新用户首单，活动来源：用户购买，活动使用类型：通用
        create_discount_activity(name='测试折扣券首单用户购买通用', activity_object=1, activity_from=2, use_type=1)
        # 正常创建折扣券，适用类型：新用户首单，活动来源：用户购买，活动使用类型：接送机
        create_discount_activity(name='测试折扣券首单用户购买接送机', activity_object=1, activity_from=2, use_type=3)
        # 正常创建折扣券，适用类型：新用户首单，活动来源：用户购买，活动使用类型：实时单
        create_discount_activity(name='测试折扣券首单用户购买实时单', activity_object=1, activity_from=2, use_type=2)
        # 正常创建折扣券，适用类型：新用户首单，活动来源：管理员发放，活动使用类型：通用
        create_discount_activity(name='测试折扣券首单管理员发放通用', activity_object=1, activity_from=3, use_type=1)
        # 正常创建折扣券，适用类型：新用户首单，活动来源：管理员发放，活动使用类型：接送机
        create_discount_activity(name='测试折扣券首单管理员发放接送机', activity_object=1, activity_from=3, use_type=3)
        # 正常创建折扣券，适用类型：新用户首单，活动来源：管理员发放，活动使用类型：实时单
        create_discount_activity(name='测试折扣券首单管理员发放实时单', activity_object=1, activity_from=3, use_type=2)
        # 正常创建折扣券，适用类型：新用户首单，活动来源：投诉处理，活动使用类型：通用
        create_discount_activity(name='测试折扣券首单投诉处理通用', activity_object=1, activity_from=4, use_type=1)
        # 正常创建折扣券，适用类型：新用户首单，活动来源：投诉处理，活动使用类型：接送机
        create_discount_activity(name='测试折扣券首单投诉处理接送机', activity_object=1, activity_from=4, use_type=3)
        # 正常创建折扣券，适用类型：新用户首单，活动来源：投诉处理，活动使用类型：实时单
        create_discount_activity(name='测试折扣券首单投诉处理实时单', activity_object=1, activity_from=4, use_type=2)
        # 正常创建折扣券，适用类型：新用户首单，活动来源：其他，活动使用类型：通用
        create_discount_activity(name='测试折扣券首单其他通用', activity_object=1, activity_from=9, use_type=1)
        # 正常创建折扣券，适用类型：新用户首单，活动来源：其他，活动使用类型：接送机
        create_discount_activity(name='测试折扣券首单其他接送机', activity_object=1, activity_from=9, use_type=3)
        # 正常创建折扣券，适用类型：新用户首单，活动来源：其他，活动使用类型：实时单
        create_discount_activity(name='测试折扣券首单其他实时单', activity_object=1, activity_from=9, use_type=2)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：银行活动发放，活动使用类型：通用
        create_discount_activity(name='测试折扣券成功交易银行发放通用', activity_object=2, activity_from=1, use_type=1)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：银行活动发放，活动使用类型：接送机
        create_discount_activity(name='测试折扣券成功交易银行发放接送机', activity_object=2, activity_from=1, use_type=3)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：银行活动发放，活动使用类型：实时单
        create_discount_activity(name='测试折扣券成功交易银行发放实时单', activity_object=2, activity_from=1, use_type=2)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：用户购买，活动使用类型：通用
        create_discount_activity(name='测试折扣券成功交易用户购买通用', activity_object=2, activity_from=2, use_type=1)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：用户购买，活动使用类型：接送机
        create_discount_activity(name='测试折扣券成功交易用户购买接送机', activity_object=2, activity_from=2, use_type=3)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：用户购买，活动使用类型：实时单
        create_discount_activity(name='测试折扣券成功交易用户购买实时单', activity_object=2, activity_from=2, use_type=2)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：管理员发放，活动使用类型：通用
        create_discount_activity(name='测试折扣券成功交易管理员发放通用', activity_object=2, activity_from=3, use_type=1)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：管理员发放，活动使用类型：接送机
        create_discount_activity(name='测试折扣券成功交易管理员发放接送机', activity_object=2, activity_from=3, use_type=3)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：管理员发放，活动使用类型：实时单
        create_discount_activity(name='测试折扣券成功交易管理员发放实时单', activity_object=2, activity_from=3, use_type=2)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：投诉处理，活动使用类型：通用
        create_discount_activity(name='测试折扣券成功交易投诉处理通用', activity_object=2, activity_from=4, use_type=1)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：投诉处理，活动使用类型：接送机
        create_discount_activity(name='测试折扣券成功交易投诉处理接送机', activity_object=2, activity_from=4, use_type=3)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：投诉处理，活动使用类型：实时单
        create_discount_activity(name='测试折扣券成功交易投诉处理实时单', activity_object=2, activity_from=4, use_type=2)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：其他，活动使用类型：通用
        create_discount_activity(name='测试折扣券成功交易其他通用', activity_object=2, activity_from=9, use_type=1)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：其他，活动使用类型：接送机
        create_discount_activity(name='测试折扣券成功交易其他接送机', activity_object=2, activity_from=9, use_type=3)
        # 正常创建折扣券，适用类型：成功交易用户，活动来源：其他，活动使用类型：实时单
        create_discount_activity(name='测试折扣券成功交易其他实时单', activity_object=2, activity_from=9, use_type=2)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：银行活动发放，活动使用类型：通用
        create_discount_activity(name='测试折扣券本行卡交易银行发放通用', activity_object=3, activity_from=1, use_type=1)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：银行活动发放，活动使用类型：接送机
        create_discount_activity(name='测试折扣券本行卡交易银行发放接送机', activity_object=3, activity_from=1, use_type=3)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：银行活动发放，活动使用类型：实时单
        create_discount_activity(name='测试折扣券本行卡交易银行发放实时单', activity_object=3, activity_from=1, use_type=2)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：用户购买，活动使用类型：通用
        create_discount_activity(name='测试折扣券本行卡交易用户购买通用', activity_object=3, activity_from=2, use_type=1)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：用户购买，活动使用类型：接送机
        create_discount_activity(name='测试折扣券本行卡交易用户购买接送机', activity_object=3, activity_from=2, use_type=3)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：用户购买，活动使用类型：实时单
        create_discount_activity(name='测试折扣券本行卡交易用户购买实时单', activity_object=3, activity_from=2, use_type=2)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：管理员发放，活动使用类型：通用
        create_discount_activity(name='测试折扣券本行卡交易管理员发放通用', activity_object=3, activity_from=3, use_type=1)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：管理员发放，活动使用类型：接送机
        create_discount_activity(name='测试折扣券本行卡交易管理员发放接送机', activity_object=3, activity_from=3, use_type=3)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：管理员发放，活动使用类型：实时单
        create_discount_activity(name='测试折扣券本行卡交易管理员发放实时单', activity_object=3, activity_from=3, use_type=2)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：投诉处理，活动使用类型：通用
        create_discount_activity(name='测试折扣券本行卡交易投诉处理通用', activity_object=3, activity_from=4, use_type=1)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：投诉处理，活动使用类型：接送机
        create_discount_activity(name='测试折扣券本行卡交易投诉处理接送机', activity_object=3, activity_from=4, use_type=3)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：投诉处理，活动使用类型：实时单
        create_discount_activity(name='测试折扣券本行卡交易投诉处理实时单', activity_object=3, activity_from=4, use_type=2)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：其他，活动使用类型：通用
        create_discount_activity(name='测试折扣券本行卡交易其他通用', activity_object=3, activity_from=9, use_type=1)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：其他，活动使用类型：接送机
        create_discount_activity(name='测试折扣券本行卡交易其他接送机', activity_object=3, activity_from=9, use_type=3)
        # 正常创建折扣券，适用类型：本行卡交易，活动来源：其他，活动使用类型：实时单
        create_discount_activity(name='测试折扣券本行卡交易其他实时单', activity_object=3, activity_from=9, use_type=2)
        # 正常创建折扣券，适用类型：登录用户，活动来源：银行活动发放，活动使用类型：通用
        create_discount_activity(name='测试折扣券登录用户银行发放通用', activity_object=4, activity_from=1, use_type=1)
        # 正常创建折扣券，适用类型：登录用户，活动来源：银行活动发放，活动使用类型：接送机
        create_discount_activity(name='测试折扣券登录用户银行发放接送机', activity_object=4, activity_from=1, use_type=3)
        # 正常创建折扣券，适用类型：登录用户，活动来源：银行活动发放，活动使用类型：实时单
        create_discount_activity(name='测试折扣券登录用户银行发放实时单', activity_object=4, activity_from=1, use_type=2)
        # 正常创建折扣券，适用类型：登录用户，活动来源：用户购买，活动使用类型：通用
        create_discount_activity(name='测试折扣券登录用户用户购买通用', activity_object=4, activity_from=2, use_type=1)
        # 正常创建折扣券，适用类型：登录用户，活动来源：用户购买，活动使用类型：接送机
        create_discount_activity(name='测试折扣券登录用户用户购买接送机', activity_object=4, activity_from=2, use_type=3)
        # 正常创建折扣券，适用类型：登录用户，活动来源：用户购买，活动使用类型：实时单
        create_discount_activity(name='测试折扣券登录用户用户购买实时单', activity_object=4, activity_from=2, use_type=2)
        # 正常创建折扣券，适用类型：登录用户，活动来源：管理员发放，活动使用类型：通用
        create_discount_activity(name='测试折扣券登录用户管理员发放通用', activity_object=4, activity_from=3, use_type=1)
        # 正常创建折扣券，适用类型：登录用户，活动来源：管理员发放，活动使用类型：接送机
        create_discount_activity(name='测试折扣券登录用户管理员发放接送机', activity_object=4, activity_from=3, use_type=3)
        # 正常创建折扣券，适用类型：登录用户，活动来源：管理员发放，活动使用类型：实时单
        create_discount_activity(name='测试折扣券登录用户管理员发放实时单', activity_object=4, activity_from=3, use_type=2)
        # 正常创建折扣券，适用类型：登录用户，活动来源：投诉处理，活动使用类型：通用
        create_discount_activity(name='测试折扣券登录用户投诉处理通用', activity_object=4, activity_from=4, use_type=1)
        # 正常创建满减券，适用类型：登录用户，活动来源：投诉处理，活动使用类型：接送机
        create_discount_activity(name='测试折扣券登录用户投诉处理接送机', activity_object=4, activity_from=4, use_type=3)
        # 正常创建折扣券，适用类型：登录用户，活动来源：投诉处理，活动使用类型：实时单
        create_discount_activity(name='测试折扣券登录用户投诉处理实时单', activity_object=4, activity_from=4, use_type=2)
        # 正常创建折扣券，适用类型：登录用户，活动来源：其他，活动使用类型：通用
        create_discount_activity(name='测试折扣券登录用户其他通用', activity_object=4, activity_from=9, use_type=1)
        # 正常创建折扣券，适用类型：登录用户，活动来源：其他，活动使用类型：接送机
        create_discount_activity(name='测试折扣券登录用户其他接送机', activity_object=4, activity_from=9, use_type=3)
        # 正常创建折扣券，适用类型：登录用户，活动来源：其他，活动使用类型：实时单
        create_discount_activity(name='测试折扣券登录用户其他实时单', activity_object=4, activity_from=9, use_type=2)
        # 正常创建折扣券，适用类型：批量充值，活动来源：银行活动发放，活动使用类型：通用
        create_discount_activity(name='测试折扣券批量充值银行发放通用', activity_object=5, activity_from=1, use_type=1)
        # 正常创建折扣券，适用类型：批量充值，活动来源：银行活动发放，活动使用类型：接送机
        create_discount_activity(name='测试折扣券批量充值银行发放接送机', activity_object=5, activity_from=1, use_type=3)
        # 正常创建折扣券，适用类型：批量充值，活动来源：银行活动发放，活动使用类型：实时单
        create_discount_activity(name='测试折扣券批量充值银行发放实时单', activity_object=5, activity_from=1, use_type=2)
        # 正常创建折扣券，适用类型：批量充值，活动来源：用户购买，活动使用类型：通用
        create_discount_activity(name='测试折扣券批量充值用户购买通用', activity_object=5, activity_from=2, use_type=1)
        # 正常创建折扣券，适用类型：批量充值，活动来源：用户购买，活动使用类型：接送机
        create_discount_activity(name='测试折扣券批量充值用户购买接送机', activity_object=5, activity_from=2, use_type=3)
        # 正常创建折扣券，适用类型：批量充值，活动来源：用户购买，活动使用类型：实时单
        create_discount_activity(name='测试折扣券批量充值用户购买实时单', activity_object=5, activity_from=2, use_type=2)
        # 正常创建折扣券，适用类型：批量充值，活动来源：管理员发放，活动使用类型：通用
        create_discount_activity(name='测试折扣券批量充值管理员发放通用', activity_object=5, activity_from=3, use_type=1)
        # 正常创建折扣券，适用类型：批量充值，活动来源：管理员发放，活动使用类型：接送机
        create_discount_activity(name='测试折扣券批量充值管理员发放接送机', activity_object=5, activity_from=3, use_type=3)
        # 正常创建折扣券，适用类型：批量充值，活动来源：管理员发放，活动使用类型：实时单
        create_discount_activity(name='测试折扣券批量充值管理员发放实时单', activity_object=5, activity_from=3, use_type=2)
        # 正常创建折扣券，适用类型：批量充值，活动来源：投诉处理，活动使用类型：通用
        create_discount_activity(name='测试折扣券批量充值投诉处理通用', activity_object=5, activity_from=4, use_type=1)
        # 正常创建折扣券，适用类型：批量充值，活动来源：投诉处理，活动使用类型：接送机
        create_discount_activity(name='测试折扣券批量充值投诉处理接送机', activity_object=5, activity_from=4, use_type=3)
        # 正常创建折扣券，适用类型：批量充值，活动来源：投诉处理，活动使用类型：实时单
        create_discount_activity(name='测试折扣券批量充值投诉处理实时单', activity_object=5, activity_from=4, use_type=2)
        # 正常创建折扣券，适用类型：批量充值，活动来源：其他，活动使用类型：通用
        create_discount_activity(name='测试折扣券批量充值其他通用', activity_object=5, activity_from=9, use_type=1)
        # 正常创建折扣券，适用类型：批量充值，活动来源：其他，活动使用类型：接送机
        create_discount_activity(name='测试折扣券批量充值其他接送机', activity_object=5, activity_from=9, use_type=3)
        # 正常创建折扣券，适用类型：批量充值，活动来源：其他，活动使用类型：实时单
        create_discount_activity(name='测试折扣券批量充值其他实时单', activity_object=5, activity_from=9, use_type=2)
        # 正常创建折扣券，适用类型：批量充值，活动来源：红包充值，活动使用类型：通用
        create_discount_activity(name='测试折扣券批量充值红包充值通用', activity_object=5, activity_from=5, use_type=1)
        # 正常创建折扣券，适用类型：批量充值，活动来源：红包充值，活动使用类型：接送机
        create_discount_activity(name='测试折扣券批量充值红包充值接送机', activity_object=5, activity_from=5, use_type=3)
        # 正常创建折扣券，适用类型：批量充值，活动来源：红包充值，活动使用类型：实时单
        create_discount_activity(name='测试折扣券批量充值红包充值实时单', activity_object=5, activity_from=5, use_type=2)

        # 创建折扣券相同签报号不通来源，适用类型：批量充值，活动来源：红包充值，活动使用类型：实时单
        create_discount_activity(name='测试折扣券批量充值红包充值实时单', activity_object=5, activity_from=5, use_type=2,sign_id='测试折扣券相同签报号')
        # 创建折扣券相同签报号不通来源，适用类型：批量充值，活动来源：银行活动发放，活动使用类型：实时单
        create_discount_activity(name='测试折扣券批量充值红包充值实时单', activity_object=5, activity_from=1, use_type=2,sign_id='测试折扣券相同签报号')
        # 创建折扣券相同签报号不通来源，适用类型：批量充值，活动来源：用户购买，活动使用类型：实时单
        create_discount_activity(name='测试折扣券批量充值红包充值实时单', activity_object=5, activity_from=2, use_type=2,sign_id='测试折扣券相同签报号')
        # 创建折扣券相同签报号不通来源，适用类型：批量充值，活动来源：其他，活动使用类型：实时单
        create_discount_activity(name='测试折扣券批量充值红包充值实时单', activity_object=5, activity_from=9, use_type=2,sign_id='测试折扣券相同签报号')

        # 查询活动列表
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 0,  # 查询全部状态
                                   'activityId': None, 'activityType': None, 'signId': None, 'pageSize': 100,
                                   'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        self.activity_list.reverse()
        for i in range(len(self.activity_list)):
            assert self.activity_list[i]['activity_id'] == activity_list[i]['activityId']
            assert self.activity_list[i]['activity_name'] == activity_list[i]['activityName']
            assert self.activity_list[i]['activity_object'] == activity_list[i]['activityObjectDesc']
            assert self.activity_list[i]['activity_object_id'] == activity_list[i]['activityObject']
            assert self.activity_list[i]['activity_from'] == activity_list[i]['activityFromDesc']
            assert self.activity_list[i]['activity_from_id'] == activity_list[i]['activityFrom']
            assert self.activity_list[i]['use_type'] == activity_list[i]['activityUseTypeDesc']
            assert self.activity_list[i]['use_type_id'] == activity_list[i]['activityUseType']
            assert activity_list[i]['expireTime'] == 15
            assert activity_list[i]['grantTotal'] == 100
            assert activity_list[i]['signId'] == self.activity_list[i]['sign_id']
            assert activity_list[i]['activityStartTime'] == start_time
            assert activity_list[i]['activityEndTime'] == end_time
            assert activity_list[i]['activityStatus'] == 1
            assert activity_list[i]['activityStatusDesc'] == '生效'
            assert activity_list[i]['activityType'] == 2
            assert activity_list[i]['activityTypeDesc'] == '折扣券'
            self.activity_list[i].update({"id":activity_list[i]['id']})

        # 查询活动详情
        for x in self.activity_list:
            get_activity_detail_api = GetActivityDetailApi()
            get_activity_detail_api.get({'activityId': x['id']})
            assert get_activity_detail_api.get_status_code() == 200
            assert get_activity_detail_api.get_resp_code() == 0
            assert get_activity_detail_api.get_resp_message() == 'OK'
            activity_detail_data = get_activity_detail_api.get_resp_data()
            assert activity_detail_data['activityCycleTotalTime'] == ''
            assert activity_detail_data['activityCycleType'] == ''
            assert activity_detail_data['activityId'] == x['activity_id']
            assert activity_detail_data['activityName'] == x['activity_name']
            assert activity_detail_data['activityPeopleCount'] == ''
            assert activity_detail_data['activityUseType'] == x['use_type_id']
            assert activity_detail_data['activityUseTypeDesc'] == x['use_type']
            assert activity_detail_data['couponAmount'] == '5000'
            assert activity_detail_data['couponDiscount'] == '0.80'
            assert activity_detail_data['description'] == x['desc']
            assert activity_detail_data['discountAmountMax'] == ''
            assert activity_detail_data['discountAmountMin'] == ''
            assert activity_detail_data['payAmount'] == '10000'
            assert activity_detail_data['payAmountMax'] == ''
            assert activity_detail_data['payAmountMin'] == ''

    def create_activity_random(self):
        """
        测试创建随机立减
        :return:
        """
        now_time = datetime.datetime.now()
        start_time = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S")
        def create_random_activity(name, activity_object, activity_from, use_type,activity_cycle_type,sign_id=None):
            """
            创建随机立减活动
            :param name:活动名称
            :param sign_id:签报号
            :param activity_object:适用类型
            :param activity_from:活动来源
            :param use_type:活动使用类型
            :return:
            """
            if not sign_id:
                sign_id_text = '《签报号》001abc' + str(int(time.time())) + str(random.randint(100, 999))
            else:
                sign_id_text = sign_id
            # 正常创建随机立减
            create_activity_api = AddActivityApi()
            description = BaseFaker().create_sentence()  # 随机生成一段文字
            activity_id = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
            create_activity_api.post(
                {"activityStartTime": start_time, "activityEndTime": end_time,
                 "activityType": "3", "activityObject": activity_object, "couponExpireTime": "", "grantTotal": "100",
                 "couponDiscount": "", "payAmount": "", "couponAmount": "", "activityName": name,
                 "signId": sign_id_text, "activityId":activity_id, "payAmountMin": 10000, "discountAmountMin": 2000,
                 "discountAmountMax": 3000, "activityPeopleCount": "5", "activityCycleType": activity_cycle_type,
                 "activityCycleTotalTime": "50", "activityFrom": activity_from, "activityUseType": use_type, "description": description})
            assert create_activity_api.get_status_code() == 200
            assert create_activity_api.get_resp_code() == 0
            assert create_activity_api.get_resp_message() == 'OK'
            time.sleep(0.5)
            activity_from_desc = None
            if activity_from == 1:
                activity_from_desc = '银行活动发放'
            elif activity_from == 2:
                activity_from_desc = '用户购买'
            elif activity_from == 3:
                activity_from_desc = '管理员发放'
            elif activity_from == 4:
                activity_from_desc = '投诉处理'
            elif activity_from == 9:
                activity_from_desc = '其他'
            elif activity_from == 5:
                activity_from_desc = '红包充值'

            activity_object_desc = None
            if activity_object == 7:
                activity_object_desc = '客户端用户'
            elif activity_object == 6:
                activity_object_desc = '白名单充值'

            use_type_desc = None
            if use_type == 1:
                use_type_desc = '通用'
            elif use_type == 2:
                use_type_desc = '专车'
            elif use_type == 3:
                use_type_desc = '接送机'

            if activity_cycle_type == 1:
                activity_cycle_type_desc = '日'
            elif activity_cycle_type == 2:
                activity_cycle_type_desc = '月'
            else:
                activity_cycle_type_desc = '活动期间'
            self.activity_list.append({'activity_id': activity_id, 'activity_name': name,
                                       'activity_object': activity_object_desc, 'activity_object_id': activity_object,
                                       'activity_from_id': activity_from, 'activity_from': activity_from_desc,
                                       'use_type': use_type_desc, 'use_type_id': use_type,
                                       'sign_id': sign_id_text,'desc':description,'activity_cycle_type':activity_cycle_type,'activity_cycle_type_desc':activity_cycle_type_desc})  # 将该活动信息加入全局变量列表中

        # 正常创建随机立减，适用类型：客户端用户，活动来源：银行活动发放，活动使用类型：通用
        create_random_activity(name='测试随机立减客户端用户银行发放通用', activity_object=7, activity_from=1, use_type=1,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：客户端用户，活动来源：银行活动发放，活动使用类型：接送机
        create_random_activity(name='测试随机立减客户端用户银行发放接送机', activity_object=7, activity_from=1, use_type=3,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：客户端用户，活动来源：银行活动发放，活动使用类型：实时单
        create_random_activity(name='测试随机立减客户端用户银行发放实时单', activity_object=7, activity_from=1, use_type=2,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：客户端用户，活动来源：用户购买，活动使用类型：通用
        create_random_activity(name='测试随机立减客户端用户用户购买通用', activity_object=7, activity_from=2, use_type=1,activity_cycle_type=2)
        # 正常创建随机立减，适用类型：客户端用户，活动来源：用户购买，活动使用类型：接送机
        create_random_activity(name='测试随机立减客户端用户用户购买接送机', activity_object=7, activity_from=2, use_type=3,activity_cycle_type=2)
        # 正常创建随机立减，适用类型：客户端用户，活动来源：用户购买，活动使用类型：实时单
        create_random_activity(name='测试随机立减客户端用户用户购买实时单', activity_object=7, activity_from=2, use_type=2,activity_cycle_type=2)
        # 正常创建随机立减，适用类型：客户端用户，活动来源：管理员发放，活动使用类型：通用
        create_random_activity(name='测试随机立减客户端用户管理员发放通用', activity_object=7, activity_from=3, use_type=1,activity_cycle_type=3)
        # 正常创建随机立减，适用类型：客户端用户，活动来源：管理员发放，活动使用类型：接送机
        create_random_activity(name='测试随机立减客户端用户管理员发放接送机', activity_object=7, activity_from=3, use_type=3,activity_cycle_type=3)
        # 正常创建随机立减，适用类型：客户端用户，活动来源：管理员发放，活动使用类型：实时单
        create_random_activity(name='测试随机立减客户端用户管理员发放实时单', activity_object=7, activity_from=3, use_type=2,activity_cycle_type=3)
        # 正常创建随机立减，适用类型：客户端用户，活动来源：投诉处理，活动使用类型：通用
        create_random_activity(name='测试随机立减客户端用户投诉处理通用', activity_object=7, activity_from=4, use_type=1,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：客户端用户，活动来源：投诉处理，活动使用类型：接送机
        create_random_activity(name='测试随机立减客户端用户投诉处理接送机', activity_object=7, activity_from=4, use_type=3,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：客户端用户，活动来源：投诉处理，活动使用类型：实时单
        create_random_activity(name='测试随机立减客户端用户投诉处理实时单', activity_object=7, activity_from=4, use_type=2,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：客户端用户，活动来源：其他，活动使用类型：通用
        create_random_activity(name='测试随机立减客户端用户其他通用', activity_object=7, activity_from=9, use_type=1,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：客户端用户，活动来源：其他，活动使用类型：接送机
        create_random_activity(name='测试随机立减客户端用户其他接送机', activity_object=7, activity_from=9, use_type=3,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：客户端用户，活动来源：其他，活动使用类型：实时单
        create_random_activity(name='测试随机立减客户端用户其他实时单', activity_object=7, activity_from=9, use_type=2,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：白名单，活动来源：银行活动发放，活动使用类型：通用
        create_random_activity(name='测试随机立减白名单银行发放通用', activity_object=6, activity_from=1, use_type=1,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：白名单，活动来源：银行活动发放，活动使用类型：接送机
        create_random_activity(name='测试随机立减白名单银行发放接送机', activity_object=6, activity_from=1, use_type=3,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：白名单，活动来源：银行活动发放，活动使用类型：实时单
        create_random_activity(name='测试随机立减白名单银行发放实时单', activity_object=6, activity_from=1, use_type=2,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：白名单，活动来源：用户购买，活动使用类型：通用
        create_random_activity(name='测试随机立减白名单用户购买通用', activity_object=6, activity_from=2, use_type=1,activity_cycle_type=2)
        # 正常创建随机立减，适用类型：白名单，活动来源：用户购买，活动使用类型：接送机
        create_random_activity(name='测试随机立减白名单用户购买接送机', activity_object=6, activity_from=2, use_type=3,activity_cycle_type=2)
        # 正常创建随机立减，适用类型：白名单，活动来源：用户购买，活动使用类型：实时单
        create_random_activity(name='测试随机立减白名单用户购买实时单', activity_object=6, activity_from=2, use_type=2,activity_cycle_type=2)
        # 正常创建随机立减，适用类型：白名单，活动来源：管理员发放，活动使用类型：通用
        create_random_activity(name='测试随机立减白名单管理员发放通用', activity_object=6, activity_from=3, use_type=1,activity_cycle_type=3)
        # 正常创建随机立减，适用类型：白名单，活动来源：管理员发放，活动使用类型：接送机
        create_random_activity(name='测试随机立减白名单管理员发放接送机', activity_object=6, activity_from=3, use_type=3,activity_cycle_type=3)
        # 正常创建随机立减，适用类型：白名单，活动来源：管理员发放，活动使用类型：实时单
        create_random_activity(name='测试随机立减白名单管理员发放实时单', activity_object=6, activity_from=3, use_type=2,activity_cycle_type=3)
        # 正常创建随机立减，适用类型：白名单，活动来源：投诉处理，活动使用类型：通用
        create_random_activity(name='测试随机立减白名单投诉处理通用', activity_object=6, activity_from=4, use_type=1,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：白名单，活动来源：投诉处理，活动使用类型：接送机
        create_random_activity(name='测试随机立减白名单投诉处理接送机', activity_object=6, activity_from=4, use_type=3,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：白名单，活动来源：投诉处理，活动使用类型：实时单
        create_random_activity(name='测试随机立减白名单投诉处理实时单', activity_object=6, activity_from=4, use_type=2,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：白名单，活动来源：其他，活动使用类型：通用
        create_random_activity(name='测试随机立减白名单其他通用', activity_object=6, activity_from=9, use_type=1,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：白名单，活动来源：其他，活动使用类型：接送机
        create_random_activity(name='测试随机立减白名单其他接送机', activity_object=6, activity_from=9, use_type=3,activity_cycle_type=1)
        # 正常创建随机立减，适用类型：白名单，活动来源：其他，活动使用类型：实时单
        create_random_activity(name='测试随机立减白名单其他实时单', activity_object=6, activity_from=9, use_type=2,activity_cycle_type=1)

        # 创建随机立减相同签报号不同来源，适用类型：白名单，活动来源：其他，活动使用类型：实时单
        create_random_activity(name='测试随机立减白名单其他实时单', activity_object=6, activity_from=9, use_type=2,activity_cycle_type=1,sign_id='测试随机立减相同签报号')
        # 创建随机立减相同签报号不同来源，适用类型：白名单，活动来源：银行活动发放，活动使用类型：实时单
        create_random_activity(name='测试随机立减白名单其他实时单', activity_object=6, activity_from=1, use_type=2,activity_cycle_type=1,sign_id='测试随机立减相同签报号')
        # 创建随机立减相同签报号不同来源，适用类型：白名单，活动来源：用户购买，活动使用类型：实时单
        create_random_activity(name='测试随机立减白名单其他实时单', activity_object=6, activity_from=2, use_type=2,activity_cycle_type=1,sign_id='测试随机立减相同签报号')


        # 查询活动列表
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 0,  # 查询全部状态
                                   'activityId': None, 'activityType': None, 'signId': None, 'pageSize': 100,
                                   'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        self.activity_list.reverse()
        for i in range(len(self.activity_list)):
            assert self.activity_list[i]['activity_id'] == activity_list[i]['activityId']
            assert self.activity_list[i]['activity_name'] == activity_list[i]['activityName']
            assert self.activity_list[i]['activity_object'] == activity_list[i]['activityObjectDesc']
            assert self.activity_list[i]['activity_object_id'] == activity_list[i]['activityObject']
            assert self.activity_list[i]['activity_from'] == activity_list[i]['activityFromDesc']
            assert self.activity_list[i]['activity_from_id'] == activity_list[i]['activityFrom']
            assert self.activity_list[i]['use_type'] == activity_list[i]['activityUseTypeDesc']
            assert self.activity_list[i]['use_type_id'] == activity_list[i]['activityUseType']
            assert activity_list[i]['expireTime'] == ''
            assert activity_list[i]['grantTotal'] == 100
            assert activity_list[i]['signId'] == self.activity_list[i]['sign_id']
            assert activity_list[i]['activityStartTime'] == start_time
            assert activity_list[i]['activityEndTime'] == end_time
            assert activity_list[i]['activityStatus'] == 1
            assert activity_list[i]['activityStatusDesc'] == '生效'
            assert activity_list[i]['activityType'] == 3
            assert activity_list[i]['activityTypeDesc'] == '随机立减'
            self.activity_list[i].update({"id":activity_list[i]['id']})

        # 查询活动详情
        for x in self.activity_list:
            get_activity_detail_api = GetActivityDetailApi()
            get_activity_detail_api.get({'activityId': x['id']})
            assert get_activity_detail_api.get_status_code() == 200
            assert get_activity_detail_api.get_resp_code() == 0
            assert get_activity_detail_api.get_resp_message() == 'OK'
            activity_detail_data = get_activity_detail_api.get_resp_data()
            assert activity_detail_data['activityCycleTotalTime'] == 50
            assert activity_detail_data['activityCycleType'] == x['activity_cycle_type_desc']
            assert activity_detail_data['activityId'] == x['activity_id']
            assert activity_detail_data['activityName'] == x['activity_name']
            assert activity_detail_data['activityPeopleCount'] == 5
            assert activity_detail_data['activityUseType'] == x['use_type_id']
            assert activity_detail_data['activityUseTypeDesc'] == x['use_type']
            assert activity_detail_data['couponAmount'] == ''
            assert activity_detail_data['couponDiscount'] == ''
            assert activity_detail_data['description'] == x['desc']
            assert activity_detail_data['discountAmountMax'] == '3000'
            assert activity_detail_data['discountAmountMin'] == '2000'
            assert activity_detail_data['payAmount'] == ''
            assert activity_detail_data['payAmountMax'] == ''
            assert activity_detail_data['payAmountMin'] == '10000'

    def query_activity(self):
        """
        活动查询
        :return:
        """
        now_time = datetime.datetime.now()
        start_time = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S")
        # 创建满减券第一个
        create_activity_api = AddActivityApi()
        description = BaseFaker().create_sentence()  # 随机生成一段文字
        full_cut_activity_id_one = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
        create_activity_api.post({"activityObject": 1, "activityStartTime": start_time,
                                  "activityEndTime": end_time, "activityName": '测试活动查询满减券1',
                                  "signId": '签报号-满减券11009877823',
                                  "activityId": full_cut_activity_id_one, "couponExpireTime": 15, "grantTotal": 100,
                                  "activityFrom": 1, "activityUseType": 1, "activityType": 1,
                                  "couponDiscount": "",
                                  "payAmount": 10000, "couponAmount": 5000, "payAmountMin": "", "payAmountMax": "",
                                  "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
                                  "activityCycleType": "", "activityCycleTotalTime": "",
                                  "description": description})
        assert create_activity_api.get_status_code() == 200
        assert create_activity_api.get_resp_code() == 0
        assert create_activity_api.get_resp_message() == 'OK'
        self.activity_list.append({'activity_id': full_cut_activity_id_one,'sign_id': '测试活动查询满减券'})  # 将该活动信息加入全局变量列表中
        time.sleep(1)
        # 创建满减券第二个签报号与第一个相同
        create_activity_api = AddActivityApi()
        description = BaseFaker().create_sentence()  # 随机生成一段文字
        full_cut_activity_id_two = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
        create_activity_api.post({"activityObject": 1, "activityStartTime": start_time,
                                  "activityEndTime": end_time, "activityName": '测试活动查询满减券2',
                                  "signId": '签报号-满减券11009877823',
                                  "activityId": full_cut_activity_id_two, "couponExpireTime": 15, "grantTotal": 100,
                                  "activityFrom": 1, "activityUseType": 1, "activityType": 1,
                                  "couponDiscount": "",
                                  "payAmount": 10000, "couponAmount": 5000, "payAmountMin": "", "payAmountMax": "",
                                  "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
                                  "activityCycleType": "", "activityCycleTotalTime": "",
                                  "description": description})
        assert create_activity_api.get_status_code() == 200
        assert create_activity_api.get_resp_code() == 0
        assert create_activity_api.get_resp_message() == 'OK'
        self.activity_list.append({'activity_id': full_cut_activity_id_two,'sign_id': '测试活动查询满减券'})  # 将该活动信息加入全局变量列表中
        # 创建折扣券
        create_activity_api = AddActivityApi()
        description = BaseFaker().create_sentence()  # 随机生成一段文字
        discount_activity_id = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
        create_activity_api.post({"activityObject": 1, "activityStartTime": start_time,
                                  "activityEndTime": end_time, "activityName": '测试活动查询折扣券',
                                  "signId": '签报号-折扣券',
                                  "activityId": discount_activity_id, "couponExpireTime": 15, "grantTotal": 100,
                                  "activityFrom": 1, "activityUseType": 1, "activityType": 2,
                                  "couponDiscount": "0.8",
                                  "payAmount": 10000, "couponAmount": 5000, "payAmountMin": "", "payAmountMax": "",
                                  "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
                                  "activityCycleType": "", "activityCycleTotalTime": "",
                                  "description": description})
        assert create_activity_api.get_status_code() == 200
        assert create_activity_api.get_resp_code() == 0
        assert create_activity_api.get_resp_message() == 'OK'
        self.activity_list.append({'activity_id': discount_activity_id, 'sign_id': '测试活动查询折扣券'})  # 将该活动信息加入全局变量列表中
        # 创建随机立减
        create_activity_api = AddActivityApi()
        description = BaseFaker().create_sentence()  # 随机生成一段文字
        random_activity_id = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
        create_activity_api.post(
            {"activityStartTime": start_time, "activityEndTime": end_time,
             "activityType": "3", "activityObject": 1, "couponExpireTime": "", "grantTotal": "100",
             "couponDiscount": "", "payAmount": "", "couponAmount": "", "activityName": '测试活动查询随机立减',
             "signId": '签报号-随机立减', "activityId": random_activity_id, "payAmountMin": 10000, "discountAmountMin": 2000,
             "discountAmountMax": 3000, "activityPeopleCount": "5", "activityCycleType": 1,
             "activityCycleTotalTime": "50", "activityFrom": 1, "activityUseType": 1,
             "description": description})
        assert create_activity_api.get_status_code() == 200
        assert create_activity_api.get_resp_code() == 0
        assert create_activity_api.get_resp_message() == 'OK'
        self.activity_list.append({'activity_id': random_activity_id, 'sign_id': '测试活动查询随机立减'})  # 将该活动信息加入全局变量列表中
        # 根据活动ID查询
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 0,  # 查询全部状态
                                   'activityId': random_activity_id, 'activityType': None, 'signId': None, 'pageSize': None,'pageNum': None})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        assert len(activity_list) == 1
        assert activity_list[0]['activityId'] == random_activity_id
        assert activity_list[0]['activityName'] == '测试活动查询随机立减'
        assert activity_list[0]['activityObjectDesc'] == '新用户 平台首单'
        assert activity_list[0]['activityObject'] == 1
        assert activity_list[0]['activityFromDesc'] == '银行活动发放'
        assert activity_list[0]['activityFrom'] == 1
        assert activity_list[0]['activityUseTypeDesc'] == '通用'
        assert activity_list[0]['activityUseType'] == 1
        assert activity_list[0]['expireTime'] == ''
        assert activity_list[0]['grantTotal'] == 100
        assert activity_list[0]['signId'] == '签报号-随机立减'
        assert activity_list[0]['activityStartTime'] == start_time
        assert activity_list[0]['activityEndTime'] == end_time
        assert activity_list[0]['activityStatus'] == 1
        assert activity_list[0]['activityStatusDesc'] == '生效'
        assert activity_list[0]['activityType'] == 3
        assert activity_list[0]['activityTypeDesc'] == '随机立减'

        # 根据签报号查询
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 0,  # 查询全部状态
                                   'activityId': None, 'activityType': None, 'signId': '签报号-满减券11009877823', 'pageSize': None,'pageNum': None})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        assert len(activity_list) == 2
        assert activity_list[0]['activityId'] == full_cut_activity_id_two
        assert activity_list[0]['activityName'] == '测试活动查询满减券2'
        assert activity_list[0]['activityObjectDesc'] == '新用户 平台首单'
        assert activity_list[0]['activityObject'] == 1
        assert activity_list[0]['activityFromDesc'] == '银行活动发放'
        assert activity_list[0]['activityFrom'] == 1
        assert activity_list[0]['activityUseTypeDesc'] == '通用'
        assert activity_list[0]['activityUseType'] == 1
        assert activity_list[0]['expireTime'] == 15
        assert activity_list[0]['grantTotal'] == 100
        assert activity_list[0]['signId'] == '签报号-满减券11009877823'
        assert activity_list[0]['activityStartTime'] == start_time
        assert activity_list[0]['activityEndTime'] == end_time
        assert activity_list[0]['activityStatus'] == 1
        assert activity_list[0]['activityStatusDesc'] == '生效'
        assert activity_list[0]['activityType'] == 1
        assert activity_list[0]['activityTypeDesc'] == '满减券'
        assert activity_list[1]['activityId'] == full_cut_activity_id_one
        assert activity_list[1]['activityName'] == '测试活动查询满减券1'
        assert activity_list[1]['activityObjectDesc'] == '新用户 平台首单'
        assert activity_list[1]['activityObject'] == 1
        assert activity_list[1]['activityFromDesc'] == '银行活动发放'
        assert activity_list[1]['activityFrom'] == 1
        assert activity_list[1]['activityUseTypeDesc'] == '通用'
        assert activity_list[1]['activityUseType'] == 1
        assert activity_list[1]['expireTime'] == 15
        assert activity_list[1]['grantTotal'] == 100
        assert activity_list[1]['signId'] == '签报号-满减券11009877823'
        assert activity_list[1]['activityStartTime'] == start_time
        assert activity_list[1]['activityEndTime'] == end_time
        assert activity_list[1]['activityStatus'] == 1
        assert activity_list[1]['activityStatusDesc'] == '生效'
        assert activity_list[1]['activityType'] == 1
        assert activity_list[1]['activityTypeDesc'] == '满减券'

        # 根据活动类型查询满减券
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 0,  # 查询全部状态
                                   'activityId': None, 'activityType': 1, 'signId': None, 'pageSize': 1000,'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        for x in activity_list:
            assert x['activityType'] == 1
            assert x['activityTypeDesc'] == '满减券'
        assert activity_list[0]['activityId'] == full_cut_activity_id_two
        assert activity_list[0]['activityName'] == '测试活动查询满减券2'
        assert activity_list[1]['activityId'] == full_cut_activity_id_one
        assert activity_list[1]['activityName'] == '测试活动查询满减券1'
        test_close_activity_id = activity_list[1]['id']

        # 根据活动类型查询折扣券
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 0,  # 查询全部状态
                                   'activityId': None, 'activityType': 2, 'signId': None, 'pageSize': 1000,
                                   'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        for x in activity_list:
            assert x['activityType'] == 2
            assert x['activityTypeDesc'] == '折扣券'
        assert activity_list[0]['activityId'] == discount_activity_id
        assert activity_list[0]['activityName'] == '测试活动查询折扣券'

        # 根据活动类型查询随机立减
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 0,  # 查询全部状态
                                   'activityId': None, 'activityType': 3, 'signId': None, 'pageSize': 1000,
                                   'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        for x in activity_list:
            assert x['activityType'] == 3
            assert x['activityTypeDesc'] == '随机立减'
        assert activity_list[0]['activityId'] == random_activity_id
        assert activity_list[0]['activityName'] == '测试活动查询随机立减'

        # 终止一个满减券活动
        close_activity_api = CloseActivityApi()
        close_activity_api.post({'id': int(test_close_activity_id)})
        assert close_activity_api.get_status_code() == 200
        assert close_activity_api.get_resp_code() == 0
        assert close_activity_api.get_resp_message() == 'OK'

        # 再次根据活动类型查询满减券
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 0,  # 查询全部状态
                                   'activityId': None, 'activityType': 1, 'signId': None, 'pageSize': 1000,'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        for x in activity_list:
            assert x['activityType'] == 1
            assert x['activityTypeDesc'] == '满减券'
        assert activity_list[0]['activityId'] == full_cut_activity_id_two
        assert activity_list[0]['activityName'] == '测试活动查询满减券2'
        assert activity_list[1]['activityId'] == full_cut_activity_id_one
        assert activity_list[1]['activityName'] == '测试活动查询满减券1'

        # 根据活动状态查询已终止的活动
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get({'activityStatus': 2,'activityId': None, 'activityType': None, 'signId': None, 'pageSize': 1000,'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        for x in activity_list:
            assert x['activityStatus'] == 2
            assert x['activityStatusDesc'] == '终止'
        assert activity_list[0]['activityId'] == full_cut_activity_id_one
        assert activity_list[0]['activityName'] == '测试活动查询满减券1'

        # 根据活动状态查询开启的活动
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get(
            {'activityStatus': 1, 'activityId': None, 'activityType': None, 'signId': None, 'pageSize': 1000,
             'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        for x in activity_list:
            assert x['activityStatus'] == 1
            assert x['activityStatusDesc'] == '生效'
        assert activity_list[0]['activityId'] == random_activity_id
        assert activity_list[0]['activityName'] == '测试活动查询随机立减'
        assert activity_list[1]['activityId'] == discount_activity_id
        assert activity_list[1]['activityName'] == '测试活动查询折扣券'
        assert activity_list[2]['activityId'] == full_cut_activity_id_two
        assert activity_list[2]['activityName'] == '测试活动查询满减券2'

        # 根据活动状态与类型查询满减券开启的活动
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get(
            {'activityStatus': 1, 'activityId': None, 'activityType': 1, 'signId': None, 'pageSize': 1000,
             'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        for x in activity_list:
            assert x['activityStatus'] == 1
            assert x['activityStatusDesc'] == '生效'
            assert x['activityType'] == 1
            assert x['activityTypeDesc'] == '满减券'
        assert activity_list[0]['activityId'] == full_cut_activity_id_two
        assert activity_list[0]['activityName'] == '测试活动查询满减券2'

        # 根据活动状态与活动ID查询
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get(
            {'activityStatus': 1, 'activityId': full_cut_activity_id_two, 'activityType': None, 'signId': None, 'pageSize': 1000,
             'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        assert len(activity_list) == 1
        assert activity_list[0]['activityStatus'] == 1
        assert activity_list[0]['activityStatusDesc'] == '生效'
        assert activity_list[0]['activityType'] == 1
        assert activity_list[0]['activityTypeDesc'] == '满减券'
        assert activity_list[0]['activityId'] == full_cut_activity_id_two
        assert activity_list[0]['activityName'] == '测试活动查询满减券2'

        # 根据活动状态与签报号查询有数据
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get(
            {'activityStatus': 1, 'activityId': None, 'activityType': None, 'signId': '签报号-满减券11009877823', 'pageSize': 1000,
             'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        assert len(activity_list) == 1
        assert activity_list[0]['activityStatus'] == 1
        assert activity_list[0]['activityStatusDesc'] == '生效'
        assert activity_list[0]['activityType'] == 1
        assert activity_list[0]['activityTypeDesc'] == '满减券'
        assert activity_list[0]['activityId'] == full_cut_activity_id_two
        assert activity_list[0]['activityName'] == '测试活动查询满减券2'

        # 根据活动状态与签报号查询无数据，签报号不存在
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get(
            {'activityStatus': 1, 'activityId': None, 'activityType': None, 'signId': '签报号-满减券110039877823', 'pageSize': 1000,
             'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        assert len(activity_list) == 0

        # 根据活动ID与签报号查询有数据
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get(
            {'activityStatus': 0, 'activityId': full_cut_activity_id_two, 'activityType': None, 'signId': '签报号-满减券11009877823', 'pageSize': 1000,
             'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        assert len(activity_list) == 1
        assert activity_list[0]['activityStatus'] == 1
        assert activity_list[0]['activityStatusDesc'] == '生效'
        assert activity_list[0]['activityType'] == 1
        assert activity_list[0]['activityTypeDesc'] == '满减券'
        assert activity_list[0]['activityId'] == full_cut_activity_id_two
        assert activity_list[0]['activityName'] == '测试活动查询满减券2'
        # 根据活动ID与签报号查询无数据
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get(
            {'activityStatus': 1, 'activityId': full_cut_activity_id_two, 'activityType': None,
             'signId': '签报号-满减券110098177823', 'pageSize': 1000,
             'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        assert len(activity_list) == 0

        # 根据活动ID与签报号、活动类型查询有数据
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get(
            {'activityStatus': 0, 'activityId': full_cut_activity_id_two, 'activityType': 1, 'signId': '签报号-满减券11009877823', 'pageSize': 1000,
             'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        assert len(activity_list) == 1
        assert activity_list[0]['activityStatus'] == 1
        assert activity_list[0]['activityStatusDesc'] == '生效'
        assert activity_list[0]['activityType'] == 1
        assert activity_list[0]['activityTypeDesc'] == '满减券'
        assert activity_list[0]['activityId'] == full_cut_activity_id_two
        assert activity_list[0]['activityName'] == '测试活动查询满减券2'
        # 根据活动ID与签报号查询无数据
        get_activity_list_api = GetActivityListApi()
        get_activity_list_api.get(
            {'activityStatus': 1, 'activityId': full_cut_activity_id_two, 'activityType': 1,
             'signId': '签报号-满减券110098177823', 'pageSize': 1000,
             'pageNum': 1})
        assert get_activity_list_api.get_status_code() == 200
        assert get_activity_list_api.get_resp_code() == 0
        assert get_activity_list_api.get_resp_message() == 'OK'
        activity_list = get_activity_list_api.get_resp_data()['list']
        assert len(activity_list) == 0

    def query_activity_auto_overdue(self):
        """
        活动自动过期
        :return:
        """
        now_time = datetime.datetime.now()
        start_time = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (now_time + datetime.timedelta(minutes=+1)).strftime("%Y-%m-%d %H:%M:%S")
        # 创建满减券第一个
        create_activity_api = AddActivityApi()
        description = BaseFaker().create_sentence()  # 随机生成一段文字
        full_cut_activity_id = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
        create_activity_api.post({"activityObject": 1, "activityStartTime": start_time,
                                  "activityEndTime": end_time, "activityName": '测试活动自动过期',
                                  "signId": '签报号-活动自动过期',
                                  "activityId": full_cut_activity_id, "couponExpireTime": 15, "grantTotal": 100,
                                  "activityFrom": 1, "activityUseType": 1, "activityType": 1,
                                  "couponDiscount": "",
                                  "payAmount": 10000, "couponAmount": 5000, "payAmountMin": "", "payAmountMax": "",
                                  "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
                                  "activityCycleType": "", "activityCycleTotalTime": "",
                                  "description": description})
        assert create_activity_api.get_status_code() == 200
        assert create_activity_api.get_resp_code() == 0
        assert create_activity_api.get_resp_message() == 'OK'
        self.activity_list.append({'activity_id': full_cut_activity_id,'sign_id': '签报号-活动自动过期'})  # 将该活动信息加入全局变量列表中
        count = 1
        max_count= 200
        while count < max_count:
            # 根据活动ID查询
            get_activity_list_api = GetActivityListApi()
            get_activity_list_api.get({'activityStatus': 0,  # 查询全部状态
                                       'activityId': full_cut_activity_id, 'activityType': None, 'signId': None,
                                       'pageSize': None, 'pageNum': None})
            assert get_activity_list_api.get_status_code() == 200
            assert get_activity_list_api.get_resp_code() == 0
            assert get_activity_list_api.get_resp_message() == 'OK'
            activity_list = get_activity_list_api.get_resp_data()['list']
            assert len(activity_list) == 1
            if activity_list[0]['activityStatus'] == 1:
                count += 1
                time.sleep(5)
                continue
            else:
                assert activity_list[0]['activityId'] == full_cut_activity_id
                assert activity_list[0]['activityName'] == '测试活动自动过期'
                assert activity_list[0]['activityObjectDesc'] == '新用户 平台首单'
                assert activity_list[0]['activityObject'] == 1
                assert activity_list[0]['activityFromDesc'] == '银行活动发放'
                assert activity_list[0]['activityFrom'] == 1
                assert activity_list[0]['activityUseTypeDesc'] == '通用'
                assert activity_list[0]['activityUseType'] == 1
                assert activity_list[0]['expireTime'] == 15
                assert activity_list[0]['grantTotal'] == 100
                assert activity_list[0]['signId'] == '签报号-活动自动过期'
                assert activity_list[0]['activityStartTime'] == start_time
                assert activity_list[0]['activityEndTime'] == end_time
                assert activity_list[0]['activityStatus'] == 2
                assert activity_list[0]['activityStatusDesc'] == '终止'
                assert activity_list[0]['activityType'] == 1
                assert activity_list[0]['activityTypeDesc'] == '满减券'
                break
        assert count < max_count


    def download_import_template(self):
        """
        测试下载模板接口
        :return:
        """
        download_bytes = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00;\x00\x03\x00\xfe\xff\t\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\xfe\xff\xff\xff\x00\x00\x00\x00\x01\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xffR\x00o\x00o\x00t\x00 \x00E\x00n\x00t\x00r\x00y\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x16\x00\x05\x01\xff\xff\xff\xff\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\xc0\x06\x00\x00\x00\x00\x00\x00W\x00o\x00r\x00k\x00b\x00o\x00o\x00k\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x12\x00\x02\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb6\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\xff\xff\xff\xfd\xff\xff\xff\xfe\xff\xff\xff\x04\x00\x00\x00\x05\x00\x00\x00\x06\x00\x00\x00\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00\x05\x00\x00\x00\x06\x00\x00\x00\x07\x00\x00\x00\x08\x00\x00\x00\t\x00\x00\x00\n\x00\x00\x00\x0b\x00\x00\x00\x0c\x00\x00\x00\r\x00\x00\x00\x0e\x00\x00\x00\x0f\x00\x00\x00\x10\x00\x00\x00\x11\x00\x00\x00\x12\x00\x00\x00\x13\x00\x00\x00\x14\x00\x00\x00\x15\x00\x00\x00\x16\x00\x00\x00\x17\x00\x00\x00\x18\x00\x00\x00\x19\x00\x00\x00\x1a\x00\x00\x00\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\t\x08\x10\x00\x00\x06\x05\x00\xd3\x10\xcc\x07A\x00\x00\x00\x06\x00\x00\x00\xe1\x00\x02\x00\xb0\x04\xc1\x00\x02\x00\x00\x00\xe2\x00\x00\x00\\\x00p\x00\x06\x00\x00netcar                                                                                                       B\x00\x02\x00\xb0\x04a\x01\x02\x00\x00\x00=\x01\x02\x00\x00\x00\x9c\x00\x02\x00\x0e\x00\x19\x00\x02\x00\x00\x00\x12\x00\x02\x00\x00\x00\x13\x00\x02\x00\x00\x00\xaf\x01\x02\x00\x00\x00\xbc\x01\x02\x00\x00\x00=\x00\x12\x00h\x01\x0e\x01\\:\xbe#8\x00\x00\x00\x00\x00\x01\x00X\x02@\x00\x02\x00\x00\x00\x8d\x00\x02\x00\x00\x00"\x00\x02\x00\x00\x00\x0e\x00\x02\x00\x01\x00\xb7\x01\x02\x00\x00\x00\xda\x00\x02\x00\x00\x001\x00\x15\x00\xc8\x00\x00\x00\xff\x7f\x90\x01\x00\x00\x00\x00\x00\x00\x05\x00Arial1\x00\x15\x00\xc8\x00\x00\x00\xff\x7f\x90\x01\x00\x00\x00\x00\x00\x00\x05\x00Arial1\x00\x15\x00\xc8\x00\x00\x00\xff\x7f\x90\x01\x00\x00\x00\x00\x00\x00\x05\x00Arial1\x00\x15\x00\xc8\x00\x00\x00\xff\x7f\x90\x01\x00\x00\x00\x00\x00\x00\x05\x00Arial\x1e\x04\x1a\x00\x05\x00\x15\x00\x00"$"#,##0_);("$"#,##0)\x1e\x04\x1f\x00\x06\x00\x1a\x00\x00"$"#,##0_);[Red]("$"#,##0)\x1e\x04 \x00\x07\x00\x1b\x00\x00"$"#,##0.00_);("$"#,##0.00)\x1e\x04%\x00\x08\x00 \x00\x00"$"#,##0.00_);[Red]("$"#,##0.00)\x1e\x045\x00*\x000\x00\x00_("$"* #,##0_);_("$"* (#,##0);_("$"* "-"_);_(@_)\x1e\x04,\x00)\x00\'\x00\x00_(* #,##0_);_(* (#,##0);_(* "-"_);_(@_)\x1e\x04=\x00,\x008\x00\x00_("$"* #,##0.00_);_("$"* (#,##0.00);_("$"* "-"??_);_(@_)\x1e\x044\x00+\x00/\x00\x00_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)\xe0\x00\x14\x00\x00\x00\x00\x00\xf5\xff \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x01\x00\x00\x00\xf5\xff \x00\x00\xf4\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x01\x00\x00\x00\xf5\xff \x00\x00\xf4\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x02\x00\x00\x00\xf5\xff \x00\x00\xf4\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x02\x00\x00\x00\xf5\xff \x00\x00\xf4\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x00\x00\x00\x00\xf5\xff \x00\x00\xf4\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x00\x00\x00\x00\xf5\xff \x00\x00\xf4\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x00\x00\x00\x00\xf5\xff \x00\x00\xf4\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x00\x00\x00\x00\xf5\xff \x00\x00\xf4\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x00\x00\x00\x00\xf5\xff \x00\x00\xf4\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x00\x00\x00\x00\xf5\xff \x00\x00\xf4\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x00\x00\x00\x00\xf5\xff \x00\x00\xf4\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x00\x00\x00\x00\xf5\xff \x00\x00\xf4\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x00\x00\x00\x00\xf5\xff \x00\x00\xf4\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x00\x00\x00\x00\xf5\xff \x00\x00\xf4\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x00\x00\x00\x00\x01\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x01\x00+\x00\xf5\xff \x00\x00\xf8\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x01\x00)\x00\xf5\xff \x00\x00\xf8\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x01\x00,\x00\xf5\xff \x00\x00\xf8\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x01\x00*\x00\xf5\xff \x00\x00\xf8\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x01\x00\t\x00\xf5\xff \x00\x00\xf8\x00\x00\x00\x00\x00\x00\x00\x00\xc0 \xe0\x00\x14\x00\x00\x001\x00\x01\x00 \x00\x00\x00\x00\x00\x08\x04\x08\x04\x00\x00\xc0 \x93\x02\x04\x00\x10\x80\x03\xff\x93\x02\x04\x00\x11\x80\x06\xff\x93\x02\x04\x00\x12\x80\x04\xff\x93\x02\x04\x00\x13\x80\x07\xff\x93\x02\x04\x00\x00\x80\x00\xff\x93\x02\x04\x00\x14\x80\x05\xff`\x01\x02\x00\x00\x00\x85\x00\x0e\x00y\x05\x00\x00\x00\x00\x06\x00Sheet0\x8c\x00\x04\x00\x01\x00\x01\x00\xae\x01\x04\x00\x01\x00\x01\x04\x17\x00\x08\x00\x01\x00\x00\x00\x00\x00\x00\x00\xfc\x00\x13\x00\x01\x00\x00\x00\x01\x00\x00\x00\x04\x00\x01\xab\x8e\xfdN\xc1\x8b\xf7S\xff\x00\n\x00\x08\x00\\\x05\x00\x00\x0c\x00\x00\x00\n\x00\x00\x00\t\x08\x10\x00\x00\x06\x10\x00\xbb\r\xcc\x07\xc1\x00\x00\x00\x06\x00\x00\x00\x0b\x02\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x7f\x06\x00\x00\r\x00\x02\x00\x01\x00\x0c\x00\x02\x00d\x00\x0f\x00\x02\x00\x01\x00\x11\x00\x02\x00\x00\x00\x10\x00\x08\x00\xfc\xa9\xf1\xd2MbP?_\x00\x02\x00\x01\x00*\x00\x02\x00\x00\x00+\x00\x02\x00\x00\x00\x82\x00\x02\x00\x01\x00\x80\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00%\x02\x04\x00\x00\x00\xff\x00\x81\x00\x02\x00\xc1\x04\x14\x00\x00\x00\x15\x00\x00\x00\x83\x00\x02\x00\x00\x00\x84\x00\x02\x00\x00\x00\xa1\x00"\x00\x01\x00d\x00\x01\x00\x01\x00\x01\x00\x02\x00,\x01,\x01\x00\x00\x00\x00\x00\x00\xe0?\x00\x00\x00\x00\x00\x00\xe0?\x01\x00U\x00\x02\x00\x08\x00}\x00\x0c\x00\x00\x00\x00\x00\xf3\x04\x15\x00\x02\x00\x02\x00\x00\x02\x0e\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x08\x02\x10\x00\x00\x00\x00\x00\x01\x00\xff\x00\x00\x00\x00\x00\x00\x01\x0f\x00\xfd\x00\n\x00\x00\x00\x00\x00\x15\x00\x00\x00\x00\x00\xd7\x00\x06\x00"\x00\x00\x00\x00\x00>\x02\x12\x00\xb6\x06\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1d\x00\x0f\x00\x03\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        download_api = DownloadImportTemplateApi()
        download_api.post()
        assert download_api.get_status_code() == 200
        assert download_api.get_resp_content_not_json() == download_bytes

    def upload_file_to_activity(self):
        """
        测试批量充值类型活动
        :return:
        """
        now_time = datetime.datetime.now()
        start_time = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S")
        # 正常创建满减券
        create_activity_api = AddActivityApi()
        description = BaseFaker().create_sentence()  # 随机生成一段文字
        activity_id = hooks.get_random_activity_id()  # 随机生成数据库中不存在的活动ID
        create_activity_api.post({"activityObject": 5, "activityStartTime": start_time,
                                  "activityEndTime": end_time, "activityName": '测试批量充值上传文件',
                                  "signId": '签报-批量充值上传文件',
                                  "activityId": activity_id, "couponExpireTime": 15, "grantTotal": 100,
                                  "activityFrom": 1, "activityUseType": 1, "activityType": 1,
                                  "couponDiscount": "",
                                  "payAmount": 10000, "couponAmount": 5000, "payAmountMin": "", "payAmountMax": "",
                                  "discountAmountMin": "", "discountAmountMax": "", "activityPeopleCount": "",
                                  "activityCycleType": "", "activityCycleTotalTime": "",
                                  "description": description})
        assert create_activity_api.get_status_code() == 200
        assert create_activity_api.get_resp_code() == 0
        assert create_activity_api.get_resp_message() == 'OK'
        self.activity_list.append({'activity_id': activity_id,'sign_id': '签报号-活动自动过期'})  # 将该活动信息加入全局变量列表中
        time.sleep(1)

        # 准备测试文件
        id_num_list = []
        # 调用三次登录接口，生成3个数据库中已存在的新用户
        for i in range(3):
            login_result = TradeLoginApi().login()
            user_mobile = login_result['mobile']
            id_num_list.append({'mobile': user_mobile, 'id_num': str(user_mobile) + '9999999'})
            id_num_list.append({'mobile': user_mobile, 'id_num': str(user_mobile) + '9999999'})

        # 两个数据库中不存在的用户，其中一个用户文件中写入两次
        not_active_user_one = hooks.get_new_mobile()
        not_active_user_two = hooks.get_new_mobile()
        id_num_list.append({'mobile':None,'id_num':str(not_active_user_one) + '9999999'})
        id_num_list.append({'mobile':None,'id_num':str(not_active_user_two) + '9999999'})
        id_num_list.append({'mobile':None,'id_num':str(not_active_user_two) + '9999999'})

        from xlutils.copy import copy
        from HttpRunnerManager.settings import BASE_DIR
        import xlrd,os
        excel_file_path =  os.path.join(BASE_DIR, './ApiManager/pf_netcar_monitoring/ImportTemplate.xls')
        excel_file = xlrd.open_workbook(excel_file_path)
        write_data = copy(excel_file)
        sheet_data = write_data.get_sheet(0)

        row = 1
        for i in id_num_list:
            sheet_data.write(row, 0, i['id_num'])
            row += 1
        write_data.save(excel_file_path)
        time.sleep(1)

        # 请求上传文件接口
        request_data = {'activityId':activity_id}
        files = {'importFile': ('ImportTemplate.xls', open(excel_file_path, 'rb'))}
        import_coupon_recharge_api = ImportCouponRechargeApi()
        response_result = import_coupon_recharge_api.request_api(data=request_data,file=files)
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        import_coupon_recharge_data = response_result['data']
        assert import_coupon_recharge_data['importFailNums'] == 0
        assert import_coupon_recharge_data['importSuccessNums'] == 9
        # 请求查询上传历史接口
        recharge_info_api = RechargeRecordInfoApi()
        recharge_info_api.get({'activityId': activity_id})
        assert recharge_info_api.get_status_code() == 200
        assert recharge_info_api.get_resp_code() == 0
        assert recharge_info_api.get_resp_message() == 'OK'
        recharge_info_data = recharge_info_api.get_resp_data()
        assert len(recharge_info_data['list']) == 1
        assert recharge_info_data['list'][0]['rechargeNum'] == 9
        assert recharge_info_data['list'][0]['activityId'] == activity_id
        assert recharge_info_data['list'][0]['rechargeType'] == ''
        assert recharge_info_data['list'][0]['rechargeTypeDesc'] == '优惠券满减充值'
        batch_id = recharge_info_data['list'][0]['batchId']
        # 校验数据库中批量充值表记录
        coupon_recharge_record = hooks.get_coupon_recharge_record(batch_id)
        assert len(coupon_recharge_record) == 9

        # trade端验证发券，不存在的用户，文件中写入一次
        get_coupon_list_api = GetCouponListApi(mobile=not_active_user_one)
        get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
        assert get_coupon_list_api.get_status_code() == 200
        assert get_coupon_list_api.get_resp_code() == 0
        assert get_coupon_list_api.get_resp_message() == 'OK'
        coupon_list_data = get_coupon_list_api.get_resp_data()
        assert len(coupon_list_data['list']) == 1
        assert coupon_list_data['list'][0]['activityUseType'] == 1
        assert coupon_list_data['list'][0]['couponType'] == 1
        assert coupon_list_data['list'][0]['couponName'] == '测试批量充值上传文件'
        assert coupon_list_data['list'][0]['payAmount'] == 10000
        assert coupon_list_data['list'][0]['couponState'] == '1'
        assert coupon_list_data['list'][0]['couponAmount'] == 5000
        assert coupon_list_data['list'][0]['couponDiscount'] == 0
        assert coupon_list_data['list'][0]['maxCouponAmount'] == 5000
        assert coupon_list_data['list'][0]['description'] == description
        coupon_start_time = coupon_list_data['list'][0]['couponStartTime']
        timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
        coupon_start_time_timeStamp = int(time.mktime(timeArray))
        assert int(time.time()) - coupon_start_time_timeStamp < 120
        assert coupon_list_data['list'][0]['couponEndTime'] == (now_time + datetime.timedelta(days=+15)).strftime("%Y-%m-%d 23:59")

        # trade端验证发券，不存在的用户，文件中写入两次
        get_coupon_list_api = GetCouponListApi(mobile=not_active_user_two)
        get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
        assert get_coupon_list_api.get_status_code() == 200
        assert get_coupon_list_api.get_resp_code() == 0
        assert get_coupon_list_api.get_resp_message() == 'OK'
        coupon_list_data = get_coupon_list_api.get_resp_data()
        assert len(coupon_list_data['list']) == 2
        for x in range(2):
            assert coupon_list_data['list'][x]['activityUseType'] == 1
            assert coupon_list_data['list'][x]['couponType'] == 1
            assert coupon_list_data['list'][x]['couponName'] == '测试批量充值上传文件'
            assert coupon_list_data['list'][x]['payAmount'] == 10000
            assert coupon_list_data['list'][x]['couponState'] == '1'
            assert coupon_list_data['list'][x]['couponAmount'] == 5000
            assert coupon_list_data['list'][x]['couponDiscount'] == 0
            assert coupon_list_data['list'][x]['maxCouponAmount'] == 5000
            assert coupon_list_data['list'][x]['description'] == description
            coupon_start_time = coupon_list_data['list'][x]['couponStartTime']
            timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
            coupon_start_time_timeStamp = int(time.mktime(timeArray))
            assert int(time.time()) - coupon_start_time_timeStamp < 120
            assert coupon_list_data['list'][x]['couponEndTime'] == (now_time + datetime.timedelta(days=+15)).strftime("%Y-%m-%d 23:59")

        # trade端验证发券，已存在的用户，文件中写入两次
        for i in id_num_list:
            if i['mobile']:
                get_coupon_list_api = GetCouponListApi(mobile=i['mobile'])
                get_coupon_list_api.get({"couponStatus": 1,'orderFlag':0})
                assert get_coupon_list_api.get_status_code() == 200
                assert get_coupon_list_api.get_resp_code() == 0
                assert get_coupon_list_api.get_resp_message() == 'OK'
                coupon_list_data = get_coupon_list_api.get_resp_data()
                assert len(coupon_list_data['list']) == 2
                for x in range(2):
                    assert coupon_list_data['list'][x]['activityUseType'] == 1
                    assert coupon_list_data['list'][x]['couponType'] == 1
                    assert coupon_list_data['list'][x]['couponName'] == '测试批量充值上传文件'
                    assert coupon_list_data['list'][x]['payAmount'] == 10000
                    assert coupon_list_data['list'][x]['couponState'] == '1'
                    assert coupon_list_data['list'][x]['couponAmount'] == 5000
                    assert coupon_list_data['list'][x]['couponDiscount'] == 0
                    assert coupon_list_data['list'][x]['maxCouponAmount'] == 5000
                    assert coupon_list_data['list'][x]['description'] == description
                    coupon_start_time = coupon_list_data['list'][x]['couponStartTime']
                    timeArray = time.strptime(coupon_start_time, "%Y-%m-%d %H:%M")
                    coupon_start_time_timeStamp = int(time.mktime(timeArray))
                    assert int(time.time()) - coupon_start_time_timeStamp < 120
                    assert coupon_list_data['list'][x]['couponEndTime'] == (now_time + datetime.timedelta(days=+15)).strftime("%Y-%m-%d 23:59")


    def tearDown(self):
        super(ActivityManagerMonitoring, self).tearDown()
        for x in self.activity_list:
            hooks.delete_activity(x['activity_id'], sign_id=x['sign_id'])
        self.activity_list = []
        time.sleep(5)


if __name__ == '__main__':
    api = ActivityManagerMonitoring()
    api.run_method(monitoring_name='活动管理监控', monitoring_class=api,redis_key=ACTIVITY_MANAGER_MONITORING_KEY)
    # api = ActivityManagerMonitoring()
    # api.upload_file_to_activity()
    # api.tearDown()
