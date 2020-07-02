# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi
from ApiManager.pf_netcar_api.base_api import BaseApi


class GetActivityRulesListApi(LoginBaseApi):
    """
    获取精彩活动列表-已登录
    """
    url = '/netCar/page/activity/rules/getActivityRulesList'



class GetActivityRulesListNotLoginApi(BaseApi):
    """
    获取精彩活动列表-未登录
    """
    url = '/netCar/page/activity/rules/getActivityRulesList'
