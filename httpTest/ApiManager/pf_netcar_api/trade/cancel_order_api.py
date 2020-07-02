# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi


class CancelOrderApi(LoginBaseApi):
    """
    取消下单接口
    """
    url = '/netCar/page/order/cancelOrder'

    def build_custom_param(self, data):
        return {
            "data": {
                "orderId": data['orderId']
            },
            "signStr": "string"
        }
