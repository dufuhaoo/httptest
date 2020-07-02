# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi


class GetOrderStatusRealTimeDataApi(LoginBaseApi):
    """
    获取订单实时状态
    """
    url = '/netCar/page/order/getOrderStatusRealTimeData'

    def build_custom_param(self, params):
        return {'orderId':params['orderId']}

