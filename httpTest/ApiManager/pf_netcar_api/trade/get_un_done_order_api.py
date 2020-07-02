# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi


class GetUnDoneOrderApi(LoginBaseApi):
    """
    查询未完成订单
    """
    url = '/netCar/page/order/queryUnDoneOrder'
