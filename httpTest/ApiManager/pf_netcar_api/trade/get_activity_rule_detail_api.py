# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi
from ApiManager.pf_netcar_api.base_api import BaseApi


class GetActivityRulesDetailApi(LoginBaseApi):
    """
    获取精彩活动详情-已登录
    """
    url = '/netCar/page/activity/rules/getRuleDetail'

    def build_custom_param(self, params):
        return {"ruleId":params['id']}


class GetActivityRulesDetailNoLoginApi(BaseApi):
    """
    获取精彩活动详情-未登录
    """
    url = '/netCar/page/activity/rules/getRuleDetail'

    def build_custom_param(self, params):
        return {"ruleId": params['id']}