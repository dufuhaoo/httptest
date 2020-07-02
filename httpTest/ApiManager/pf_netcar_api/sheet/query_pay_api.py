# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import SheetLoginBaseApi


class QueryPayApi(SheetLoginBaseApi):
    """
    支付明细查询接口
    """
    url = '/netCarAdminAuth/pay/gePay'

    def build_custom_param(self, data):
        return {'payBeginTime': data['payBeginTime'], # 开始时间
                'payEndTime': data['payEndTime'], # 结束时间
                'userId': data['userId'], # 用户ID
                'orderId': data['orderId'], # 订单号
                'payOrderId': data['payOrderId'], # 交易单号
                }