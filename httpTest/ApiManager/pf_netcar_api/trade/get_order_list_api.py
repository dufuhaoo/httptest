# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi


class GetOrderListApi(LoginBaseApi):
    """
    我的行程列表
    """
    url = '/netCar/page/order/getOrderList'

    def build_custom_param(self, params):
        return {'pageNum': 1,'pageSize':10}

