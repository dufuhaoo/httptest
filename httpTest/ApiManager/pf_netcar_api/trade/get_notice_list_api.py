# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi
from ApiManager.pf_netcar_api.base_api import BaseApi


class GetNoticeListApi(LoginBaseApi):
    """
    获取通知列表-已登录
    """
    url = '/netCar/page/query/getNoticeList'



class GetNoticeListNotLoginApi(BaseApi):
    """
    获取通知列表-未登录
    """
    url = '/netCar/page/query/getNoticeList'
