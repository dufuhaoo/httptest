# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi


class GetOrderDetailInfoApi(LoginBaseApi):
    """
    获取订单详情接口
    """
    url = '/netCar/page/order/getOrderDetailInfo'

    def build_custom_param(self, params):
        return {'orderId': params['orderId']}

